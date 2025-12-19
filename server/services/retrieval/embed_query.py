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

def embed_query(query: str):
    response = client.embeddings.create(
        model=EMBED_MODEL,
        input=query
    )

    vec = np.array(response.data[0].embedding, dtype="float32")
    vec = vec.reshape(1, -1)
    return vec
