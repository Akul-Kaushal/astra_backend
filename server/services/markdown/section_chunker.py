def chunk_section(section: dict, max_chars=800) -> list[str]:
    chunks = []
    buffer = ""

    for line in section["content"]:
        if len(buffer) + len(line) > max_chars:
            chunks.append(
                f"## {section['heading']}\n{buffer.strip()}"
            )
            buffer = ""

        buffer += line + "\n"

    if buffer.strip():
        chunks.append(
            f"## {section['heading']}\n{buffer.strip()}"
        )

    return chunks
