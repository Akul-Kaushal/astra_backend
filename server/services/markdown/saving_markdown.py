from pathlib import Path

def save_markdown(markdown: str, filename: str, doc_type: str):
    base = Path("knowledge") / doc_type
    base.mkdir(parents=True, exist_ok=True)

    path = base / filename
    path.write_text(markdown, encoding="utf-8")

    return str(path)
