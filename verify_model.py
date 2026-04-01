# Save as verify_model.py and run it
from transformers import (
    DistilBertForSequenceClassification,
    DistilBertTokenizer
)
import torch
import os

# Try mlflow_best first, fall back to best_distilbert
model_path = 'models/mlflow_best' \
    if os.path.exists('models/mlflow_best') \
    else 'models/best_distilbert'

tokenizer_path = 'models/tokenizer'

print(f"Loading model from: {model_path}")

model     = DistilBertForSequenceClassification\
    .from_pretrained(model_path)
tokenizer = DistilBertTokenizer\
    .from_pretrained(tokenizer_path)
model.eval()

# Quick test
test_text = "Apple reported record profits."
inputs = tokenizer(
    test_text,
    max_length=128,
    padding='max_length',
    truncation=True,
    return_tensors='pt'
)

with torch.no_grad():
    outputs = model(**inputs)
    probs   = torch.softmax(
        outputs.logits, dim=1)
    pred    = probs.argmax(dim=1).item()
    conf    = probs.max().item()

label_map = {
    0:'World', 1:'Sports',
    2:'Business', 3:'Sci/Tech'
}

print(f"✅ Model loaded successfully")
print(f"   Test: '{test_text}'")
print(f"   Prediction: {label_map[pred]}")
print(f"   Confidence: {conf:.4f}")