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
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=JetBrains+Mono:wght@500&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        .main {
            background: radial-gradient(circle at top right, #111827, #0b0f19 60%);
        }

        h1 {
            background: linear-gradient(90deg, #38BDF8 0%, #818CF8 50%, #C084FC 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800 !important;
        }

        .stMetric, [data-testid="stMetric"], .report-card, div[data-testid="stVerticalBlockBorderWrapper"] {
            background: rgba(17, 24, 39, 0.75) !important;
            backdrop-filter: blur(12px);
            padding: 18px !important;
            border-radius: 14px !important;
            border: 1px solid rgba(56, 189, 248, 0.25) !important;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.35);
        }

        [data-testid="stMetricValue"] {
            font-family: 'JetBrains Mono', monospace;
            color: #F8FAFC !important;
        }

        [data-testid="stFileUploader"] section {
            background: rgba(15, 23, 42, 0.65) !important;
            border: 2px dashed rgba(56, 189, 248, 0.4) !important;
            border-radius: 16px !important;
            padding: 2rem !important;
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0b0f19 0%, #111827 100%);
            border-right: 1px solid rgba(56, 189, 248, 0.15);
        }
    </style>
""", unsafe_allow_html=True)

# Sidebar Controls
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/security-checked.png", width=64)
    st.title("DeepShield AI")
    st.markdown("---")
    st.markdown("### 🛡️ Navigation Mode")
    app_mode = st.radio(
        "Select Forensic Engine",
        ["📁 Media Forensics (Video/Audio/Image)", "✍️ Text Forensics"]
    )
    st.markdown("---")
    st.markdown("### ⚙️ Thresholds")
    sensitivity = st.slider("Detection Sensitivity", 0.0, 1.0, 0.5, 0.05)
    st.caption("Adjusts late-fusion risk calibration.")

# ==========================================
# MODE 1: MEDIA FORENSICS
# ==========================================
if app_mode == "📁 Media Forensics (Video/Audio/Image)":
    st.title("🛡️ Multimodal Deepfake & AI Voice Verification Suite")
    st.markdown("Upload suspicious video, audio, or image assets for cryptographic and deep-learning forensic inspection.")

    uploaded_file = st.file_uploader(
        "Choose a media file for analysis",
        type=["mp4", "mov", "avi", "wav", "mp3", "flac", "jpg", "jpeg", "png", "webp"],
        help="Supports video containers, audio tracks, and compressed images."
    )

    if uploaded_file is None:
        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            with st.container(border=True):
                st.markdown("#### 🎭 Visual Deepfake & ELA")
                st.caption("Detects face-swaps, diffusion artifacts, and pixel-level compression tampering.")
        with c2:
            with st.container(border=True):
                st.markdown("#### 🎙️ AI Voice Cloning")
                st.caption("Analyzes acoustic anomalies and synthetic speech patterns using Wav2Vec 2.0.")
        with c3:
            with st.container(border=True):
                st.markdown("#### 🛡️ C2PA Provenance")
                st.caption("Verifies cryptographic content credentials and checks for stripped metadata.")

    if uploaded_file is not None:
        col_preview, col_info = st.columns([1, 2], gap="large")

        with col_preview:
            with st.container(border=True):
                st.markdown("#### 🖼️ Target Preview")
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
            with st.container(border=True):
                st.markdown("#### 📄 File Metadata & Scan Control")
                m1, m2, m3 = st.columns(3)
                m1.metric("Format Type", file_ext.upper())
                m2.metric("File Size", f"{round(uploaded_file.size / (1024 * 1024), 2)} MB")
                m3.metric("Status", "Ready to Scan")
                st.caption(f"**Filename:** `{uploaded_file.name}`")
                st.markdown("<br>", unsafe_allow_html=True)
                analyze_btn = st.button("🚀 Run Deep Forensic Scan", type="primary", use_container_width=True)

        if analyze_btn:
            with st.status("Executing Multi-Stream Forensic Pipeline...", expanded=True) as status:
                st.write("🔄 Demuxing streams & extracting frames / 16kHz audio...")
                st.write("🧠 Running visual deepfake/AI-gen checks & Wav2Vec2 audio scoring...")
                st.write("🔐 Inspecting C2PA cryptographic container manifests...")

                try:
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
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
                    st.error("The backend took longer than 5 minutes to respond.")
                    st.stop()
                except requests.exceptions.ConnectionError:
                    status.update(label="Connection Refused", state="error")
                    st.error("Could not connect to FastAPI backend. Ensure uvicorn is running.")
                    st.stop()

            # Display Results Tabs
            tab1, tab2, tab3 = st.tabs(["👁️ Visual Analysis", "🎙️ Audio Forensics", "📜 Provenance & Metadata"])
            
            with tab1:
                st.subheader("Visual Face-Swap, AI Generation & Tampering Forensics")
                vis_res = res.get("visual_analysis", {})
                if vis_res.get("visual_fake_prob") is not None:
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Combined Visual Risk", f"{round(vis_res['visual_fake_prob'] * 100, 2)}%")
                    c2.metric("Face-Swap Probability", f"{round(vis_res.get('face_deepfake_prob', vis_res['visual_fake_prob']) * 100, 2)}%")
                    c3.metric("Full AI-Gen Probability", f"{round(vis_res.get('ai_generated_prob', 0.0) * 100, 2)}%")

                    if vis_res.get("ela_base64"):
                        st.markdown("#### 🔍 Error Level Analysis (ELA) Compression Heatmap")
                        st.image(base64.b64decode(vis_res["ela_base64"]), caption="Anomalies & synthetic textures", width=420)

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
                    st.info("No audio stream detected.")

            with tab3:
                st.subheader("Content Credentials & Provenance Manifest")
                prov = res.get("provenance", {})
                st.write(prov.get("manifest_summary", "No manifest data available."))
                if prov.get("c2pa_present"):
                    st.success("This media file contains a valid C2PA cryptographic provenance trail.")
                else:
                    st.warning("No C2PA metadata found. File may have been re-encoded or stripped.")

# ==========================================
# MODE 2: TEXT FORENSICS
# ==========================================
elif app_mode == "✍️ Text Forensics":
    st.title("✍️ AI-Generated Text Forensics")
    st.markdown("Paste suspicious articles, essays, or chat logs below to detect machine-generated writing patterns.")

    sample_text = st.text_area("Enter text paragraph for inspection:", height=200, placeholder="Type or paste text here...")
    scan_text_btn = st.button("🚀 Analyze Text Authenticity", type="primary")

    if scan_text_btn:
        if not sample_text.strip():
            st.warning("Please enter some text to analyze.")
        else:
            with st.spinner("Analyzing linguistic perplexity and burstiness..."):
                try:
                    response = requests.post("http://localhost:8000/verify-text", json={"text": sample_text}, timeout=300)
                    if response.status_code == 200:
                        t_res = response.json().get("text_analysis", {})
                        ai_prob = t_res.get("ai_generated_prob", 0.0) * 100
                        t_verdict = t_res.get("verdict", "UNKNOWN")

                        st.markdown("---")
                        col_t1, col_t2 = st.columns(2)
                        t_color = "🔴" if "AI" in t_verdict else "🟢"
                        col_t1.metric("Text Verdict", f"{t_color} {t_verdict}")
                        col_t2.metric("AI-Generation Probability", f"{round(ai_prob, 2)}%")

                        st.markdown("### Threat Probability Meter")
                        st.progress(min(max(ai_prob / 100.0, 0.0), 1.0))
                    else:
                        st.error("Backend error during text analysis.")
                except Exception as e:
                    st.error(f"Connection failed: {e}")