import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

MODEL = "llama-3.3-70b-versatile"


def answer_question(question: str, contexts: list[str]) -> str:
    context_text = "\n\n".join(contexts)

    messages = [
  {
    "role": "system",
    "content": (
      "You are an elderly-focused insurance assistant. "
      "Your job is to explain insurance information to senior citizens in very simple, clear language. "
      "Avoid legal jargon, technical terms, and assumptions. "
      "Always be calm, respectful, and factual."
    )
  },
  {
    "role": "system",
    "content": (
      "STRICT RULES:\n"
      "1. Use ONLY the provided context when answering insurance or policy-related questions.\n"
      "2. Do NOT add outside knowledge, assumptions, or general advice for policies.\n"
      "3. Always explicitly mention:\n"
      "   - Provider Name\n"
      "   - Cost / Premium (if mentioned in context)\n"
      "4. If cost is NOT mentioned in the context, clearly say: 'Cost is not mentioned in the policy document.'\n"
      "5. If the question is NOT related to insurance or policies, respond using the tag:\n"
      "   \n"
      "   and give a simple, high-level explanation (no policy references).\n"
      "   and answer strictly from the context.\n"
      "7. Never mix policy-based answers with general knowledge.\n"
      "8. If the context does not contain the answer, clearly state:\n"
      "   'This information is not available in the provided policy document.'"
      "9. If provider not found which is rarely the case in the rag as it in mentioned in rag then do not give answer like not explicitly mentioned as many of the rag contains the provider name\n"
      "   'This information is not available in the provided policy document.'"
    )
  },
  {
    "role": "user",
    "content": (
      "Context (Policy Content):\n"
      "Policy Name: Mention The provider Name Along with the text"
      f'{contexts}'
      "Question:\n"
      f'{question}'
    )
  }
]


    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.2,
    )

    return response.choices[0].message.content.strip()
