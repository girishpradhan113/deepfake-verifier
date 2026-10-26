import base64
import streamlit as st
import requests

# Page Configuration
st.set_page_config(
    page_title="DeepShield | Multimodal Forensics Suite",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling for Cyber-Forensics Look
st.markdown("""
    <style>
        .main { background-color: #0b0f19; }
        .stMetric {
            background-color: #111827;
            padding: 15px;
            border-radius: 10px;
            border: 1px solid #1f2937;
        }
        .report-card {
            background-color: #111827;
            padding: 20px;
            border-radius: 12px;
            border: 1px solid #374151;
            margin-bottom: 20px;
        }
    </style>
""", unsafe_allow_html=True)

# Sidebar Controls
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/security-checked.png", width=64)
    st.title("DeepShield AI")
    st.markdown("---")
    st.markdown("### 🔍 Forensic Modules")
    st.info(
        "• **Visual:** Face-Swap, AI-Gen & ELA\n"
        "• **Audio:** Wav2Vec 2.0 Voice Spoofing\n"
        "• **Provenance:** C2PA Content Credentials"
    )
    st.markdown("---")
    st.markdown("### ⚙️ Thresholds")
    sensitivity = st.slider("Detection Sensitivity", 0.0, 1.0, 0.5, 0.05)
    st.caption("Adjusts late-fusion risk calibration.")

# Main Header
st.title("🛡️ Multimodal Deepfake & AI Voice Verification Suite")
st.markdown(
    "Upload suspicious video, audio, or image assets for cryptographic and deep-learning forensic inspection."
)

# File Uploader Container
uploaded_file = st.file_uploader(
    "Choose a media file for analysis",
    type=["mp4", "mov", "avi", "wav", "mp3", "flac", "jpg", "jpeg", "png", "webp"],
    help="Supports video containers, audio tracks, and compressed images."
)

if uploaded_file is not None:
    col_preview, col_info = st.columns([1, 2])

    with col_preview:
        st.markdown("#### 📂 Target Preview")
        file_ext = uploaded_file.name.split(".")[-1].lower()
        if file_ext in ["jpg", "jpeg", "png", "webp"]:
            st.image(uploaded_file, caption=uploaded_file.name, use_container_width=True)
        elif file_ext in ["mp4", "mov", "avi"]:
            st.video(uploaded_file)
        elif file_ext in ["wav", "mp3", "flac"]:
            st.audio(uploaded_file)
        else:
            st.write(f"File: `{uploaded_file.name}`")

    with col_info:
        st.markdown("#### 📋 File Metadata")
        st.markdown(f"""
        * **Filename:** `{uploaded_file.name}`
        * **Size:** `{round(uploaded_file.size / (1024 * 1024), 2)} MB`
        * **Format Type:** `{file_ext.upper()}`
        """)

        analyze_btn = st.button("🚀 Run Deep Forensic Scan", type="primary", use_container_width=True)

    if analyze_btn:
        with st.status("Executing Multi-Stream Forensic Pipeline...", expanded=True) as status:
            st.write("🔄 Demuxing streams & extracting frames / 16kHz audio...")
            st.write("🧠 Running visual deepfake/AI-gen checks & Wav2Vec2 audio scoring...")
            st.write("🔐 Inspecting C2PA cryptographic container manifests...")

            try:
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                # 300-second timeout prevents ReadTimeout during large CPU inferences or weight loading
                response = requests.post("http://localhost:8000/verify", files=files, timeout=300)

                if response.status_code == 200:
                    res = response.json()
                    status.update(label="Forensic Scan Complete!", state="complete", expanded=False)
                else:
                    status.update(label="Scan Failed on Backend", state="error")
                    st.error(f"Server returned error code {response.status_code}")
                    st.stop()
            except requests.exceptions.ReadTimeout:
                status.update(label="Request Timed Out", state="error")
                st.error(
                    "The backend took longer than 5 minutes to respond. Check Terminal 1 (`uvicorn`) "
                    "to see if Hugging Face is still downloading model weights."
                )
                st.stop()
            except requests.exceptions.ConnectionError:
                status.update(label="Connection Refused", state="error")
                st.error(
                    "Could not connect to FastAPI backend. Ensure `uvicorn app.api:app --reload --port 8000` "
                    "is running in Terminal 1."
                )
                st.stop()

        # Display Results Dashboard
        fusion = res["fusion"]
        verdict = fusion["verdict"]
        fraud_score = fusion["fraud_score"]

        st.markdown("---")
        st.header("📊 Forensic Assessment Report")

        # Top Metric Cards
        m1, m2, m3 = st.columns(3)

        verdict_color = "🔴" if "MANIPULATED" in verdict else ("🟡" if "SUSPICIOUS" in verdict else "🟢")
        m1.metric("Authenticity Verdict", f"{verdict_color} {verdict}")
        m2.metric("Calculated Fraud Risk", f"{fraud_score}%")

        c2pa_status = "Verified 🔐" if res["provenance"]["c2pa_present"] else "Missing / Stripped ⚠️"
        m3.metric("Cryptographic Provenance", c2pa_status)

        # Risk Progress Bar
        st.markdown("### Threat Probability Meter")
        st.progress(min(max(float(fraud_score) / 100.0, 0.0), 1.0))

        # Detailed Tab Breakdown
        tab1, tab2, tab3 = st.tabs(["👁️ Visual Analysis", "🎙️ Audio Forensics", "📜 Provenance & Metadata"])

        with tab1:
            st.subheader("Visual Face-Swap, AI Generation & Tampering Forensics")
            vis_res = res.get("visual_analysis", {})
            if vis_res.get("visual_fake_prob") is not None:
                c1, c2, c3 = st.columns(3)
                c1.metric("Combined Visual Risk", f"{round(vis_res['visual_fake_prob'] * 100, 2)}%")
                c2.metric(
                    "Face-Swap Probability",
                    f"{round(vis_res.get('face_deepfake_prob', vis_res['visual_fake_prob']) * 100, 2)}%"
                )
                c3.metric(
                    "Full AI-Gen Probability",
                    f"{round(vis_res.get('ai_generated_prob', 0.0) * 100, 2)}%"
                )

                if vis_res.get("ela_base64"):
                    st.markdown("#### 🔍 Error Level Analysis (ELA) Compression Heatmap")
                    st.image(
                        base64.b64decode(vis_res["ela_base64"]),
                        caption="Brighter regions indicate compression anomalies or synthetic textures",
                        width=420
                    )

                frame_scores = vis_res.get("frame_scores", [])
                if len(frame_scores) > 1:
                    st.markdown("#### Frame-by-Frame Anomaly Score Timeline")
                    st.line_chart(frame_scores)
            else:
                st.info("No visual data detected or file is purely audio.")

        with tab2:
            st.subheader("AI Voice Cloning & Vocoder Forensics")
            aud_res = res.get("audio_analysis", {})
            if aud_res.get("audio_fake_prob") is not None:
                st.metric("Synthetic Voice Spoof Probability", f"{round(aud_res['audio_fake_prob'] * 100, 2)}%")
                chunk_scores = aud_res.get("chunk_scores", [])
                if chunk_scores:
                    st.markdown("#### 4-Second Temporal Audio Window Scores")
                    st.bar_chart(chunk_scores)
            else:
                st.info("No audio stream detected or file is a static image/silent video.")

        with tab3:
            st.subheader("Content Credentials & Provenance Manifest")
            prov = res.get("provenance", {})
            st.write(prov.get("manifest_summary", "No manifest data available."))
            if prov.get("c2pa_present"):
                st.success("This media file contains a valid C2PA tamper-evident cryptographic provenance trail.")
            else:
                st.warning(
                    "No C2PA metadata found. The file may have been re-encoded, stripped of metadata, "
                    "or generated without cryptographic tracking."
                )