import librosa
import numpy as np
import torch
from transformers import AutoFeatureExtractor, AutoModelForAudioClassification

class AudioForensicsDetector:
    def __init__(self, model_id="HyperMoon/wav2vec2-base-960h-finetuned-deepfake", device="cpu"):
        self.device = device
        self.extractor = AutoFeatureExtractor.from_pretrained(model_id)
        self.model = AutoModelForAudioClassification.from_pretrained(model_id).to(device)
        self.model.eval()

    @torch.no_grad()
    def predict_audio(self, wav_path: str) -> dict:
        """Evaluates 16 kHz audio in 4-second windows for synthetic voice artifacts."""
        waveform, sr = librosa.load(wav_path, sr=16000, mono=True)
        if len(waveform) < 8000:  # Require at least 0.5 seconds of audio
            return {"audio_fake_prob": None, "chunk_scores": []}

        chunk_size = 16000 * 4  # 4-second windows
        chunks = [
            waveform[i : i + chunk_size]
            for i in range(0, len(waveform), chunk_size)
            if len(waveform[i : i + chunk_size]) >= 8000
        ]

        inputs = self.extractor(
            chunks, sampling_rate=16000, return_tensors="pt", padding=True
        ).to(self.device)
        logits = self.model(**inputs).logits
        probs = torch.softmax(logits, dim=-1).cpu().numpy()

        id2label = {k: v.lower() for k, v in self.model.config.id2label.items()}
        fake_idx = next(
            (idx for idx, label in id2label.items() if "fake" in label or "spoof" in label), 0
        )

        chunk_scores = [float(p[fake_idx]) for p in probs]
        mel_spec = librosa.power_to_db(
            librosa.feature.melspectrogram(y=waveform, sr=sr, n_mels=128), ref=np.max
        )

        return {
            "audio_fake_prob": float(np.mean(chunk_scores)),
            "chunk_scores": chunk_scores,
            "mel_spectrogram": mel_spec.tolist()
        }