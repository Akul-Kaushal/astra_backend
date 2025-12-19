from fastapi import APIRouter
from pydantic import BaseModel
from server.services.retrieval.qa_pipeline import ask

router = APIRouter()


class QuestionRequest(BaseModel):
    question: str


class AnswerResponse(BaseModel):
    answer: str


@router.post("/ask", response_model=AnswerResponse)
def ask_question(req: QuestionRequest):
    answer = ask(req.question)
    return {"answer": answer}
