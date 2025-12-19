import re

def parse_markdown_sections(markdown: str) -> list[dict]:
    sections = []
    current = None

    for line in markdown.splitlines():
        if line.startswith("## "):
            if current:
                sections.append(current)

            current = {
                "heading": line.replace("## ", "").strip(),
                "content": []
            }
        elif current:
            current["content"].append(line)

    if current:
        sections.append(current)

    return sections
