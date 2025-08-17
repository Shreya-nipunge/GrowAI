from fastapi import FastAPI
from backend.routers.whatsapp import router as whatsapp_router
from backend.routers.ai import router as ai_router
from backend.routers.dashboard import router as dashboard_router


app = FastAPI()



# Register routes
app.include_router(whatsapp_router, prefix="/whatsapp")
app.include_router(ai_router, prefix="/ai")
app.include_router(dashboard_router, prefix="/dashboard")

@app.get("/")
async def root():
    return {"message": "Backend is running 🚀"} 

if __name__ == '__main__':
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
