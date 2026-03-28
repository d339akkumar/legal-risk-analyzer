import os
from groq import Groq


def _get_client(api_key: str = None):
    key = api_key or os.environ.get("GROQ_API_KEY")
    if not key:
        raise ValueError(
            "GROQ_API_KEY not found.\n"
            "  Local: run  set GROQ_API_KEY=your-key  in your terminal\n"
            "  Or add it to C:\\Users\\Lenovo\\.streamlit\\secrets.toml"
        )
    return Groq(api_key=key)


def generate_ai_explanation(clause: str, api_key: str = None) -> str:
    """Explain a single legal clause in plain English (2-3 sentences)."""
    prompt = (
        "Explain this legal clause in simple English. "
        "Also explain why it may be risky. "
        "Keep it short — 2 to 3 sentences only.\n\n"
        f"Clause:\n{clause}"
    )
    try:
        client = _get_client(api_key)
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Explanation not available. ({e})"


def summarize_document(clauses_with_risk: list, score: float, level: str, api_key: str = None) -> str:
    """
    Generate a detailed, specific plain-English summary of the contract.
    clauses_with_risk: list of dicts — keys: clause, risk, confidence, explanation
    api_key: passed directly from app.py using st.secrets
    """
    high_count  = sum(1 for r in clauses_with_risk if r["risk"] == "High")
    med_count   = sum(1 for r in clauses_with_risk if r["risk"] == "Medium")
    low_count   = sum(1 for r in clauses_with_risk if r["risk"] == "Low")
    total       = len(clauses_with_risk)

    # Send high risk clauses separately so AI can be specific about them
    high_clauses = "\n".join(
        f"- {r['clause'][:200]}"
        for r in clauses_with_risk if r["risk"] == "High"
    )[:1500]

    med_clauses = "\n".join(
        f"- {r['clause'][:150]}"
        for r in clauses_with_risk if r["risk"] == "Medium"
    )[:800]

    prompt = f"""You are a senior legal analyst reviewing a contract for a non-lawyer client.

CONTRACT STATS:
- Overall risk score: {score}/3.00 — {level}
- High risk clauses: {high_count}
- Medium risk clauses: {med_count}
- Low risk clauses: {low_count}
- Total clauses: {total}

HIGH RISK CLAUSES FOUND:
{high_clauses if high_clauses else "None"}

MEDIUM RISK CLAUSES:
{med_clauses if med_clauses else "None"}

Write a detailed analysis with EXACTLY this structure — use these exact headings:

VERDICT: One sentence on whether this contract is safe to sign.

KEY RISKS: List the 2-3 most dangerous specific issues found (mention actual clause content like termination terms, liability caps, payment conditions). Be specific — not generic.

WHAT TO WATCH OUT FOR: 2-3 practical things the signing party must negotiate or clarify before signing.

OVERALL ASSESSMENT: One final sentence with a clear recommendation.

Keep each section short and in plain English. No legal jargon."""

    try:
        client = _get_client(api_key)
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a senior legal risk analyst. "
                        "Give specific, actionable advice based on the actual clause content provided. "
                        "Never give generic advice — always refer to specific issues found in the contract."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=600,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Summary not available. ({e})"