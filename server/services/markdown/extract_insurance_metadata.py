import re
def extract_insurance_metadata(raw_text: str) -> dict:
    text = raw_text.strip()

    text = re.sub(r"\s+", " ", text)

    provider_patterns = [
        r"HDFC ERGO",
        r"ICICI Lombard",
        r"Star Health",
        r"Bajaj Allianz",
        r"Reliance General Insurance"
        r"Star Health"
        r"LIC's"
    ]

    provider = "Unknown Provider"
    for p in provider_patterns:
        if re.search(p, text, re.IGNORECASE):
            provider = p
            break

    BLACKLIST = {
        "policy wording",
        "policy document",
        "cin",
        "uin",
        "irda",
        "terms and conditions",
    }
    policy_name = "Unknown Insurance Policy"
    lines = raw_text[:3000].splitlines()
    for line in lines:
        clean = line.strip()
        lower = clean.lower()
        if not clean or any(b in lower for b in BLACKLIST):
            continue
        match = re.search(
            r"\b(Policy|Plan|Insurance)\s+[A-Z][A-Za-z]*(?:\s+[A-Z][A-Za-z]*){0,6}\b",
            clean
        )
        if match:
            policy_name = match.group(0)
            break

    return {
        "doc_type": "insurance",
        "policy_name": policy_name,
        "provider": provider,
        "coverage_type": "health",
        "audience": "senior_citizen"
    }
