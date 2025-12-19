def to_bullets(lines: list[str], max_items=100) -> str:
    bullets = []
    for line in lines:
        clean = line.strip()
        if len(clean) >= 10:
            bullets.append(f"- {clean}")
        if len(bullets) >= max_items:
            break
    return "\n".join(bullets)

def render_sections(content: dict) -> str:
    order = [
        "Hospitalization Coverage",
        "Cardiac Coverage",
        "Critical Illness Coverage",
        "Chronic Disease Coverage",
        "Out Patient Coverage",
        "Modern Treatments",
        "AYUSH Treatment",
        "Home Care / Domiciliary Treatment",
        "Special Benefits",
        "Wellness Benefits",
        "Optional Covers",
        "Waiting Periods",
        "Pre-Existing Disease",
        "Exclusions"
    ]

    md = []
    for section in order:
        if section in content:
            md.append(f"## {section}")
            md.append(to_bullets(content[section]))
            md.append("")

    return "\n".join(md)


def insurance_to_markdown(raw_text: str, policy_name: str, provider: str) -> str:
    from .normalise_markdown import normalize_text
    from .content_parser import parse_insurance_content

    lines = normalize_text(raw_text)
    content = parse_insurance_content(lines)

    sections_md = render_sections(content)

    return f"""doc_type: insurance
policy_name: {policy_name}
provider: {provider}
coverage_type: health
audience: senior_citizen
---

# {policy_name} – Simple Explanation

## What This Policy Is For
This policy is provided by **{provider}** to help cover medical and hospital expenses.

{sections_md}

## In Simple Words
This insurance helps pay hospital bills when you fall sick.  
Some treatments have waiting periods and exclusions depending on the illness.
"""
