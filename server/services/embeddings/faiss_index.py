import faiss
import numpy as np

def build_faiss_index(embeddings):
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim) 

    vectors = embeddings.astype("float32")
    index.add(vectors)

    return index
