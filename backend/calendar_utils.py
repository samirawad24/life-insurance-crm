import os
import json
import base64
from datetime import datetime, timedelta

CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID", "primary")
CREDENTIALS_B64 = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON_B64", "")

TIME_SLOTS = {
    "9:30 AM":  {"hour": 9,  "minute": 30},
    "11:00 AM": {"hour": 11, "minute": 0},
    "1:30 PM":  {"hour": 13, "minute": 30},
    "3:00 PM":  {"hour": 15, "minute": 0},
    "4:30 PM":  {"hour": 16, "minute": 30},
}


def create_appointment_event(lead, appointment_date: str, appointment_time: str, meeting_type: str):
    if not CREDENTIALS_B64:
        print("[calendar] GOOGLE_SERVICE_ACCOUNT_JSON_B64 not set — skipping")
        return

    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build

        creds_json = json.loads(base64.b64decode(CREDENTIALS_B64).decode("utf-8"))
        creds = service_account.Credentials.from_service_account_info(
            creds_json,
            scopes=["https://www.googleapis.com/auth/calendar"]
        )
        service = build("calendar", "v3", credentials=creds, cache_discovery=False)

        slot = TIME_SLOTS.get(appointment_time)
        if not slot:
            print(f"[calendar] Unknown time slot: {appointment_time}")
            return

        # appointment_date is like "Mon, Jun 23" — parse it with current year
        year = datetime.now().year
        dt_str = f"{appointment_date} {year}"
        start_dt = datetime.strptime(dt_str, "%a, %b %d %Y").replace(
            hour=slot["hour"], minute=slot["minute"]
        )
        end_dt = start_dt + timedelta(minutes=30)

        name = f"{lead.first_name} {lead.last_name}".strip()
        meeting_label = "Phone Call" if meeting_type == "phone" else "Zoom Meeting"

        event = {
            "summary": f"{meeting_label} — {name}",
            "description": (
                f"Lead from Florida Life Insurance website\n"
                f"Phone: {lead.phone or 'N/A'}\n"
                f"Email: {lead.email or 'N/A'}\n"
                f"Age: {lead.age or 'N/A'}\n"
                f"Notes: {lead.notes or 'N/A'}\n"
                f"Score: {lead.score}/100"
            ),
            "start": {"dateTime": start_dt.isoformat(), "timeZone": "America/New_York"},
            "end":   {"dateTime": end_dt.isoformat(),   "timeZone": "America/New_York"},
            "reminders": {
                "useDefault": False,
                "overrides": [
                    {"method": "popup", "minutes": 60},
                    {"method": "popup", "minutes": 10},
                ]
            }
        }

        result = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
        print(f"[calendar] Event created: {result.get('htmlLink')}")

    except Exception as e:
        print(f"[calendar] Failed to create event: {e}")
