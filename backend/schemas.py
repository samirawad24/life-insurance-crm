from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime


class UserCreate(BaseModel):
    email: str
    name: str
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    name: str
    role: str
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserOut


class LeadCreate(BaseModel):
    first_name: str
    last_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    age: Optional[int] = None
    annual_income: Optional[float] = None
    coverage_amount: Optional[float] = None
    health_status: Optional[str] = None
    status: str = "new"
    source: str = "manual"
    notes: Optional[str] = None


class LeadUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    age: Optional[int] = None
    annual_income: Optional[float] = None
    coverage_amount: Optional[float] = None
    health_status: Optional[str] = None
    status: Optional[str] = None
    source: Optional[str] = None
    notes: Optional[str] = None


class CallOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    lead_id: int
    user_id: int
    duration_seconds: int
    outcome: Optional[str]
    notes: Optional[str]
    called_at: datetime


class LeadOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    first_name: str
    last_name: str
    email: Optional[str]
    phone: Optional[str]
    age: Optional[int]
    annual_income: Optional[float]
    coverage_amount: Optional[float]
    health_status: Optional[str]
    status: str
    score: int
    source: str
    notes: Optional[str]
    assigned_to: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]
    calls: List[CallOut] = []


class CallCreate(BaseModel):
    lead_id: int
    duration_seconds: int = 0
    outcome: str
    notes: Optional[str] = None


class DashboardStats(BaseModel):
    total_leads: int
    new_leads: int
    contacted_leads: int
    qualified_leads: int
    converted_leads: int
    lost_leads: int
    calls_today: int
    conversion_rate: float
    hot_leads: List[LeadOut]
    recent_calls: List[CallOut]
