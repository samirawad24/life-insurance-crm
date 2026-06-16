from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..models import Lead, Call
from ..schemas import LeadCreate, LeadUpdate, LeadOut
from ..deps import get_current_user
from ..models import User
from ..scoring import calculate_score

router = APIRouter(prefix="/api/leads", tags=["leads"])


def rescore(lead: Lead, db: Session):
    calls = db.query(Call).filter(Call.lead_id == lead.id).all()
    answered = sum(1 for c in calls if c.outcome == "answered")
    lead.score = calculate_score(lead, len(calls), answered)
    db.commit()


@router.get("", response_model=List[LeadOut])
def list_leads(
    status: Optional[str] = None,
    source: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(Lead)
    if status:
        q = q.filter(Lead.status == status)
    if source:
        q = q.filter(Lead.source == source)
    if search:
        term = f"%{search}%"
        q = q.filter(
            Lead.first_name.ilike(term)
            | Lead.last_name.ilike(term)
            | Lead.email.ilike(term)
            | Lead.phone.ilike(term)
        )
    return q.order_by(Lead.score.desc(), Lead.created_at.desc()).all()


@router.post("", response_model=LeadOut)
def create_lead(data: LeadCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    lead = Lead(**data.model_dump(), assigned_to=current_user.id)
    db.add(lead)
    db.commit()
    db.refresh(lead)
    rescore(lead, db)
    db.refresh(lead)
    return lead


@router.get("/{lead_id}", response_model=LeadOut)
def get_lead(lead_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@router.put("/{lead_id}", response_model=LeadOut)
def update_lead(lead_id: int, data: LeadUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(lead, field, value)
    db.commit()
    db.refresh(lead)
    rescore(lead, db)
    db.refresh(lead)
    return lead


@router.delete("/{lead_id}")
def delete_lead(lead_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    db.delete(lead)
    db.commit()
    return {"ok": True}
