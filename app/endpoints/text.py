from fastapi import APIRouter

router = APIRouter()

@router.get("/text")
async def get_text(value: str):
    return {"message": "Hello World"}
    