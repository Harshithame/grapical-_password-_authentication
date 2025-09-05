from __future__ import annotations

import csv
import hashlib
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Optional, Dict


@dataclass
class PatientRecord:
    patient_id: str
    full_name: str
    date_of_birth: date
    email: str | None
    phone: str | None


class CsvPatientRepository:
    def __init__(self, csv_path: Path) -> None:
        self.csv_path = csv_path
        if not self.csv_path.exists():
            self._initialize_file()

    def _initialize_file(self) -> None:
        self.csv_path.parent.mkdir(parents=True, exist_ok=True)
        with self.csv_path.open("w", newline="") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "patient_id",
                    "full_name",
                    "date_of_birth",
                    "email",
                    "phone",
                ],
            )
            writer.writeheader()

    def _load_all(self) -> Dict[str, PatientRecord]:
        records: Dict[str, PatientRecord] = {}
        if not self.csv_path.exists():
            return records
        with self.csv_path.open("r", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    rec = PatientRecord(
                        patient_id=row["patient_id"],
                        full_name=row["full_name"],
                        date_of_birth=date.fromisoformat(row["date_of_birth"]),
                        email=row.get("email") or None,
                        phone=row.get("phone") or None,
                    )
                    records[rec.patient_id] = rec
                except Exception:
                    continue
        return records

    def _persist_all(self, records: Dict[str, PatientRecord]) -> None:
        with self.csv_path.open("w", newline="") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "patient_id",
                    "full_name",
                    "date_of_birth",
                    "email",
                    "phone",
                ],
            )
            writer.writeheader()
            for rec in records.values():
                writer.writerow(
                    {
                        "patient_id": rec.patient_id,
                        "full_name": rec.full_name,
                        "date_of_birth": rec.date_of_birth.isoformat(),
                        "email": rec.email or "",
                        "phone": rec.phone or "",
                    }
                )

    @staticmethod
    def _normalize_key(full_name: str, date_of_birth: date) -> str:
        normalized = f"{full_name.strip().lower()}|{date_of_birth.isoformat()}"
        return hashlib.sha1(normalized.encode()).hexdigest()[:12]

    def find_by_name_and_dob(self, full_name: str, date_of_birth: date) -> Optional[PatientRecord]:
        key = self._normalize_key(full_name, date_of_birth)
        records = self._load_all()
        return records.get(key)

    def get_or_create(self, full_name: str, date_of_birth: date, email: str | None, phone: str | None) -> PatientRecord:
        key = self._normalize_key(full_name, date_of_birth)
        records = self._load_all()
        if key in records:
            return records[key]
        rec = PatientRecord(
            patient_id=key,
            full_name=full_name,
            date_of_birth=date_of_birth,
            email=email,
            phone=phone,
        )
        records[key] = rec
        self._persist_all(records)
        return rec
