from server.config import PROJECT_ROOT

def load_markdown_files():
    knowledge_dir = PROJECT_ROOT / "knowledge"

    print(PROJECT_ROOT)

    files = []
    for path in knowledge_dir.rglob("*.md"):
        files.append({
            "path": str(path),
            "content": path.read_text(encoding="utf-8")
        })

    return files


if __name__ == "__main__":
    files = load_markdown_files()
    print("Found markdown files:", len(files))
    for f in files:
        print(f["path"])
