import re


def split_into_clauses(text):
    clauses = re.split(r'\n\s*\n|(?<=\.)\s+(?=[A-Z])|(?=\d+\.\s)', text)

    cleaned = []

    for c in clauses:
        c = c.strip()

        if len(c.split()) < 8:
            continue

        if any(keyword in c.lower() for keyword in [
            "ministry", "road", "complex", "government",
            "department", "email", "phone", "address"
        ]):
            continue

        if len(re.findall(r'[^a-zA-Z0-9\s]', c)) > len(c) * 0.3:
            continue

        cleaned.append(c)

    return cleaned