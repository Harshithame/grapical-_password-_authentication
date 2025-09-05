from __future__ import annotations

import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict

from dateutil.tz import tzlocal

from .models import PatientInput, WorkflowResponse
from .services.patient_repo import CsvPatientRepository
from .services.calendar_service import ExcelCalendarService
from .services.notification_service import NotificationService
from .services.event_bus import global_event_bus


class WorkflowOrchestrator:
    def __init__(
        self,
        data_dir: Path,
    ) -> None:
        self.data_dir = data_dir
        self.patients = CsvPatientRepository(self.data_dir / "patients.csv")
        self.calendar = ExcelCalendarService(self.data_dir / "calendar.xlsx")
        self.notifications = NotificationService()

    def start(self, patient: PatientInput) -> WorkflowResponse:
        workflow_id = str(uuid.uuid4())
        global_event_bus.publish(
            "workflow_started",
            {"workflow_id": workflow_id, "patient": patient.model_dump()},
        )

        # 1) Patient lookup/create
        existing = self.patients.find_by_name_and_dob(patient.full_name, patient.date_of_birth)
        patient_rec = existing or self.patients.get_or_create(
            full_name=patient.full_name,
            date_of_birth=patient.date_of_birth,
            email=patient.email,
            phone=patient.phone,
        )
        is_new_patient = existing is None
        # 60 minutes for new; 30 minutes for existing
        slot_minutes = 60 if is_new_patient else 30

        # 2) Smart scheduling window: next 14 days during 9-17
        now = datetime.now(tzlocal()).replace(minute=0, second=0, microsecond=0)
        window_start = now + timedelta(days=1, hours=9 - now.hour)
        window_end = now + timedelta(days=14)
        slots = self.calendar.find_available_slots(
            preferred_doctor=patient.doctor_preference,
            preferred_location=patient.location or "Main Clinic",
            duration_minutes=slot_minutes,
            window_start=window_start,
            window_end=window_end,
            max_results=5,
        )
        if not slots:
            return WorkflowResponse(
                workflow_id=workflow_id,
                status="no_slots",
                message="No available time slots",
            )

        chosen_slot = slots[0]
        appointment_id = str(uuid.uuid4())[:8]
        doctor = patient.doctor_preference or "On-Call"
        location = patient.location or "Main Clinic"
        self.calendar.book_slot(
            appointment_id=appointment_id,
            patient_id=patient_rec.patient_id,
            doctor=doctor,
            location=location,
            start=chosen_slot,
            duration_minutes=slot_minutes,
        )

        # 3) Insurance capture (static demo: ensure structure present)
        if not patient.insurance:
            # For demo, synthesize dummy insurance
            from .models import InsuranceInfo

            patient.insurance = InsuranceInfo(carrier="DemoCare", member_id="D12345", group_number="G-001")

        # 4) Confirmation message
        if patient.email:
            body = self.notifications.format_confirmation(
                patient_name=patient.full_name,
                doctor=doctor,
                start=chosen_slot,
                location=location,
            )
            self.notifications.send_email(
                to_email=patient.email,
                subject="Appointment Confirmation",
                body=body,
            )
        elif patient.phone:
            body = self.notifications.format_confirmation(
                patient_name=patient.full_name,
                doctor=doctor,
                start=chosen_slot,
                location=location,
            )
            self.notifications.send_sms(to_phone=patient.phone, body=body)

        global_event_bus.publish(
            "appointment_confirmed",
            {
                "workflow_id": workflow_id,
                "appointment_id": appointment_id,
                "patient_id": patient_rec.patient_id,
                "start": chosen_slot.isoformat(),
                "duration_minutes": slot_minutes,
                "doctor": doctor,
                "location": location,
            },
        )

        # 5) Intake forms (demo: email link)
        if patient.email:
            self.notifications.send_email(
                to_email=patient.email,
                subject="Patient Intake Forms",
                body="Please complete your intake forms here: https://example.com/forms/intake",
            )

        # 6) Reminders (log events only; scheduling handled by API scheduler)
        global_event_bus.publish(
            "reminders_scheduled",
            {"workflow_id": workflow_id, "appointment_id": appointment_id, "start": chosen_slot.isoformat()},
        )

        return WorkflowResponse(
            workflow_id=workflow_id,
            status="scheduled",
            message=f"Appointment booked for {chosen_slot.isoformat()}",
        )
