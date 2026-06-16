from datetime import datetime, timezone
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import Lead


def calculate_score(lead: "Lead", call_count: int = 0, answered_calls: int = 0) -> int:
    score = 0

    # Age (0-20 pts) — prime buying window is 35-55
    if lead.age:
        if 35 <= lead.age <= 55:
            score += 20
        elif 25 <= lead.age < 35 or 55 < lead.age <= 65:
            score += 12
        elif lead.age > 65:
            score += 5
        else:
            score += 8

    # Income (0-25 pts)
    if lead.annual_income:
        if lead.annual_income >= 100_000:
            score += 25
        elif lead.annual_income >= 75_000:
            score += 20
        elif lead.annual_income >= 50_000:
            score += 14
        elif lead.annual_income >= 30_000:
            score += 8
        else:
            score += 3

    # Coverage interest (0-20 pts)
    if lead.coverage_amount:
        if lead.coverage_amount >= 500_000:
            score += 20
        elif lead.coverage_amount >= 250_000:
            score += 15
        elif lead.coverage_amount >= 100_000:
            score += 10
        else:
            score += 5

    # Health status (0-15 pts)
    health_map = {"excellent": 15, "good": 12, "fair": 6, "poor": 2}
    if lead.health_status:
        score += health_map.get(lead.health_status.lower(), 0)

    # Engagement (0-10 pts) — call answer rate
    if call_count > 0:
        score += int((answered_calls / call_count) * 10)

    # Recency (0-10 pts)
    if lead.created_at:
        created = lead.created_at
        if created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)
        days_old = (datetime.now(timezone.utc) - created).days
        if days_old <= 1:
            score += 10
        elif days_old <= 7:
            score += 7
        elif days_old <= 30:
            score += 4
        else:
            score += 1

    return min(score, 100)
