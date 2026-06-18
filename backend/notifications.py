import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

GMAIL_USER = os.getenv("GMAIL_USER", "")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "")
NOTIFY_EMAIL = os.getenv("NOTIFY_EMAIL", GMAIL_USER)


def send_lead_notification(lead):
    if not GMAIL_USER or not GMAIL_APP_PASSWORD:
        return

    try:
        name = f"{lead.first_name} {lead.last_name}".strip()
        coverage_type = lead.coverage_type or "Unknown"
        subject = f"New Lead: {name} — {coverage_type}"

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

        body = "\n".join(lines)

        msg = MIMEMultipart()
        msg["From"] = GMAIL_USER
        msg["To"] = NOTIFY_EMAIL
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            server.send_message(msg)
    except Exception as e:
        print(f"[notifications] email failed: {e}")
