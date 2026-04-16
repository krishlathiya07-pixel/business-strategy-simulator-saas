from fastapi import APIRouter, Depends, HTTPException
from typing import Any, List
from sqlalchemy.orm import Session
from backend.app.api import deps
from backend.app.db.session import get_db
from backend.app.models.simulation import User
from backend.app.services.simulation_service import simulation_service
from backend.app.schemas.simulation import SimulationStep, SimulationState, SimulationReset

router = APIRouter()

@router.get("/state", response_model=SimulationState)
def get_state(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Get the current simulation state for the logged-in user.
    """
    return simulation_service.get_state(db, current_user.id)

@router.post("/step", response_model=SimulationState)
def take_step(
    step: SimulationStep,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Take a simulation step.
    """
    return simulation_service.step(db, current_user.id, step.action, step.amount)

@router.post("/reset", response_model=SimulationState)
def reset_simulation(
    reset: SimulationReset,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Reset the simulation.
    """
    return simulation_service.reset(db, current_user.id, reset.task, reset.seed, reset.difficulty)

@router.get("/history")
def get_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Get the simulation history for the current session.
    """
    return {"history": simulation_service.get_history(db, current_user.id)}

@router.get("/leaderboard")
def get_leaderboard(
    db: Session = Depends(get_db)
) -> Any:
    """
    Get the global leaderboard based on rewards.
    """
    # Simple leaderboard implementation: Top 10 history records by reward
    from backend.app.models.simulation import GameHistory, User, GameSession
    results = db.query(GameHistory, User.full_name).join(GameSession, GameHistory.session_id == GameSession.id).join(User, GameSession.user_id == User.id).order_by(GameHistory.reward.desc()).limit(10).all()
    
    leaderboard = []
    for h, name in results:
        leaderboard.append({
            "name": name,
            "reward": h.reward,
            "quarter": h.quarter,
            "profit": h.profit
        })
    return {"leaderboard": leaderboard}
