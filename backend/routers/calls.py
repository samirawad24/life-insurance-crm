from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Call, Lead
from ..schemas import CallCreate, CallOut
from ..deps import get_current_user
from ..models import User
from ..scoring import calculate_score

router = APIRouter(prefix="/api/calls", tags=["calls"])


@router.post("", response_model=CallOut)
def log_call(data: CallCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    lead = db.query(Lead).filter(Lead.id == data.lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    call = Call(**data.model_dump(), user_id=current_user.id)
    db.add(call)
    db.commit()
    db.refresh(call)

    # Recalculate score and auto-advance status from new → contacted
    all_calls = db.query(Call).filter(Call.lead_id == lead.id).all()
    answered = sum(1 for c in all_calls if c.outcome == "answered")
    lead.score = calculate_score(lead, len(all_calls), answered)
    if lead.status == "new":
        lead.status = "contacted"
    db.commit()

    return call


@router.get("/lead/{lead_id}", response_model=List[CallOut])
def get_lead_calls(lead_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Call).filter(Call.lead_id == lead_id).order_by(Call.called_at.desc()).all()


@router.get("", response_model=List[CallOut])
def list_calls(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Call).order_by(Call.called_at.desc()).limit(50).all()
