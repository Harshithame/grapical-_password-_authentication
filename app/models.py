from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field, EmailStr


class InsuranceInfo(BaseModel):
    carrier: str = Field(..., description="Insurance carrier name")
    member_id: str = Field(..., description="Member ID")
    group_number: Optional[str] = Field(None, description="Group number")


class PatientInput(BaseModel):
    full_name: str
    date_of_birth: date
    doctor_preference: Optional[str] = None
    location: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    insurance: Optional[InsuranceInfo] = None


class Appointment(BaseModel):
    appointment_id: str
    patient_id: str
    doctor: str
    location: str
    start_datetime: datetime
    duration_minutes: int


class WorkflowStartRequest(BaseModel):
    patient: PatientInput


class WorkflowResponse(BaseModel):
    workflow_id: str
    status: str
    message: str


class EventLog(BaseModel):
    timestamp: datetime
    event: str
    workflow_id: str
    details: dict
