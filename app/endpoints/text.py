
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.llm_service import generate_response

router = APIRouter()


class QuestionRequest(BaseModel):
    question: str


@router.post("/text")
async def get_text(request: QuestionRequest):
    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty.",
        )

    try:
        result = await generate_response(question)

        return {
            "question": question,
            "answer": result["answer"],
            "sources": result["sources"],
        }

    except Exception as exc:
        print(f"AI generation error: {type(exc).__name__}: {exc}")
        raise HTTPException(
            status_code=500,
            detail="Unable to generate a response. Please try again.",
        )
