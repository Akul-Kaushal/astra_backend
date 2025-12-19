from server.services.retrieval.load_store import load_vector_store
from server.services.retrieval.embed_query import embed_query
from server.services.retrieval.search import search
from server.services.llm.answer import answer_question

def ask(question: str):
    index, docs = load_vector_store()
    query_vec = embed_query(question)

    retrieved = search(index, docs, query_vec, top_k=5)
    contexts = [d["content"] for d in retrieved]

    answer = answer_question(question, contexts)
    return answer


if __name__ == "__main__":
    q = "Is air ambulance covered in this policy?"
    print(ask(q))
