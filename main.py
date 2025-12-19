import os
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

groq_api_key = os.environ.get("GROQ_API_KEY")


def main():
    llm = ChatOpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=groq_api_key,
        model="llama-3.3-70b-versatile",
        temperature=0.7,
    )

    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello, how are you?"},
    ]

    response = llm.invoke(messages)
    # print(dir(response))
    print(response.content)

if __name__ == "__main__":
    main()
