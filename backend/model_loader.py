import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# Change this one line:
MODEL_PATH = "Deepakkumar9897/bert-legal-risk"

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)

model.to(device)
model.eval()

label_map = {0: "Low", 1: "Medium", 2: "High"}


def predict_batch(texts):
    inputs = tokenizer(
        texts,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=128
    )

    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model(**inputs)

    probs = torch.softmax(outputs.logits, dim=1)
    preds = torch.argmax(probs, dim=1)

    return preds, probs