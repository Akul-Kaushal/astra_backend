def detect_section(line: str) -> str | None:
    l = line.lower()

    # ---------------- CORE COVERAGE ----------------
    if any(k in l for k in [
        "in-patient", "hospitalisation", "hospitalization", "room rent",
        "icu", "intensive care", "surgeon", "operation theatre"
    ]):
        return "Hospitalization Coverage"

    if "day care" in l:
        return "Day Care Treatment"

    if "pre-hospital" in l or "post hospital" in l:
        return "Pre & Post Hospitalization"

    if any(k in l for k in ["modern treatment", "robotic", "immunotherapy", "stem cell"]):
        return "Modern Treatments"

    if "ayush" in l or "ayurveda" in l or "homeopathy" in l:
        return "AYUSH Treatment"

    if "organ donor" in l or "transplant" in l:
        return "Organ Donor / Transplant"

    if "road ambulance" in l or "air ambulance" in l:
        return "Ambulance Coverage"

    if "home care" in l or "domiciliary" in l:
        return "Home Care / Domiciliary Treatment"

    if "out-patient" in l or "opd" in l:
        return "Out Patient Coverage"

    # ---------------- DISEASE SPECIFIC ----------------
    if "cardiac" in l or "heart" in l:
        return "Cardiac Coverage"

    if "critical illness" in l:
        return "Critical Illness Coverage"

    if "cancer" in l or "chemotherapy" in l:
        return "Cancer Coverage"

    if "diabetes" in l or "hypertension" in l:
        return "Chronic Disease Coverage"

    if "kidney" in l or "dialysis" in l or "renal" in l:
        return "Renal Coverage"

    if "stroke" in l or "paralysis" in l or "brain" in l:
        return "Neurological Coverage"

    # ---------------- BENEFITS ----------------
    if "restoration" in l or "reinstatement" in l:
        return "Restoration Benefit"

    if "no claim bonus" in l or "cumulative bonus" in l:
        return "No Claim Bonus"

    if "wellness" in l or "reward" in l:
        return "Wellness Benefits"

    if "health check" in l:
        return "Health Check-up"

    if "rehabilitation" in l or "pain management" in l:
        return "Rehabilitation & Pain Management"

    if "e-medical opinion" in l or "second opinion" in l:
        return "Second Opinion"

    # ---------------- OPTIONAL COVERS ----------------
    if "maternity" in l or "new born" in l:
        return "Maternity & New Born"

    if "personal accident" in l:
        return "Personal Accident Cover"

    if "women care" in l:
        return "Women Care"

    if "deductible" in l or "co-payment" in l:
        return "Deductible / Co-pay"

    if "room rent modification" in l:
        return "Room Rent Modification"

    # ---------------- WAITING & LIMITS ----------------
    if "waiting period" in l:
        return "Waiting Periods"

    if "pre-existing" in l or "ped" in l:
        return "Pre-Existing Disease"

    if "sub-limit" in l or "limit per" in l or "maximum of" in l:
        return "Sub-limits & Caps"

    if "moratorium" in l:
        return "Moratorium Period"

    # ---------------- EXCLUSIONS ----------------
    if "exclusion" in l or "shall not be liable" in l:
        return "Exclusions"

    # ---------------- ADMIN ----------------
    if "eligibility" in l or "entry age" in l:
        return "Eligibility"

    if "sum insured" in l:
        return "Sum Insured"

    if "premium" in l or "instalment" in l:
        return "Premium & Payment"

    if "renewal" in l or "grace period" in l:
        return "Renewal & Grace Period"

    if "portability" in l or "migration" in l:
        return "Portability & Migration"

    if "claim" in l:
        return "Claims Procedure"

    if "cancellation" in l or "free look" in l:
        return "Cancellation & Free Look"

    return None
