from server.services.retrieval.load_store import load_vector_store
from server.services.retrieval.embed_query import embed_query
from server.services.retrieval.search import search
from server.services.llm.answer import answer_question


def is_cross_policy_question(question: str) -> bool:
    q = question.lower()
    keywords = [
        # General coverage
        "covered",
        "coverage",
        "does it cover",
        "is it covered",
        "included",
        "include",
        "benefit",
        "benefits",

        # Surgery / treatment
        "surgery",
        "operation",
        "procedure",
        "treatment",
        "therapy",
        "hospitalization",
        "hospitalisation",
        "icu",
        "operation theatre",
        "implant",
        "device",

        # Disease / condition
        "heart",
        "cardiac",
        "cancer",
        "diabetes",
        "kidney",
        "dialysis",
        "stroke",
        "bypass",
        "angioplasty",
        "stent",
        "transplant",

        # Cost / money
        "cost",
        "price",
        "expense",
        "expenses",
        "charges",
        "bill",
        "amount",
        "limit",
        "sub limit",
        "maximum",
        "up to",
        "rs",
        "₹",

        # Eligibility / age
        "age",
        "years",
        "yrs",
        "eligible",
        "eligibility",
        "entry age",
        "renewal age",

        # Waiting / exclusions
        "waiting period",
        "waiting",
        "months",
        "days",
        "pre-existing",
        "ped",
        "excluded",
        "not covered",
        "exclusion",

        # Claim related
        "claim",
        "reimbursement",
        "cashless",
        "settlement"
    ]
    return any(k in q for k in keywords)

def ask(question: str, history: list[dict[str, str]] | None = None):
    index, docs = load_vector_store()
    query_vec = embed_query(question)

    cross_policy = is_cross_policy_question(question)
    top_k = 15 if cross_policy else 5

    retrieved = search(index, docs, query_vec, top_k=top_k)
    contexts = [d["content"] for d in retrieved]

    answer = answer_question(question, contexts, cross_policy, history)
    return answer


if __name__ == "__main__":
    q = "Is 50yrs man heart surgery covered?"
    print(ask(q))
