weights = {
    "Low": 1,
    "Medium": 2,
    "High": 3
}


def calculate_risk_score(results):
    if not results:
        return 0, "Low Risk", 0

    total = 0
    high_penalty = 0
    high_count = 0

    for r in results:
        w = weights[r["risk"]]
        conf = r["confidence"]

        total += w * conf

        if r["risk"] == "High":
            high_penalty += 0.5 * conf
            high_count += 1

    avg_score = total / len(results)

    final_score = avg_score + high_penalty
    final_score = min(final_score, 3)

    if final_score < 1.5:
        level = "Low Risk"
    elif final_score < 2.3:
        level = "Medium Risk"
    else:
        level = "High Risk"

    return round(final_score, 2), level, high_count