import c2pa

class MultimodalFusionEngine:
    @staticmethod
    def verify_c2pa_provenance(file_path: str) -> dict:
        """Checks if media contains a valid C2PA cryptographic manifest."""
        try:
            reader = c2pa.Reader.from_file(file_path)
            manifest_json = reader.json()
            return {"c2pa_present": True, "manifest_summary": manifest_json[:500]}
        except Exception:
            return {"c2pa_present": False, "manifest_summary": "No C2PA cryptographic manifest found."}

    @staticmethod
    def fuse_scores(visual_prob: float | None, audio_prob: float | None) -> dict:
        """Computes a weighted fraud probability score and assigns a forensic verdict."""
        if visual_prob is not None and audio_prob is not None:
            # Weight highest-risk modality more heavily to catch audio-only dubbing or silent face swaps
            combined_risk = 0.45 * visual_prob + 0.35 * audio_prob + 0.20 * max(visual_prob, audio_prob)
        elif visual_prob is not None:
            combined_risk = visual_prob
        elif audio_prob is not None:
            combined_risk = audio_prob
        else:
            return {"fraud_score": 0.0, "verdict": "INCONCLUSIVE"}

        if combined_risk >= 0.70:
            verdict = "MANIPULATED / SYNTHETIC"
        elif combined_risk >= 0.40:
            verdict = "SUSPICIOUS (MANUAL REVIEW REQUIRED)"
        else:
            verdict = "LIKELY AUTHENTIC"

        return {
            "fraud_score": round(combined_risk * 100, 2),
            "trust_score": round((1.0 - combined_risk) * 100, 2),
            "verdict": verdict
        }