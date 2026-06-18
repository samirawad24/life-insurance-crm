import os
import urllib.request
import urllib.error
import json

RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
NOTIFY_EMAIL = os.getenv("NOTIFY_EMAIL", "samirawad24@gmail.com")


def send_lead_notification(lead):
    if not RESEND_API_KEY:
        print("[notifications] RESEND_API_KEY not set")
        return

    try:
        name = f"{lead.first_name} {lead.last_name}".strip()
        coverage_type = lead.coverage_type or "Unknown"

        lines = [
            f"Name:          {name}",
            f"Phone:         {lead.phone or 'N/A'}",
            f"Email:         {lead.email or 'N/A'}",
            f"Age:           {lead.age or 'N/A'}",
            f"Coverage Type: {coverage_type}",
        ]
        if lead.coverage_amount:
            lines.append(f"Coverage:      ${lead.coverage_amount:,.0f}")
        if lead.annual_income:
            lines.append(f"Income:        ${lead.annual_income:,.0f}/yr")
        if lead.health_status:
            lines.append(f"Health:        {lead.health_status}")
        if lead.score is not None:
            lines.append(f"Lead Score:    {lead.score}/100")
        if lead.notes:
            lines.append(f"Notes:         {lead.notes}")

        payload = json.dumps({
            "from": "Florida Life Insurance CRM <onboarding@resend.dev>",
            "to": [NOTIFY_EMAIL],
            "subject": f"New Lead: {name} — {coverage_type}",
            "text": "\n".join(lines)
        }).encode("utf-8")

        req = urllib.request.Request(
            "https://api.resend.com/emails",
            data=payload,
            headers={
                "Authorization": f"Bearer {RESEND_API_KEY}",
                "Content-Type": "application/json"
            }
        )
        with urllib.request.urlopen(req, timeout=10) as res:
            print(f"[notifications] Resend OK: {res.status}")

    except Exception as e:
        print(f"[notifications] Resend failed: {e}")
