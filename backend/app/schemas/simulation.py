from typing import List, Optional
from pydantic import BaseModel

class Competitor(BaseModel):
    name: str
    emoji: str
    strategy: str
    market_share: float
    description: str

class SimulationState(BaseModel):
    revenue: float
    costs: float
    profit: float
    market_share: float
    employees: int
    customer_satisfaction: float
    product_quality: float
    quarter: int
    max_quarters: int
    task: str
    industry: str
    difficulty: str = "medium"
    done: bool
    market_rank: int
    message: str
    competitors: List[Competitor]
    news: Optional[str] = None
    reward: Optional[float] = None
    chart_revenue: Optional[List[float]] = []
    chart_profit: Optional[List[float]] = []
    chart_share: Optional[List[float]] = []
    news_feed: Optional[List[dict]] = []

class SimulationStep(BaseModel):
    action: str
    amount: float = 5000.0

class SimulationReset(BaseModel):
    task: str = "grow_market_share"
    seed: Optional[int] = 42
    difficulty: str = "medium"
