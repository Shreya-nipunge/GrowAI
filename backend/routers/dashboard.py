from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def dashboard_home():
    return {"message": "Dashboard endpoint working"}
