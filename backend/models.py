from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="agent")
    created_at = Column(DateTime, default=datetime.utcnow)

    leads = relationship("Lead", back_populates="agent", foreign_keys="Lead.assigned_to")
    calls = relationship("Call", back_populates="user")


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, index=True)
    phone = Column(String)
    age = Column(Integer)
    annual_income = Column(Float)
    coverage_amount = Column(Float)
    health_status = Column(String)       # excellent, good, fair, poor
    status = Column(String, default="new")  # new, contacted, qualified, converted, lost
    score = Column(Integer, default=0)
    source = Column(String, default="manual")  # manual, facebook, referral, website
    notes = Column(Text)
    assigned_to = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    agent = relationship("User", back_populates="leads", foreign_keys=[assigned_to])
    calls = relationship("Call", back_populates="lead", cascade="all, delete-orphan")


class Call(Base):
    __tablename__ = "calls"

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    duration_seconds = Column(Integer, default=0)
    outcome = Column(String)   # answered, voicemail, no_answer, scheduled_callback
    notes = Column(Text)
    called_at = Column(DateTime, default=datetime.utcnow)

    lead = relationship("Lead", back_populates="calls")
    user = relationship("User", back_populates="calls")
