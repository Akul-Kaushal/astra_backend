from server.services.chunking.build_chunks import build_chunks
from server.services.embeddings.embed_chunks import embed_chunks
from server.services.embeddings.faiss_index import build_faiss_index
from server.services.embeddings.save_vector_store import save_vector_store

def build_index():
    docs = build_chunks()
    embeddings = embed_chunks(docs)
    index = build_faiss_index(embeddings)
    save_vector_store(index, docs)

    print("Embeddings built:", embeddings.shape)
    print("Chunks indexed:", len(docs))

    print(docs)


if __name__ == "__main__":
    build_index()
