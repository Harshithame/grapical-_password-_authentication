## Patient Scheduling Chatbot API (Demo)

- Automates: greeting → CSV lookup → Excel scheduling → insurance capture → confirmation → intake forms → reminders
- Event-driven; fully backend handled after a single POST

### Run

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Start workflow (sample)

```bash
curl -X POST http://localhost:8000/workflow/start \
  -H 'Content-Type: application/json' \
  -d '{
    "patient": {
      "full_name": "Jane Doe",
      "date_of_birth": "1990-05-10",
      "doctor_preference": "Smith",
      "location": "Main Clinic",
      "email": "jane@example.com",
      "insurance": {"carrier": "DemoCare", "member_id": "M123", "group_number": "G01"}
    }
  }'
```

Artifacts are created under `data/`. Reminders are scheduled with APScheduler and logged to console.
