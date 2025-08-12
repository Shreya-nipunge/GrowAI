from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from datetime import datetime

app = FastAPI()
templates = Jinja2Templates(directory="dashboard/templates")
app.mount("/static", StaticFiles(directory="dashboard/static"), name="static")

# In-memory fake data
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

@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "escalations": escalations})

@app.get("/escalation/{escalation_id}")
async def view_escalation(request: Request, escalation_id: int):
    item = next((e for e in escalations if e["id"] == escalation_id), None)
    return templates.TemplateResponse("escalation.html", {"request": request, "item": item})

@app.post("/escalation/{escalation_id}/respond")
async def respond(escalation_id: int, message: str = Form(...)):
    item = next((e for e in escalations if e["id"] == escalation_id), None)
    if item:
        item["notes"].append({
            "by": "advisor",
            "msg": message,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    return RedirectResponse(url=f"/escalation/{escalation_id}", status_code=303)

@app.post("/escalation/{escalation_id}/resolve")
async def resolve(escalation_id: int):
    item = next((e for e in escalations if e["id"] == escalation_id), None)
    if item:
        item["status"] = "resolved"
        item["notes"].append({
            "by": "system",
            "msg": "Escalation resolved.",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    return RedirectResponse(url="/", status_code=303)
