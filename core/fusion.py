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
    def fuse_scores(visual_prob, audio_prob):
        # Default fallback if streams are missing
        scores = [p for p in [visual_prob, audio_prob] if p is not None]
        if not scores:
            return {"fraud_score": 0.0, "verdict": "INSUFFICIENT DATA"}

        fraud_score = round(sum(scores) / len(scores) * 100, 2)

        # Introduce a Confidence Deadzone to prevent false binary guesses
        if 42 <= fraud_score <= 58:
            verdict = "INCONCLUSIVE / AMBIGUOUS"
        elif fraud_score > 58:
            verdict = "HIGH PROBABILITY MANIPULATED 🔴"
        else:
            verdict = "AUTHENTIC 🟢"

        return {
            "fraud_score": fraud_score,
            "verdict": verdict
        }