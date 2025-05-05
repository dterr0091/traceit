from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Define relationship with CreditBalance
    credit_balance = relationship("CreditBalance", back_populates="user", uselist=False)
    search_history = relationship("SearchHistory", back_populates="user")

class CreditBalance(Base):
    __tablename__ = "credit_balances"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    balance = Column(Integer, default=20)  # Default credits for new users
    tier = Column(String, default="free")  # free, premium, enterprise
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Define relationship with User
    user = relationship("User", back_populates="credit_balance")
    
class CreditTransaction(Base):
    __tablename__ = "credit_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    amount = Column(Integer)  # Can be positive (added) or negative (used)
    transaction_type = Column(String)  # purchase, usage, bonus, etc.
    search_id = Column(Integer, ForeignKey("search_history.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class SearchHistory(Base):
    __tablename__ = "search_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    query_hash = Column(String, index=True)  # SHA-256 hash of the query
    query_type = Column(String)  # light, heavy, video
    credits_used = Column(Integer)
    perplexity_used = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Define relationship with User
    user = relationship("User", back_populates="search_history")
    transactions = relationship("CreditTransaction", backref="search_history") 