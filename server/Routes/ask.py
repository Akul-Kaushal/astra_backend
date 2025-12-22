from collections import deque
from fastapi import APIRouter
from pydantic import BaseModel
from server.services.retrieval.qa_pipeline import ask
from server.services.utils.translator import translate_text

router = APIRouter()


class QuestionRequest(BaseModel):
    question: str
    language: str | None = "pa"
    history: list[dict[str, str]] | None = None


class AnswerResponse(BaseModel):
    answer: str


history = deque(maxlen=5)


@router.post("/ask", response_model=AnswerResponse)
def ask_question(req: QuestionRequest):
    if req.history == []:
        history.clear()
    
    answer = ask(req.question, list(history))

    history.append({
        "question": req.question,
        "answer": answer
    })

    print(history)
    answer = translate_text(answer, "en", req.language)
    return {"answer": answer}
