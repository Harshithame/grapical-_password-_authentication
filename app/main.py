from __future__ import annotations

import os
from datetime import datetime, timedelta
from pathlib import Path

from apscheduler.schedulers.background import BackgroundScheduler
from dateutil.tz import tzlocal
from fastapi import FastAPI

from .models import WorkflowStartRequest, WorkflowResponse
from .orchestrator import WorkflowOrchestrator
from .services.notification_service import NotificationService


DATA_DIR = Path(os.getenv("DATA_DIR", "/workspace/data"))
DATA_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Patient Scheduling Chatbot API")
orchestrator = WorkflowOrchestrator(DATA_DIR)
notifications = NotificationService()

scheduler = BackgroundScheduler(timezone=str(tzlocal()))


@app.on_event("startup")
def start_scheduler() -> None:
    if not scheduler.running:
        scheduler.start()


@app.on_event("shutdown")
def shutdown_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown(wait=False)


@app.post("/workflow/start", response_model=WorkflowResponse)
def start_workflow(req: WorkflowStartRequest) -> WorkflowResponse:
    resp = orchestrator.start(req.patient)
    if resp.status == "scheduled":
        # Schedule reminders at 3 days, 1 day, and 2 hours before the booked time
        # Parse chosen slot time from message for demo simplicity
        try:
            when_str = resp.message.split(" for ", 1)[1]
            start_dt = datetime.fromisoformat(when_str)
        except Exception:
            start_dt = datetime.now(tzlocal()) + timedelta(days=3)

        patient_name = req.patient.full_name
        contact_email = req.patient.email
        contact_phone = req.patient.phone

        def schedule(kind: int, delta: timedelta):
            run_time = start_dt - delta

            def job():
                msg = notifications.format_reminder(patient_name, start_dt, kind)
                if contact_email:
                    notifications.send_email(contact_email, "Appointment Reminder", msg)
                elif contact_phone:
                    notifications.send_sms(contact_phone, msg)

            scheduler.add_job(job, "date", run_date=run_time)

        schedule(1, timedelta(days=3))
        schedule(2, timedelta(days=1))
        schedule(3, timedelta(hours=2))
    return resp


@app.get("/")
def health() -> dict:
    return {"status": "ok"}

