try:
    from backend.model_loader import predict_batch, label_map
    from backend.explainability import generate_explanation
except ImportError:
    from model_loader import predict_batch, label_map
    from explainability import generate_explanation


def analyze_clauses(clauses):
    if not clauses:
        return []

    preds, probs = predict_batch(clauses)

    results = []

    for i, clause in enumerate(clauses):
        risk = label_map[preds[i].item()]
        confidence = round(probs[i][preds[i]].item(), 3)

        results.append({
            "clause": clause,
            "risk": risk,
            "confidence": confidence,
            "explanation": generate_explanation(clause, risk)
        })

    return results