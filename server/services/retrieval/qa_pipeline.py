from server.services.retrieval.load_store import load_vector_store
from server.services.retrieval.embed_query import embed_query
from server.services.retrieval.search import search
from server.services.llm.answer import answer_question


def is_cross_policy_question(question: str) -> bool:
    q = question.lower()
    keywords = [
        "policies",
        "which policy",
        "available",
        "options",
        "for age",
        "50",
        "senior",
        "above",
    ]
    return any(k in q for k in keywords)

def ask(question: str):
    index, docs = load_vector_store()
    query_vec = embed_query(question)

    cross_policy = is_cross_policy_question(question)
    top_k = 15 if cross_policy else 5

    retrieved = search(index, docs, query_vec, top_k=top_k)
    contexts = [d["content"] for d in retrieved]

    answer = answer_question(question, contexts, cross_policy)
    return answer


if __name__ == "__main__":
    q = "Is 50yrs man heart surgery covered?"
    print(ask(q))
