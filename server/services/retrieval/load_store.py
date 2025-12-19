import json
import faiss
from pathlib import Path
from server.config import PROJECT_ROOT

def load_vector_store():
    store_dir = PROJECT_ROOT / "vector_store"

    index = faiss.read_index(str(store_dir / "index.faiss"))

    with open(store_dir / "metadata.json", "r", encoding="utf-8") as f:
        docs = json.load(f)

    return index, docs
