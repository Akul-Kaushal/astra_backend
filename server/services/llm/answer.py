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
                "You are an assistant helping senior citizens understand insurance policies. "
                "Explain clearly, simply, and avoid legal jargon."
            )
        },
        {
            "role": "user",
            "content": f"""
Use ONLY the information below to answer and mention the policy name be specific.

Context:
{context_text}

Question:
{question}
"""
        }
    ]

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.2,
    )

    return response.choices[0].message.content.strip()
