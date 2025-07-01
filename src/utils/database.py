from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional
import os

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, nullable=False)
    api_key = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime, default=func.now())


class Request(Base):
    __tablename__ = "requests"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    model_used = Column(String(100), nullable=False)
    prompt = Column(Text, nullable=False)
    response = Column(Text)
    tokens_used = Column(Integer)
    cost = Column(Float)
    created_at = Column(DateTime, default=func.now())
    
    user = relationship("User", back_populates="requests")


class UsageAlert(Base):
    __tablename__ = "usage_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    alert_type = Column(String(50), nullable=False)
    message = Column(Text, nullable=False)
    severity = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=func.now())
    
    user = relationship("User", back_populates="alerts")


# Add relationships
User.requests = relationship("Request", back_populates="user")
User.alerts = relationship("UsageAlert", back_populates="user")


class DatabaseManager:
    def __init__(self, database_url: Optional[str] = None):
        self.database_url = database_url or os.getenv("DATABASE_URL", "sqlite:///./hapivet.db")
        self.engine = create_engine(self.database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def create_tables(self):
        """Create all database tables"""
        Base.metadata.create_all(bind=self.engine)
    
    def get_session(self):
        """Get a database session"""
        return self.SessionLocal()
    
    def close_session(self, session):
        """Close a database session"""
        session.close()


# Global database manager instance
db_manager = DatabaseManager() 