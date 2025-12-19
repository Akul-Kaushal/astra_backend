from server.services.markdown.load_markdown import load_markdown_files
from server.services.markdown.chunk_markdown import chunk_markdown
from server.services.markdown.chunk_markdown import attach_metadata

def build_chunks():
    all_docs = []

    markdown_files = load_markdown_files()

    for md in markdown_files:
        markdown_text = md["content"]
        source_path = md["path"]

        base_metadata = {
            "doc_type": "insurance",
            "source": source_path
        }

        chunks = chunk_markdown(markdown_text)
        docs = attach_metadata(chunks, base_metadata)

        all_docs.extend(docs)

    return all_docs


if __name__ == "__main__":
    docs = build_chunks()
    print("Total chunks:", len(docs))
    print("\n--- SAMPLE CHUNK ---\n")
    print(docs)