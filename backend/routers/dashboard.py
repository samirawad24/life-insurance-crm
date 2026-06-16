from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timezone, date
from ..database import get_db
from ..models import Lead, Call
from ..schemas import DashboardStats
from ..deps import get_current_user
from ..models import User

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=DashboardStats)
def get_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    total = db.query(Lead).count()
    new = db.query(Lead).filter(Lead.status == "new").count()
    contacted = db.query(Lead).filter(Lead.status == "contacted").count()
    qualified = db.query(Lead).filter(Lead.status == "qualified").count()
    converted = db.query(Lead).filter(Lead.status == "converted").count()
    lost = db.query(Lead).filter(Lead.status == "lost").count()

    today_start = datetime.combine(date.today(), datetime.min.time())
    calls_today = db.query(Call).filter(Call.called_at >= today_start).count()

    conversion_rate = round(converted / total * 100, 1) if total > 0 else 0.0

    hot_leads = db.query(Lead).order_by(Lead.score.desc()).limit(5).all()
    recent_calls = db.query(Call).order_by(Call.called_at.desc()).limit(10).all()

    return DashboardStats(
        total_leads=total,
        new_leads=new,
        contacted_leads=contacted,
        qualified_leads=qualified,
        converted_leads=converted,
        lost_leads=lost,
        calls_today=calls_today,
        conversion_rate=conversion_rate,
        hot_leads=hot_leads,
        recent_calls=recent_calls,
    )
