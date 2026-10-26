import os
import shutil
from fastapi import FastAPI, UploadFile, File
from PIL import Image
from core.ingest import MediaIngestor
from core.fusion import MultimodalFusionEngine
from models.visual_detector import VisualForensicsDetector
from models.audio_detector import AudioForensicsDetector

app = FastAPI(title="Multimodal Deepfake & AI Voice Verification API")

ingestor = MediaIngestor()
visual_detector = VisualForensicsDetector()
audio_detector = AudioForensicsDetector()
fusion_engine = MultimodalFusionEngine()

@app.post("/verify")
async def verify_media(file: UploadFile = File(...)):
    os.makedirs("temp", exist_ok=True)
    file_path = os.path.join("temp", file.filename)
    wav_path = file_path + ".wav"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    ext = os.path.splitext(file.filename)[1].lower()
    visual_res = {"visual_fake_prob": None, "frame_scores": []}
    audio_res = {"audio_fake_prob": None, "chunk_scores": []}

    # 1. Visual branch (Image or Video)
    if ext in [".jpg", ".jpeg", ".png", ".webp"]:
        img = Image.open(file_path).convert("RGB")
        visual_res = visual_detector.predict_faces([img])
    elif ext in [".mp4", ".mov", ".avi", ".mkv"]:
        faces = ingestor.extract_face_crops(file_path, num_frames=12)
        visual_res = visual_detector.predict_faces(faces)

    # 2. Audio branch (Audio or Video container)
    if ext in [".wav", ".mp3", ".flac", ".m4a", ".mp4", ".mov", ".mkv"]:
        if ingestor.extract_audio(file_path, wav_path):
            audio_res = audio_detector.predict_audio(wav_path)

    # 3. Provenance & Late Fusion
    provenance = fusion_engine.verify_c2pa_provenance(file_path)
    fusion = fusion_engine.fuse_scores(
        visual_res["visual_fake_prob"], audio_res["audio_fake_prob"]
    )

    return {
        "filename": file.filename,
        "fusion": fusion,
        "visual_analysis": visual_res,
        "audio_analysis": {
            "audio_fake_prob": audio_res.get("audio_fake_prob"),
            "chunk_scores": audio_res.get("chunk_scores", [])
        },
        "provenance": provenance
    }