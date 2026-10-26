import os
import subprocess
import cv2
import numpy as np
import imageio_ffmpeg
from PIL import Image
from facenet_pytorch import MTCNN

class MediaIngestor:
    def __init__(self, device="cpu"):
        self.face_detector = MTCNN(keep_all=False, device=device, margin=20, post_process=False)
        self.ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

    def extract_audio(self, media_path: str, output_wav: str) -> bool:
        """Extracts 16 kHz mono WAV from a video or audio file using bundled FFmpeg."""
        cmd = [
            self.ffmpeg_exe, "-y", "-i", media_path,
            "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
            output_wav
        ]
        result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return result.returncode == 0 and os.path.exists(output_wav)

    def extract_face_crops(self, video_path: str, num_frames: int = 16) -> list:
        """Samples evenly spaced frames from video and returns cropped PIL face images."""
        cap = cv2.VideoCapture(video_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if total_frames <= 0:
            cap.release()
            return []

        frame_indices = np.linspace(0, total_frames - 1, num_frames, dtype=int)
        face_crops = []

        for idx in frame_indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ret, frame = cap.read()
            if not ret:
                continue
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            boxes, _ = self.face_detector.detect(rgb_frame)
            if boxes is not None and len(boxes) > 0:
                x1, y1, x2, y2 = [max(0, int(b)) for b in boxes[0]]
                face = rgb_frame[y1:y2, x1:x2]
                if face.size > 0:
                    face_crops.append(Image.fromarray(face))

        cap.release()
        return face_crops