import re

def normalize_text(raw_text: str) -> list[str]:
    text = raw_text.replace("\u00a0", " ")
    text = re.sub(r"[ \t]+", " ", text)

    lines = []
    for line in text.splitlines():
        line = line.strip()
        if line:
            lines.append(line)

    return lines
