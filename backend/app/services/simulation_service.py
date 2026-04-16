from typing import List, Dict, Any, Optional
import uuid
from sqlalchemy.orm import Session
from backend.app.models.simulation import GameSession, GameHistory, User
from server.environment import BusinessStrategyEnv

class SimulationService:
    def _get_env_for_session(self, session: GameSession) -> BusinessStrategyEnv:
        env = BusinessStrategyEnv(
            task=session.task,
            seed=42, # In a real app, we might store the seed in the session
            difficulty=session.state_data.get("difficulty", "medium")
        )
        env.load_state(session.state_data)
        # Load history into env
        env.history = [
            {
                "quarter": h.quarter,
                "action": h.action,
                "amount": h.amount,
                "profit": h.profit,
                "market_share": h.market_share,
                "market_rank": h.market_rank,
                "reward": h.reward,
                "event": h.event_name
            } for h in session.history
        ]
        return env

    def get_state(self, db: Session, user_id: int) -> Dict[str, Any]:
        session = db.query(GameSession).filter(
            GameSession.user_id == user_id,
            GameSession.is_done == False
        ).order_by(GameSession.updated_at.desc()).first()
        
        if not session:
            # Auto-reset if no active session
            return self.reset(db, user_id, "grow_market_share", 42, "medium")
        
        return self._with_charts(session)

    def step(self, db: Session, user_id: int, action: str, amount: float) -> Dict[str, Any]:
        session = db.query(GameSession).filter(
            GameSession.user_id == user_id,
            GameSession.is_done == False
        ).order_by(GameSession.updated_at.desc()).first()
        
        if not session:
            raise Exception("No active simulation session found")
            
        env = self._get_env_for_session(session)
        state = env.step(action, amount)
        
        # Save history
        history_entry = GameHistory(
            session_id=session.id,
            quarter=state["quarter"],
            action=action,
            amount=amount,
            profit=state["profit"],
            market_share=state["market_share"],
            market_rank=state["market_rank"],
            reward=state.get("reward", 0),
            event_name=state.get("current_event", {}).get("name") if state.get("current_event") else None
        )
        db.add(history_entry)
        
        # Update session
        session.current_quarter = state["quarter"]
        session.is_done = state["done"]
        session.state_data = state
        db.commit()
        db.refresh(session)
        
        return self._with_charts(session)

    def reset(self, db: Session, user_id: int, task: str, seed: Optional[int], difficulty: str = "medium") -> Dict[str, Any]:
        # Mark old sessions as done
        db.query(GameSession).filter(
            GameSession.user_id == user_id,
            GameSession.is_done == False
        ).update({"is_done": True})
        
        env = BusinessStrategyEnv(task=task, seed=seed or 42, difficulty=difficulty)
        state = env.reset()
        
        session = GameSession(
            session_id=str(uuid.uuid4()),
            user_id=user_id,
            task=task,
            industry=state["industry"],
            current_quarter=0,
            max_quarters=state["max_quarters"],
            state_data=state
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        
        return self._with_charts(session)

    def get_history(self, db: Session, user_id: int) -> List[Dict[str, Any]]:
        session = db.query(GameSession).filter(
            GameSession.user_id == user_id
        ).order_by(GameSession.updated_at.desc()).first()
        
        if not session:
            return []
            
        return [
            {
                "quarter": h.quarter,
                "action": h.action,
                "amount": h.amount,
                "profit": h.profit,
                "market_share": h.market_share,
                "market_rank": h.market_rank,
                "event": h.event_name
            } for h in session.history
        ]

    def _with_charts(self, session: GameSession) -> Dict[str, Any]:
        history = sorted(session.history, key=lambda x: x.quarter)
        
        # Initial point
        rev_hist = [session.state_data.get("revenue", 0)] if not history else []
        prof_hist = [session.state_data.get("profit", 0)] if not history else []
        share_hist = [session.state_data.get("market_share", 0) * 100] if not history else []
        
        for h in history:
            rev_hist.append(h.profit + (session.state_data.get("costs", 0))) # Simplified for chart
            prof_hist.append(h.profit)
            share_hist.append(h.market_share * 100)
            
        # Reconstruct news feed from history
        news_feed = []
        for h in reversed(history):
            if h.event_name:
                news_feed.append({"q": h.quarter, "text": f"Event: {h.event_name}"})
        
        return {
            **session.state_data,
            "chart_revenue": rev_hist,
            "chart_profit": prof_hist,
            "chart_share": share_hist,
            "news_feed": news_feed[:20]
        }

simulation_service = SimulationService()
