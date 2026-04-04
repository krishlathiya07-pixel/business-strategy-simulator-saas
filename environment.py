"""
Business Strategy Simulation Environment
Level 2 Upgrade: Competitor Companies
Two AI competitors take actions each quarter — agent must beat them.
"""

import random
from typing import Any, Dict, List, Optional


# ─── Market Events ────────────────────────────────────────────────────────────

MARKET_EVENTS = [
    {"name": "Economic Recession", "emoji": "📉", "description": "A recession hits. Revenue drops sharply.", "revenue_mult": 0.70, "costs_mult": 1.0, "market_share_delta": -0.02, "satisfaction_delta": -0.05, "prob": 0.05, "severity": "critical"},
    {"name": "Industry Boom", "emoji": "🚀", "description": "Industry-wide boom! Revenue surges.", "revenue_mult": 1.25, "costs_mult": 1.0, "market_share_delta": 0.02, "satisfaction_delta": 0.05, "prob": 0.05, "severity": "positive"},
    {"name": "Competitor Price War", "emoji": "⚔️", "description": "A competitor slashes prices. Market share under threat.", "revenue_mult": 0.88, "costs_mult": 1.0, "market_share_delta": -0.03, "satisfaction_delta": 0.0, "prob": 0.08, "severity": "negative"},
    {"name": "Viral Marketing Moment", "emoji": "🌟", "description": "Your brand goes viral! Massive market share boost.", "revenue_mult": 1.15, "costs_mult": 1.0, "market_share_delta": 0.06, "satisfaction_delta": 0.08, "prob": 0.05, "severity": "positive"},
    {"name": "Supply Chain Crisis", "emoji": "🚢", "description": "Global supply chain disruptions spike costs.", "revenue_mult": 1.0, "costs_mult": 1.30, "market_share_delta": 0.0, "satisfaction_delta": -0.04, "prob": 0.06, "severity": "negative"},
    {"name": "Tech Disruption", "emoji": "💻", "description": "New technology disrupts your industry.", "revenue_mult": 0.92, "costs_mult": 1.10, "market_share_delta": -0.02, "satisfaction_delta": -0.03, "prob": 0.06, "severity": "negative"},
    {"name": "Talent Shortage", "emoji": "👥", "description": "Industry-wide talent shortage. Hiring costs surge.", "revenue_mult": 1.0, "costs_mult": 1.15, "market_share_delta": 0.0, "satisfaction_delta": -0.02, "prob": 0.07, "severity": "negative"},
    {"name": "Government Subsidy", "emoji": "🏛️", "description": "Government announces industry subsidies!", "revenue_mult": 1.0, "costs_mult": 0.85, "market_share_delta": 0.0, "satisfaction_delta": 0.02, "prob": 0.04, "severity": "positive"},
    {"name": "Consumer Confidence Surge", "emoji": "😊", "description": "Consumer confidence hits record highs.", "revenue_mult": 1.12, "costs_mult": 1.0, "market_share_delta": 0.01, "satisfaction_delta": 0.04, "prob": 0.05, "severity": "positive"},
    {"name": "Regulatory Crackdown", "emoji": "⚖️", "description": "New regulations increase compliance costs.", "revenue_mult": 1.0, "costs_mult": 1.12, "market_share_delta": 0.0, "satisfaction_delta": -0.02, "prob": 0.05, "severity": "negative"},
]

# ─── Competitor Definitions ───────────────────────────────────────────────────

COMPETITORS = [
    {
        "name": "RivalCorp",
        "emoji": "🔴",
        "strategy": "aggressive",
        "market_share": 0.25,
        "strength": "marketing",
        "description": "Aggressive growth-focused competitor. Heavy on marketing and expansion.",
    },
    {
        "name": "MegaCo",
        "emoji": "🔵",
        "strategy": "defensive",
        "market_share": 0.40,
        "strength": "cost",
        "description": "Dominant market leader. Focuses on cost efficiency and retention.",
    },
]

# Competitor strategy action weights
COMPETITOR_STRATEGIES = {
    "aggressive": ["expand_market", "increase_marketing", "launch_product", "hire_employees", "lower_prices"],
    "defensive":  ["cut_costs", "decrease_marketing", "raise_prices", "invest_in_rd", "cut_costs"],
}


class Competitor:
    """Simulates a competing company that acts every quarter."""

    def __init__(self, config: Dict, seed: int = 0):
        self.name = config["name"]
        self.emoji = config["emoji"]
        self.strategy = config["strategy"]
        self.market_share = config["market_share"]
        self.strength = config["strength"]
        self.description = config["description"]
        self.rng = random.Random(seed)
        self.history: List[Dict] = []

    def take_action(self, quarter: int, market_event: Optional[Dict]) -> Dict:
        """Competitor takes a strategic action each quarter."""
        actions = COMPETITOR_STRATEGIES[self.strategy]

        # React to market events
        if market_event:
            if market_event["severity"] == "critical":
                action = "cut_costs"  # defensive in crisis
            elif market_event["severity"] == "positive":
                action = "expand_market"  # opportunistic in boom
            else:
                action = self.rng.choice(actions)
        else:
            action = self.rng.choice(actions)

        # Apply simplified effect on market share
        delta = 0.0
        if action in ["expand_market", "increase_marketing", "launch_product"]:
            delta = self.rng.uniform(0.005, 0.02)
        elif action in ["cut_costs", "decrease_marketing"]:
            delta = -self.rng.uniform(0.002, 0.01)
        elif action == "lower_prices":
            delta = self.rng.uniform(0.01, 0.025)

        # Apply noise
        delta += self.rng.uniform(-0.005, 0.005)
        self.market_share = round(max(min(self.market_share + delta, 0.80), 0.05), 4)

        record = {
            "quarter": quarter,
            "action": action,
            "market_share": self.market_share,
            "delta": round(delta, 4),
        }
        self.history.append(record)
        return record

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "emoji": self.emoji,
            "strategy": self.strategy,
            "market_share": self.market_share,
            "description": self.description,
        }


class BusinessStrategyEnv:
    """
    Simulates a company competing against 2 AI competitors.
    Features random market events and dynamic competitor behavior.
    """

    ACTIONS = [
        "increase_marketing", "decrease_marketing",
        "hire_employees", "layoff_employees",
        "cut_costs", "invest_in_rd",
        "launch_product", "expand_market",
        "raise_prices", "lower_prices",
    ]

    def __init__(self, task: str = "survive", seed: int = 42):
        self.task = task
        self.seed = seed
        self.rng = random.Random(seed)
        self.state_data: Dict[str, Any] = {}
        self.current_quarter = 0
        self.max_quarters = self._get_max_quarters()
        self.done = False
        self.history = []
        self.events_history: List[Dict] = []
        self.competitors: List[Competitor] = []
        self.reset()

    def _get_max_quarters(self) -> int:
        return {"survive": 4, "grow_market_share": 8, "scale_profitably": 12}.get(self.task, 4)

    def reset(self) -> Dict[str, Any]:
        self.rng = random.Random(self.seed)
        self.current_quarter = 0
        self.done = False
        self.history = []
        self.events_history = []

        # Init competitors with deterministic seeds
        self.competitors = [
            Competitor(COMPETITORS[0], seed=self.seed + 1),
            Competitor(COMPETITORS[1], seed=self.seed + 2),
        ]

        total_competitor_share = sum(c.market_share for c in self.competitors)
        agent_share = round(max(1.0 - total_competitor_share - 0.30, 0.05), 4)  # ~0.10 left for agent

        self.state_data = {
            "revenue": 50000.0,
            "costs": 35000.0,
            "profit": 15000.0,
            "market_share": agent_share,
            "employees": 20,
            "customer_satisfaction": 0.70,
            "marketing_budget": 5000.0,
            "rd_investment": 2000.0,
            "product_quality": 0.65,
            "quarter": 0,
            "max_quarters": self.max_quarters,
            "task": self.task,
            "done": False,
            "current_event": None,
            "competitors": [c.to_dict() for c in self.competitors],
            "market_rank": self._get_rank(),
            "message": "Company initialized. You face 2 competitors. Make your first move!",
        }
        return self.state_data.copy()

    def state(self) -> Dict[str, Any]:
        return self.state_data.copy()

    def _get_rank(self) -> int:
        """Get agent's market rank vs competitors (1 = leading)."""
        shares = [self.state_data.get("market_share", 0.10)] + [c.market_share for c in self.competitors]
        shares_sorted = sorted(shares, reverse=True)
        return shares_sorted.index(self.state_data.get("market_share", 0.10)) + 1

    def step(self, action: str, amount: float = 5000.0) -> Dict[str, Any]:
        if self.done:
            return {**self.state_data, "message": "Episode is over. Call reset() to start again."}
        if action not in self.ACTIONS:
            return {**self.state_data, "message": f"Invalid action '{action}'. Valid: {self.ACTIONS}"}

        # Apply agent action
        self._apply_action(action, amount)

        # Roll market event
        event = self._roll_market_event()
        if event:
            self._apply_event(event)
            self.state_data["current_event"] = {
                "name": event["name"], "emoji": event["emoji"],
                "description": event["description"], "severity": event["severity"],
            }
            self.events_history.append({"quarter": self.current_quarter + 1, **event})
        else:
            self.state_data["current_event"] = None

        # Competitors take their actions
        competitor_actions = []
        for comp in self.competitors:
            action_record = comp.take_action(self.current_quarter + 1, event)
            competitor_actions.append({
                "name": comp.name,
                "emoji": comp.emoji,
                "action": action_record["action"],
                "market_share": comp.market_share,
            })

        # Market share competition — competitors steal from agent
        self._apply_competition()

        # Simulate quarter
        self._simulate_quarter(event)

        # Update state with competitor info
        self.state_data["competitors"] = [c.to_dict() for c in self.competitors]
        self.state_data["competitor_actions"] = competitor_actions
        self.state_data["market_rank"] = self._get_rank()

        # Advance quarter
        self.current_quarter += 1
        self.state_data["quarter"] = self.current_quarter

        # Reward, done
        reward = self._compute_reward()
        self.done = self._check_done()
        self.state_data["done"] = self.done
        self.state_data["reward"] = reward

        self.history.append({
            "quarter": self.current_quarter,
            "action": action,
            "amount": amount,
            "reward": reward,
            "profit": self.state_data["profit"],
            "market_share": self.state_data["market_share"],
            "market_rank": self.state_data["market_rank"],
            "event": event["name"] if event else None,
        })

        return self.state_data.copy()

    def _apply_competition(self):
        """Competitors steal market share from agent based on their actions."""
        s = self.state_data
        total_competitor_share = sum(c.market_share for c in self.competitors)
        # Remaining share is split between agent and "uncontested market"
        available = max(1.0 - total_competitor_share, 0.05)
        # Agent keeps proportion of available share based on satisfaction + quality
        agent_strength = (s["customer_satisfaction"] + s["product_quality"]) / 2
        s["market_share"] = round(max(min(available * agent_strength, 0.60), 0.01), 4)

    def _roll_market_event(self) -> Optional[Dict]:
        roll = self.rng.random()
        cumulative = 0.0
        for event in MARKET_EVENTS:
            cumulative += event["prob"]
            if roll < cumulative:
                return event
        return None

    def _apply_event(self, event: Dict):
        s = self.state_data
        s["revenue"] *= event["revenue_mult"]
        s["costs"] *= event["costs_mult"]
        s["market_share"] = round(max(min(s["market_share"] + event["market_share_delta"], 1.0), 0.01), 4)
        s["customer_satisfaction"] = round(max(min(s["customer_satisfaction"] + event["satisfaction_delta"], 1.0), 0.0), 3)

    def _apply_action(self, action: str, amount: float):
        s = self.state_data
        if action == "increase_marketing":
            spend = min(amount, s["revenue"] * 0.2)
            s["marketing_budget"] += spend; s["costs"] += spend
            s["market_share"] = min(s["market_share"] + 0.02, 1.0)
            s["customer_satisfaction"] = min(s["customer_satisfaction"] + 0.03, 1.0)
        elif action == "decrease_marketing":
            r = min(amount, s["marketing_budget"])
            s["marketing_budget"] -= r; s["costs"] -= r
            s["market_share"] = max(s["market_share"] - 0.01, 0.01)
        elif action == "hire_employees":
            n = max(1, int(amount / 3000))
            s["employees"] += n; s["costs"] += n * 3000
            s["revenue"] *= (1 + n * 0.02)
            s["customer_satisfaction"] = min(s["customer_satisfaction"] + 0.02, 1.0)
        elif action == "layoff_employees":
            l = min(max(1, int(amount / 3000)), s["employees"] - 5)
            s["employees"] -= l; s["costs"] -= l * 3000
            s["customer_satisfaction"] = max(s["customer_satisfaction"] - 0.05, 0.0)
        elif action == "cut_costs":
            c = min(amount, s["costs"] * 0.15)
            s["costs"] -= c
            s["product_quality"] = max(s["product_quality"] - 0.03, 0.1)
        elif action == "invest_in_rd":
            i = min(amount, s["revenue"] * 0.2)
            s["rd_investment"] += i; s["costs"] += i
            s["product_quality"] = min(s["product_quality"] + 0.05, 1.0)
        elif action == "launch_product":
            s["costs"] += amount * 0.5
            s["revenue"] += amount * 0.8 * s["product_quality"]
            s["market_share"] = min(s["market_share"] + 0.03, 1.0)
        elif action == "expand_market":
            s["costs"] += amount
            s["market_share"] = min(s["market_share"] + 0.04, 1.0)
            s["revenue"] += amount * 1.2
        elif action == "raise_prices":
            s["revenue"] *= 1.08
            s["customer_satisfaction"] = max(s["customer_satisfaction"] - 0.04, 0.0)
            s["market_share"] = max(s["market_share"] - 0.01, 0.01)
        elif action == "lower_prices":
            s["revenue"] *= 0.94
            s["customer_satisfaction"] = min(s["customer_satisfaction"] + 0.04, 1.0)
            s["market_share"] = min(s["market_share"] + 0.02, 1.0)

    def _simulate_quarter(self, event: Optional[Dict] = None):
        s = self.state_data
        noise = self.rng.uniform(-0.05, 0.05)
        s["revenue"] = s["revenue"] * (1 + 0.02 + noise + s["market_share"] * 0.05)
        s["costs"] = s["costs"] * (1 + 0.01 + self.rng.uniform(0, 0.02))
        s["profit"] = round(s["revenue"] - s["costs"], 2)
        s["revenue"] = round(s["revenue"], 2)
        s["costs"] = round(s["costs"], 2)
        s["market_share"] = round(min(max(s["market_share"], 0.01), 1.0), 4)
        s["customer_satisfaction"] = round(min(max(s["customer_satisfaction"], 0.0), 1.0), 3)
        s["product_quality"] = round(min(max(s["product_quality"], 0.1), 1.0), 3)

        q = self.current_quarter + 1
        rank = self._get_rank()
        rank_str = ["🥇", "🥈", "🥉"][min(rank - 1, 2)]
        base = f"Q{q}: Profit=${s['profit']:,.0f} | Market={s['market_share']*100:.1f}% | Rank {rank_str}"
        if event:
            s["message"] = f"{event['emoji']} {event['name']}! {base}"
        elif s["profit"] < 0:
            s["message"] = f"⚠️ {base} — Losing money!"
        else:
            s["message"] = f"✅ {base}"

    def _compute_reward(self) -> float:
        s = self.state_data
        rank_bonus = max(0, (3 - self._get_rank()) * 0.1)  # bonus for beating competitors
        if self.task == "survive":
            return round(min((1.0 if s["profit"] > 0 else 0.0) + rank_bonus, 1.0), 3)
        elif self.task == "grow_market_share":
            return round(min(s["market_share"] / 0.20 + rank_bonus, 1.0), 3)
        elif self.task == "scale_profitably":
            rev = min(s["revenue"] / 100000.0, 1.0)
            sat = s["customer_satisfaction"] if s["customer_satisfaction"] >= 0.8 else s["customer_satisfaction"] * 0.5
            return round(min((rev + sat) / 2 + rank_bonus, 1.0), 3)
        return 0.0

    def _check_done(self) -> bool:
        s = self.state_data
        if self.current_quarter >= self.max_quarters:
            return True
        if s["profit"] < -50000:
            s["message"] = "💀 Bankruptcy! Company collapsed."
            return True
        if s["employees"] < 5:
            s["message"] = "💀 Too few employees. Company shut down."
            return True
        return False