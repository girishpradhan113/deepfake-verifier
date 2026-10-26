import io
import base64
import numpy as np
import torch
from PIL import Image, ImageChops, ImageEnhance
from transformers import AutoImageProcessor, AutoModelForImageClassification

class VisualForensicsDetector:
    def __init__(
        self,
        face_model_id="dima806/deepfake_vs_real_image_detection",
        aigen_model_id="umm-maybe/AI-image-detector",
        device="cpu"
    ):
        self.device = device
        # 1. Human Face Deepfake Detector
        self.face_proc = AutoImageProcessor.from_pretrained(face_model_id)
        self.face_model = AutoModelForImageClassification.from_pretrained(face_model_id).to(device).eval()

        # 2. General AI-Generated / Diffusion Image Detector
        self.aigen_proc = AutoImageProcessor.from_pretrained(aigen_model_id)
        self.aigen_model = AutoModelForImageClassification.from_pretrained(aigen_model_id).to(device).eval()

    def _score_batch(self, images: list, processor, model, target_keywords: tuple) -> list:
        inputs = processor(images=images, return_tensors="pt").to(self.device)
        logits = model(**inputs).logits
        probs = torch.softmax(logits, dim=-1).cpu().numpy()

        id2label = {k: v.lower() for k, v in model.config.id2label.items()}
        fake_idx = next(
            (idx for idx, label in id2label.items() if any(k in label for k in target_keywords)), 1
        )
        return [float(p[fake_idx]) for p in probs]

    @torch.no_grad()
    def predict_faces(self, images: list) -> dict:
        """Evaluates images for both facial deepfakes and full-scene AI generation."""
        if not images:
            return {"visual_fake_prob": None, "frame_scores": [], "ela_base64": None}

        face_scores = self._score_batch(images, self.face_proc, self.face_model, ("fake", "df"))
        aigen_scores = self._score_batch(images, self.aigen_proc, self.aigen_model, ("artificial", "fake", "ai"))

        # Take the higher risk score per frame between Face Manipulation and AI Generation
        combined_scores = [max(f, a) for f, a in zip(face_scores, aigen_scores)]

        # Generate ELA heatmap for the first frame/image
        ela_img = self.compute_ela(images[0])
        buf = io.BytesIO()
        ela_img.save(buf, format="PNG")
        ela_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

        return {
            "visual_fake_prob": float(np.mean(combined_scores)),
            "face_deepfake_prob": float(np.mean(face_scores)),
            "ai_generated_prob": float(np.mean(aigen_scores)),
            "frame_scores": combined_scores,
            "ela_base64": ela_b64
        }

    @staticmethod
    def compute_ela(image: Image.Image, quality: int = 90) -> Image.Image:
        """Generates an Error Level Analysis (ELA) heatmap to expose spliced/synthetic regions."""
        buffer = io.BytesIO()
        rgb_img = image.convert("RGB")
        rgb_img.save(buffer, "JPEG", quality=quality)
        buffer.seek(0)
        resaved = Image.open(buffer)

        ela_img = ImageChops.difference(rgb_img, resaved)
        extrema = ela_img.getextrema()
        max_diff = max([ex[1] for ex in extrema]) or 1
        scale = 255.0 / max_diff
        return ImageEnhance.Brightness(ela_img).enhance(scale)