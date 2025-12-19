import faiss

def search(index, docs, query_vec, top_k=5):
    faiss.normalize_L2(query_vec)

    scores, indices = index.search(query_vec, top_k)

    results = []
    for idx in indices[0]:
        results.append(docs[idx])

    return results
