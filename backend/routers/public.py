from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from ..database import get_db
from ..models import Lead, User
from ..scoring import calculate_score
from ..notifications import send_lead_notification

router = APIRouter(prefix="/api/public", tags=["public"])


class PublicLead(BaseModel):
    first_name: str
    last_name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    age: Optional[int] = None
    coverage_type: Optional[str] = None
    annual_income: Optional[float] = None
    coverage_amount: Optional[float] = None
    health_status: Optional[str] = None
    message: Optional[str] = None



@router.post("/lead")
def submit_lead(data: PublicLead, db: Session = Depends(get_db)):
    agent = db.query(User).first()

    notes_parts = []
    if data.coverage_type:
        notes_parts.append(f"Interested in: {data.coverage_type}")
    if data.health_status:
        notes_parts.append(f"Health Status: {data.health_status}")
    if data.message:
        notes_parts.append(f"Message: {data.message}")

    lead = Lead(
        first_name=data.first_name,
        last_name=data.last_name,
        phone=data.phone,
        email=data.email,
        age=data.age,
        annual_income=data.annual_income,
        coverage_amount=data.coverage_amount,
        health_status=data.health_status,
        notes=" | ".join(notes_parts) or None,
        source="website",
        status="new",
        assigned_to=agent.id if agent else None,
    )
    db.add(lead)
    db.commit()
    db.refresh(lead)

    lead.score = calculate_score(lead, 0, 0)
    db.commit()
    db.refresh(lead)

    send_lead_notification(lead)

    return {"success": True}
