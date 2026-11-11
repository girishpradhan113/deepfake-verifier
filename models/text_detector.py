import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

class TextForensicsDetector:
    def __init__(self, model_id="roberta-base-openai-detector", device="cpu"):
        self.device = device
        print(f"Loading Text Forensics Model ({model_id})...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_id).to(device).eval()

    @torch.no_grad()
    def predict_text(self, text: str) -> dict:
        cleaned_text = text.strip()
 
        if len(cleaned_text.split()) < 15:
            return {
                "ai_generated_prob": 0.0,
                "real_prob": 1.0,
                "verdict": "INCONCLUSIVE (TEXT TOO SHORT)"
            }

        inputs = self.tokenizer(
            text, 
            return_tensors="pt", 
            truncation=True, 
            max_length=512, 
            padding=True
        ).to(self.device)
        
        outputs = self.model(**inputs)
        probs = torch.softmax(outputs.logits, dim=-1).cpu().numpy()[0]

        # roberta-base-openai-detector mapping: Index 0 = Real, Index 1 = Fake/AI-generated
        real_prob = float(probs[0])
        fake_prob = float(probs[1]) if len(probs) > 1 else 0.0

        verdict = "AI-GENERATED / SYNTHETIC" if fake_prob > 0.5 else "HUMAN-WRITTEN"

        return {
            "ai_generated_prob": round(fake_prob, 4),
            "real_prob": round(real_prob, 4),
            "verdict": verdict
        }