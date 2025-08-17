from fastapi import FastAPI
from routers.whatsapp import router as whatsapp_router
from routers.ai import router as ai_router
from routers.dashboard import router as dashboard_router

app = FastAPI()

# Register routes
app.include_router(whatsapp_router, prefix="/whatsapp")
app.include_router(ai_router, prefix="/ai")
app.include_router(dashboard_router, prefix="/dashboard")

@app.get("/")
async def root():
    return {"message": "Backend is running 🚀"}
