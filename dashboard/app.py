from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from datetime import datetime, timedelta
import os
import requests
from dotenv import load_dotenv
import time

# =======================
# CONFIG
# =======================
load_dotenv()
BACKEND_URL = os.getenv("BACKEND_URL", "")
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "")

app = FastAPI()
templates = Jinja2Templates(directory="dashboard/templates")
app.mount("/static", StaticFiles(directory="dashboard/static"), name="static")

# =======================
# HELPER FUNCTIONS
# =======================
SIMULATE_API_FAILURE = os.getenv("SIMULATE_API_FAILURE", "false").lower() == "true"

def api_get(path: str):
    """Call backend GET if configured, else return local fallback."""
    time.sleep(1)  # simulate network delay
    if SIMULATE_API_FAILURE:
        raise requests.RequestException("Simulated backend failure for testing")
    if not BACKEND_URL:
        return None
    r = requests.get(f"{BACKEND_URL}{path}", headers={"X-Admin-Token": ADMIN_TOKEN})
    r.raise_for_status()
    return r.json()

def api_post(path: str, payload: dict):
    """Call backend POST if configured."""
    time.sleep(1)  # simulate network delay
    if SIMULATE_API_FAILURE:
        raise requests.RequestException("Simulated backend failure for testing")
    if not BACKEND_URL:
        return None
    r = requests.post(f"{BACKEND_URL}{path}", json=payload, headers={"X-Admin-Token": ADMIN_TOKEN})
    r.raise_for_status()
    return r.json()


# =======================
# FALLBACK IN-MEMORY DATA
# =======================
now = datetime.now()

escalations = [
    {
        "id": 1,
        "user": "+91-98xxxxxxx",
        "query": "Will frost affect wheat next week?",
        "attachments": [],
        "confidence": "LOW",
        "status": "open",
        "notes": [
            {"by": "user", "msg": "Hi, I’m worried about frost.",
             "timestamp": (now - timedelta(hours=5)).strftime("%Y-%m-%d %H:%M:%S")},
            {"by": "advisor", "msg": "We’ll check the forecast.",
             "timestamp": (now - timedelta(hours=4)).strftime("%Y-%m-%d %H:%M:%S")}
        ]
    },
    {
        "id": 2,
        "user": "+91-97xxxxxxx",
        "query": "What is tomato price in Pune today?",
        "attachments": [],
        "confidence": "HIGH",
        "status": "open",
        "notes": [
            {"by": "user", "msg": "Need market rate ASAP.",
             "timestamp": (now - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S")}
        ]
    },
]

# Add extra sample data
for i in range(3, 21):
    escalations.append({
        "id": i,
        "user": f"+91-9{i%10}xxxxxxx",
        "query": f"Sample query number {i}?",
        "attachments": [],
        "confidence": "MEDIUM" if i % 2 == 0 else "LOW",
        "status": "open" if i % 3 != 0 else "resolved",
        "notes": [
            {"by": "system", "msg": "Escalation created.",
             "timestamp": (now - timedelta(days=i)).strftime("%Y-%m-%d %H:%M:%S")}
        ]
    })

# =======================
# ROUTES
# =======================
@app.get("/")
async def index(request: Request):
    try:
        data = api_get("/api/escalations") if BACKEND_URL else escalations
    except requests.RequestException:
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "message": "Unable to reach backend. Please try again later."},
            status_code=500
        )
    return templates.TemplateResponse("index.html", {"request": request, "escalations": data})

@app.get("/escalation/{escalation_id}")
async def view_escalation(request: Request, escalation_id: int):
    try:
        if BACKEND_URL:
            item = api_get(f"/api/escalations/{escalation_id}")
        else:
            item = next((e for e in escalations if e["id"] == escalation_id), None)
    except requests.RequestException:
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "message": "Unable to reach backend. Please try again later."},
            status_code=500
        )

    if not item:
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "message": "Escalation not found."},
            status_code=404
        )

    return templates.TemplateResponse("escalation.html", {"request": request, "item": item})

@app.post("/escalation/{escalation_id}/respond")
async def respond(request: Request, escalation_id: int, message: str = Form(...)):
    message = message.strip()
    if not message:
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "message": "Reply cannot be empty."},
            status_code=400
        )

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
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
    except requests.RequestException:
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "message": "Unable to reach backend. Please try again later."},
            status_code=500
        )

    return RedirectResponse(url=f"/escalation/{escalation_id}", status_code=303)

@app.post("/escalation/{escalation_id}/resolve")
async def resolve(escalation_id: int):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
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
    except requests.RequestException:
        return templates.TemplateResponse(
            "error.html",
            {"request": {}, "message": "Unable to reach backend. Please try again later."},
            status_code=500
        )

    return RedirectResponse(url="/", status_code=303)
