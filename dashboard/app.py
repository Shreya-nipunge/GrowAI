from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from datetime import datetime
import os
import requests
from dotenv import load_dotenv

# =======================
# CONFIG
# =======================
load_dotenv()
BACKEND_URL = os.getenv("BACKEND_URL", "")  # e.g. http://127.0.0.1:9000
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "")

app = FastAPI()
templates = Jinja2Templates(directory="dashboard/templates")
app.mount("/static", StaticFiles(directory="dashboard/static"), name="static")

# =======================
# HELPER FUNCTIONS
# =======================
def api_get(path: str):
    """Call backend GET if configured, else None."""
    if not BACKEND_URL:
        return None
    r = requests.get(f"{BACKEND_URL}{path}", headers={"X-Admin-Token": ADMIN_TOKEN})
    r.raise_for_status()
    return r.json()

def api_post(path: str, payload: dict):
    """Call backend POST if configured."""
    if not BACKEND_URL:
        return None
    r = requests.post(f"{BACKEND_URL}{path}", json=payload, headers={"X-Admin-Token": ADMIN_TOKEN})
    r.raise_for_status()
    return r.json()

# =======================
# FALLBACK IN-MEMORY DATA
# =======================
escalations = [
    {
        "id": 1,
        "user": "+91-98xxxxxxx",
        "query": "Will frost affect wheat next week?",
        "attachments": [],
        "confidence": "LOW",
        "status": "open",
        "notes": []
    },
    {
        "id": 2,
        "user": "+91-97xxxxxxx",
        "query": "What is tomato price in Pune today?",
        "attachments": [],
        "confidence": "HIGH",
        "status": "open",
        "notes": []
    }
]

# =======================
# ROUTES
# =======================
@app.get("/")
async def index(request: Request):
    data = api_get("/api/escalations") if BACKEND_URL else escalations
    return templates.TemplateResponse("index.html", {"request": request, "escalations": data})

@app.get("/escalation/{escalation_id}")
async def view_escalation(request: Request, escalation_id: int):
    item = None
    if BACKEND_URL:
        item = api_get(f"/api/escalations/{escalation_id}")
    else:
        item = next((e for e in escalations if e["id"] == escalation_id), None)
    return templates.TemplateResponse("escalation.html", {"request": request, "item": item})

@app.post("/escalation/{escalation_id}/respond")
async def respond(escalation_id: int, message: str = Form(...)):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if BACKEND_URL:
        api_post(f"/api/escalations/{escalation_id}/respond", {"message": message})
    else:
        item = next((e for e in escalations if e["id"] == escalation_id), None)
        if item:
            item["notes"].append({
                "by": "advisor",
                "msg": message,
                "timestamp": timestamp
            })

    return RedirectResponse(url=f"/escalation/{escalation_id}", status_code=303)

@app.post("/escalation/{escalation_id}/resolve")
async def resolve(escalation_id: int):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if BACKEND_URL:
        api_post(f"/api/escalations/{escalation_id}/resolve", {"note": "Resolved via dashboard"})
    else:
        item = next((e for e in escalations if e["id"] == escalation_id), None)
        if item:
            item["status"] = "resolved"
            item["notes"].append({
                "by": "system",
                "msg": "Escalation resolved.",
                "timestamp": timestamp
            })

    return RedirectResponse(url="/", status_code=303)