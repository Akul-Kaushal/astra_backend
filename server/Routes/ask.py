from fastapi import APIRouter
from pydantic import BaseModel
from server.services.retrieval.qa_pipeline import ask
from server.services.utils.translator import translate_text

router = APIRouter()


class QuestionRequest(BaseModel):
    question: str
    language: str | None = "pa"


class AnswerResponse(BaseModel):
    answer: str


@router.post("/ask", response_model=AnswerResponse)
def ask_question(req: QuestionRequest):
    answer = ask(req.question)
    # answer = translate_text(answer, "en", req.language)
    return {"answer": answer}
