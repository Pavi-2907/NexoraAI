from fastapi import APIRouter
from endpoints.text import router as text_router

api_router = APIRouter()

api_router.include_router(text_router)

