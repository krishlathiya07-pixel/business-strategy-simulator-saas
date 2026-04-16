from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.app.db.base_class import Base

class User(Base):
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean(), default=True)
    is_superuser = Column(Boolean(), default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    sessions = relationship("GameSession", back_populates="owner", cascade="all, delete-orphan")

class GameSession(Base):
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    task = Column(String, nullable=False)
    industry = Column(String, nullable=False)
    current_quarter = Column(Integer, default=0)
    max_quarters = Column(Integer, nullable=False)
    is_done = Column(Boolean, default=False)
    state_data = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    owner = relationship("User", back_populates="sessions")
    history = relationship("GameHistory", back_populates="session", cascade="all, delete-orphan")

class GameHistory(Base):
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("gamesession.id"), nullable=False)
    quarter = Column(Integer, nullable=False)
    action = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    profit = Column(Float, nullable=False)
    market_share = Column(Float, nullable=False)
    market_rank = Column(Integer, nullable=False)
    reward = Column(Float, nullable=False)
    event_name = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    session = relationship("GameSession", back_populates="history")
