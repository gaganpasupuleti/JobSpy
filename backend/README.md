# JobSpy Alerts Lab — Backend

FastAPI backend for the standalone jobs + email alerts lab.

## Run locally

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8002
```

API docs: http://localhost:8002/docs

Email mode is **console only** — generated emails are stored in SQLite and printed to the server log.
