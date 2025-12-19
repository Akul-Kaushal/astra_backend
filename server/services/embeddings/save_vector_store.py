import faiss
import json
from pathlib import Path
from server.config import PROJECT_ROOT

def save_vector_store(index, docs):
    store_dir = PROJECT_ROOT / "vector_store"
    store_dir.mkdir(exist_ok=True)

    faiss.write_index(index, str(store_dir / "index.faiss"))

    with open(store_dir / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(docs, f, indent=2)
