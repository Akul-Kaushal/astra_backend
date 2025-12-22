import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

MODEL = "openai/gpt-oss-120b"


def answer_question(question: str, contexts: list[str], cross_policy: bool, history: list[dict[str, str]] | None = None) -> str:
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
        "content": (
            "<Intent> : If intent of the user is to 'ask about policy: move to condition if' or 'ask about general question: move to else' </Intent>\n\n"
            "<Condition : else> : If the user is asking about general question then answer strictly following the rules below.Write naturally, like a helpful human. Do not mention rules or sections.</Condition>\n\n"
            "<Rule : else> : In case of general question try to answer with very little info just related to the question"
            "<Rule : else (Strict)> : If the quesion is general then never bring any topic related to policy act as natural llm"
            "<Reference : else> : ['question' : 'Hello'] : ['answer' : 'Hello. How may I assist you today? ']"
            "<Condition : if> : If the user is asking about policy then answer strictly following the rules below.Write naturally, like a helpful human. Do not mention rules or sections. Always mention the Provider </Condition>\n\n"
            "<Rules : if> : If you cannot Find any info like unknown policy name, unknown provider, unknown coverage type, unknown audience and unknown scope then jsut leave it blank \n"
            "<Rules : if> : If you are able to find Policy name, provider, coverage type, audience and scope then answer strictly following the rules below.Write naturally, like a helpful human. Do not mention rules or sections. Always mention the Provider \n"
            "<Rule : if> : In case of policy related question try to answer as much detail as possible"
            "<Reference: if> : ['question' : 'What is the coverage limit for heart surgery?'] : ['answer' : ', <Will it be covered or not>, <Covered yes: then Mention Policy Name|Coverage|Cost|Limit|Amount|Premium | Covered No: then do not mention any info just tag it as unknown>' ]"
            "<Reference: if> : ['question' : 'Hello, Policy'] : ['answer' : 'Hello. I'm here to help you with your insurance policy [list all the policies you have : if unknown leave blank , else mention rest policies]. What would you like to know about your policy? Are you looking for information on hospitalization coverage, AYUSH treatment, or something else? Perhaps you'd like to know about the cost associated with certain treatments or the process for cashless facility in network hospitals?']"
            

        )
    }
]

    if history:
        for turn in history:
            messages.append({"role": "user", "content": turn["question"]})
            messages.append({"role": "assistant", "content": turn["answer"]})

    
    messages.append({
        "role": "user",
        "content": (
            "Context (Policy Content):\n"
            f"{context_text}\n\n"
            "Question:\n"
            f"{question}\n\n"
            "Answer strictly following the rules based on Condition: 'if | else' above. \n\n"
            "Do not mention rules or sections."
        )
    })


    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.3,
    )

    return response.choices[0].message.content.strip()
