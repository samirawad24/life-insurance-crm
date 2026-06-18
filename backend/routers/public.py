from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from ..database import get_db
from ..models import Lead, User, BookedSlot
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
    appointment_date: Optional[str] = None
    appointment_time: Optional[str] = None




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

    if data.appointment_date and data.appointment_time:
        slot = BookedSlot(slot_date=data.appointment_date, slot_time=data.appointment_time)
        db.add(slot)
        db.commit()

    send_lead_notification(lead)

    return {"success": True}


@router.get("/slots")
def get_booked_slots(db: Session = Depends(get_db)):
    slots = db.query(BookedSlot).all()
    return [{"date": s.slot_date, "time": s.slot_time} for s in slots]


@router.get("/test-telegram")
def test_telegram():
    import os, urllib.request, urllib.parse, json as _json
    token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "")
    if not token or not chat_id:
        return {"ok": False, "error": "Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID env vars"}
    try:
        payload = _json.dumps({"chat_id": chat_id, "text": "Test from Life Insurance CRM"}).encode()
        req = urllib.request.Request(
            f"https://api.telegram.org/bot{token}/sendMessage",
            data=payload,
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=10) as res:
            body = _json.loads(res.read())
            return {"ok": True, "telegram_response": body}
    except Exception as e:
        return {"ok": False, "error": str(e)}
