import os
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


client = OpenAI(
    api_key=os.getenv("OPEN_ROUTER_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

EMBED_MODEL = "sentence-transformers/all-MiniLM-L12-v2"


def embed_chunks(docs):
    texts = [doc["content"] for doc in docs]

    response = client.embeddings.create(
        model=EMBED_MODEL,
        input=texts
    )

    embeddings = np.array(
        [item.embedding for item in response.data],
        dtype="float32"
    )

    return embeddings
