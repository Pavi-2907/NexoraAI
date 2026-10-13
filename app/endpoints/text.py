from fastapi import APIRouter

router = APIRouter()

@router.get("/text")
async def get_text(value: str):
    print(f"Received value: {value}")
    return {"message": "Hello World"}
    