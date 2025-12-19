import requests
from urllib.parse import quote


def translate_text(text: str, source_lang="en", target_lang="pa") -> str:
    encoded_text = quote(text)

    url = (
        "https://translate.googleapis.com/translate_a/single"
        f"?client=gtx&sl={source_lang}&tl={target_lang}&dt=t&q={encoded_text}"
    )

    resp = requests.get(url, timeout=10)
    resp.raise_for_status()

    data = resp.json()

    translated = "".join(chunk[0] for chunk in data[0])
    return translated
