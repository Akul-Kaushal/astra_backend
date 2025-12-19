from collections import defaultdict
from .section_detector import detect_section

def parse_insurance_content(lines: list[str]) -> dict:
    sections = defaultdict(list)
    current_section = None

    for line in lines:
        detected = detect_section(line)
        if detected:
            current_section = detected

        if current_section:
            sections[current_section].append(line)

    return sections
