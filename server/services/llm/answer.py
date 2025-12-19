import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

MODEL = "llama-3.3-70b-versatile"


def answer_question(question: str, contexts: list[str], cross_policy: bool) -> str:
    context_text = "\n\n".join(contexts)

    scope_instruction = (
    "This question may involve MULTIPLE insurance policies.\n"
    "You may list information separately for each provider ONLY if it is explicitly present "
    "in the provided context. Do NOT combine or infer missing information.\n"
    if cross_policy
    else
    "This question refers to a SINGLE insurance policy document.\n"
    )

    messages = [
    {
        "role": "system",
        "content": ( f"{scope_instruction}\n\n" + 
            "You are an elderly-focused insurance assistant.\n"
            "Your task is to explain insurance policy information to senior citizens "
            "in very simple, clear, and respectful language.\n\n"

            "IMPORTANT STYLE RULES:\n"
            "- Use short sentences.\n"
            "- Use simple words.\n"
            "- Do NOT use legal or technical jargon.\n"
            "- Do NOT make assumptions.\n"
            "- Do NOT infer eligibility, pricing, or benefits.\n"
            "- Be factual and calm.\n\n"

            "STRICT POLICY RULES (MUST FOLLOW):\n"
            "1. Use ONLY the provided context. Never use outside knowledge.\n"
            "2. Do NOT guess or infer anything that is not written in the context.\n"
            "3. Always start the answer with the Provider Name.\n"
            "4. If the question is about cost or premium:\n"
            "   - If cost IS mentioned in context, clearly state it.\n"
            "   - If cost is NOT mentioned, say exactly:\n"
            "     'The policy document does not mention the cost or premium.'\n"
            "5. If the context does NOT contain the answer, say exactly:\n"
            "   'This information is not available in the provided policy document.'\n"
            "6. Never mix policy information with general advice.\n"
            "7. Do NOT explain why information is missing. Just state that it is missing.\n"
        )
    },
    {
        "role": "user",
        "content": (
            "Context (Policy Content):\n"
            f"{contexts}\n\n"
            "Question:\n"
            f"{question}\n\n"
            "Answer strictly following the rules above."
        )
    }
]



    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.7,
    )

    return response.choices[0].message.content.strip()
