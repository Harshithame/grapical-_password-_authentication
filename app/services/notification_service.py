from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional


@dataclass
class NotificationResult:
    success: bool
    channel: str
    message_id: str


class NotificationService:
    def __init__(self) -> None:
        pass

    def send_email(self, to_email: str, subject: str, body: str) -> NotificationResult:
        message_id = f"email-{int(datetime.utcnow().timestamp())}"
        print(f"[EMAIL] to={to_email} subject={subject}\n{body}")
        return NotificationResult(success=True, channel="email", message_id=message_id)

    def send_sms(self, to_phone: str, body: str) -> NotificationResult:
        message_id = f"sms-{int(datetime.utcnow().timestamp())}"
        print(f"[SMS] to={to_phone} {body}")
        return NotificationResult(success=True, channel="sms", message_id=message_id)

    def format_confirmation(self, patient_name: str, doctor: str, start: datetime, location: str) -> str:
        return (
            f"Hello {patient_name}, your appointment with Dr. {doctor} is confirmed on "
            f"{start.strftime('%a, %b %d %Y at %I:%M %p')} at {location}."
        )

    def format_reminder(self, patient_name: str, start: datetime, kind: int) -> str:
        if kind == 1:
            return f"Reminder: Your appointment is in 3 days on {start.strftime('%a at %I:%M %p')}"
        if kind == 2:
            return f"Reminder: Please complete intake forms. Confirm attendance for {start.strftime('%a %I:%M %p')}"
        return f"Final reminder: Your appointment is in ~2 hours ({start.strftime('%I:%M %p')}). Reply if you need to cancel."
