def to_bullets(lines: list[str], max_items=10) -> str:
    bullets = []
    for line in lines:
        if len(line) > 25:
            bullets.append(f"- {line}")
        if len(bullets) >= max_items:
            break
    return "\n".join(bullets)

def insurance_to_markdown(raw_text: str, policy_name: str, provider: str) -> str:
    from .normalise_markdown import normalize_text
    from .content_parser import parse_insurance_content

    lines = normalize_text(raw_text)
    content = parse_insurance_content(lines)

    return f"""---
doc_type: insurance
policy_name: {policy_name}
provider: {provider}
coverage_type: health
audience: senior_citizen
---

# {policy_name} – Simple Explanation

## What This Policy Is For
This policy is provided by **{provider}** to help cover medical and hospital expenses.

## What Is Covered
{to_bullets(content.get("What Is Covered", []))}

## Special Benefits
{to_bullets(content.get("Special Benefits", []))}

## What Is NOT Covered
{to_bullets(content.get("What Is NOT Covered", []))}

## Important Waiting Periods
{to_bullets(content.get("Waiting Periods", []))}

## In Simple Words
This insurance helps pay hospital bills when you fall sick.  
Some treatments are covered only after a waiting period.
"""
