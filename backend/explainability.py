def generate_explanation(clause, risk):
    clause = clause.lower()

    if "terminate" in clause:
        return "This clause allows termination of the agreement, which may cause sudden loss."

    if "liability" in clause:
        return "This clause defines liability, which may expose one party to financial risk."

    if "payment" in clause:
        return "This clause includes payment terms that may lead to disputes."

    if "penalty" in clause:
        return "This clause imposes penalties, which could result in financial loss."

    if "confidential" in clause:
        return "This clause requires confidentiality, which may create legal obligations."

    if risk == "High":
        return "This clause may involve significant legal or financial risk."

    elif risk == "Medium":
        return "This clause has moderate risk and should be reviewed."

    else:
        return "This clause appears relatively safe."