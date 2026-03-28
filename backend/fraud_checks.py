import re


def detect_duplicates(clauses):
    seen = set()
    duplicates = []

    for clause in clauses:
        key = clause[:100]
        if key in seen:
            duplicates.append(clause)
        else:
            seen.add(key)

    return duplicates


def detect_suspicious_numbers(clauses):
    suspicious = []

    for clause in clauses:
        numbers = re.findall(r"\d+", clause)
        for num in numbers:
            if int(num) > 1_000_000:
                suspicious.append(clause)
                break

    return suspicious


def check_missing_parties(text):
    # Broad set of keywords — covers formal contracts using
    # COMMISSION/CONSULTANT/CONTRACTOR style naming too
    keywords = [
        "party", "parties", "agreement between",
        "commission", "consultant", "contractor", "client",
        "vendor", "supplier", "employer", "employee",
        "hereinafter", "referred to as", "by and between",
        "herein called", "herein referred"
    ]
    return not any(k in text.lower() for k in keywords)


def detect_suspicious_patterns(clauses):
    patterns = [
        "no liability",
        "unlimited liability",
        "non-refundable",
        "auto-renew",
        "waive all rights",
        "sole discretion",
        "without notice",
    ]

    flagged = []

    for clause in clauses:
        for p in patterns:
            if p in clause.lower():
                flagged.append(clause)
                break

    return flagged


def run_all_checks(clauses, full_text):
    """
    Run every fraud/anomaly check.
    Returns a flat list of human-readable alert strings.
    Call this single function from app.py.
    """
    alerts = []

    # 1. Duplicate clauses
    for c in detect_duplicates(clauses):
        alerts.append(f"Duplicate clause detected: \"{c[:70]}...\"")

    # 2. Suspicious large numbers
    for c in detect_suspicious_numbers(clauses):
        nums = [int(n) for n in re.findall(r"\d+", c) if int(n) > 1_000_000]
        alerts.append(f"Unusually large figure ({nums[0]:,}) found in: \"{c[:60]}...\"")

    # 3. Missing party names
    if check_missing_parties(full_text):
        alerts.append("No party names detected — contract may be incomplete or fraudulent.")

    # 4. Suspicious legal patterns
    pattern_labels = {
        "no liability":        "No-liability waiver",
        "unlimited liability": "Unlimited liability clause",
        "non-refundable":      "Non-refundable payment term",
        "auto-renew":          "Auto-renewal clause",
        "waive all rights":    "Rights waiver",
        "sole discretion":     "Sole discretion clause",
        "without notice":      "No-notice termination/change",
    }

    for clause in clauses:
        for pattern, label in pattern_labels.items():
            if pattern in clause.lower():
                alerts.append(f"{label} found: \"{clause[:65]}...\"")
                break

    return list(dict.fromkeys(alerts))