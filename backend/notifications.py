import os
import urllib.request
import urllib.parse
import json

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")


def send_lead_notification(lead):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("[notifications] Telegram credentials not set")
        return

    try:
        name = f"{lead.first_name} {lead.last_name}".strip()
        coverage_type = lead.coverage_type or "Unknown"

        lines = [
            f"New Lead: {name}",
            f"Phone: {lead.phone or 'N/A'}",
            f"Email: {lead.email or 'N/A'}",
            f"Age: {lead.age or 'N/A'}",
            f"Type: {coverage_type}",
        ]
        if lead.coverage_amount:
            lines.append(f"Coverage: ${lead.coverage_amount:,.0f}")
        if lead.health_status:
            lines.append(f"Health: {lead.health_status}")
        if lead.score is not None:
            lines.append(f"Score: {lead.score}/100")
        if lead.notes:
            lines.append(f"Notes: {lead.notes}")

        text = "\n".join(lines)

        payload = json.dumps({
            "chat_id": TELEGRAM_CHAT_ID,
            "text": text
        }).encode("utf-8")

        req = urllib.request.Request(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            data=payload,
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=10) as res:
            print(f"[notifications] Telegram OK: {res.status}")

    except Exception as e:
        print(f"[notifications] Telegram failed: {e}")
