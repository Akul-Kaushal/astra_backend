from .markdown_section_parser import parse_markdown_sections
from .section_chunker import chunk_section

def chunk_markdown(markdown: str) -> list[str]:
    sections = parse_markdown_sections(markdown)
    all_chunks = []

    for section in sections:
        all_chunks.extend(chunk_section(section))

    return all_chunks


def attach_metadata(chunks, base_metadata):
    docs = []
    for i, chunk in enumerate(chunks):
        docs.append({
            "content": chunk,
            "metadata": {
                **base_metadata,
                "chunk_id": i
            }
        })
    return docs

