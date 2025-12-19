SECTION_MAP = {
    "What Is Covered": [
        "we will cover",
        "benefits",
        "coverage",
        "inpatient",
        "hospitalisation"
    ],
    "What Is NOT Covered": [
        "we will not cover",
        "exclusions",
        "excluded"
    ],
    "Waiting Periods": [
        "waiting period",
        "pre-existing",
        "30 days",
        "months"
    ],
    "Special Benefits": [
        "air ambulance",
        "maternity",
        "critical illness"
    ]
}

def detect_section(line: str) -> str | None:
    l = line.lower()
    for section, keywords in SECTION_MAP.items():
        if any(k in l for k in keywords):
            return section
    return None
