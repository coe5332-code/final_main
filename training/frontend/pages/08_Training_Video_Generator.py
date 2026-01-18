import streamlit as st
import asyncio
import logging
import os
import tempfile
import requests
import shutil
from typing import Optional, List, Dict
from datetime import datetime
import sys

# ==========================================
# PATH SETUP - CRITICAL FOR IMPORTS
# ==========================================
current_dir = os.path.dirname(os.path.abspath(__file__))
frontend_dir = os.path.dirname(current_dir)
project_root = os.path.dirname(frontend_dir)

if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from utils.service_utils import validate_service_content
    from utils.audio_utils import text_to_speech
    from utils.video_utils import create_slide, combine_slides_and_audio
    from services.unsplash_service import fetch_and_save_photo
    from services.gemini_service import generate_slides_from_raw
    from utils.avatar_utils import add_avatar_to_slide
    from utils.pdf_extractor import extract_raw_content
    from utils.pdf_utils import generate_service_pdf

    IMPORTS_SUCCESSFUL = True
except ImportError as e:
    IMPORTS_SUCCESSFUL = False
    IMPORT_ERROR = str(e)

try:
    from moviepy.config import change_settings

    change_settings(
        {
            "IMAGEMAGICK_BINARY": r"C:\Program Files\ImageMagick-7.1.2-Q16-HDRI\magick.exe"
        }
    )
except:
    pass

logging.basicConfig(level=logging.INFO)

st.set_page_config(page_title="Training Video Generator", page_icon="🎥", layout="wide")

if not IMPORTS_SUCCESSFUL:
    st.error("❌ Failed to import required modules")
    with st.expander("🔍 Debug Information", expanded=True):
        st.error(f"**Import Error:** {IMPORT_ERROR}")
        st.write("**Path Information:**")
        st.code(f"Current file: {__file__}")
        st.code(f"Project root: {project_root}")
    st.stop()

st.markdown(
    """
<style>
    .video-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
    }
    
    .service-card {
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        padding: 1.5rem;
        background: white;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    
    .version-badge {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        display: inline-block;
        font-weight: bold;
    }
    
    .video-preview {
        border: 3px solid #667eea;
        border-radius: 10px;
        padding: 1rem;
        background: #f8f9fa;
        margin: 1rem 0;
    }
    
    .error-box {
        background-color: #ffe6e6;
        border-left: 4px solid #ff4444;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    
    .success-box {
        background-color: #e6ffe6;
        border-left: 4px solid #44ff44;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
</style>
""",
    unsafe_allow_html=True,
)

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:54300")
VIDEOS_BASE_DIR = os.path.join(project_root, "videos")
# VIDEOS_BASE_DIR = "videos"

VOICES = {
    "en-IN-NeerjaNeural": "Neerja (Female, Indian English)",
    "en-IN-PrabhatNeural": "Prabhat (Male, Indian English)",
}


# -------------------------------------------------
# API HELPER FUNCTIONS (FIXED)
# -------------------------------------------------
@st.cache_data(ttl=300)
def fetch_services_from_api() -> List[Dict]:
    """Fetch all services from the API"""
    try:
        response = requests.get(f"{API_BASE_URL}/services/", timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching services: {e}")
        return []


def get_service_by_id(service_id: int) -> Optional[Dict]:
    """Fetch a specific service by ID"""
    try:
        response = requests.get(f"{API_BASE_URL}/services/{service_id}", timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching service details: {e}")
        return None


def create_video_record(
    service_id: int, service_name: str, video_version: int, source_type: str
) -> tuple[bool, str]:
    try:
        payload = {
            "service_id": service_id,
            "service_name": service_name,
            "video_version": video_version,
            "source_type": source_type,
            "is_new": True,
        }

        logging.info(f"🔄 Sending to API: {payload}")

        response = requests.post(
            f"{API_BASE_URL}/service_videos/", json=payload, timeout=10
        )

        logging.info(f"📡 Status Code: {response.status_code}")
        logging.info(f"📡 Response Body: {response.text}")  # <-- ADD THIS

        response.raise_for_status()

        response_data = response.json()
        logging.info(f"✅ Parsed Response: {response_data}")

        return True, f"Database record created successfully"

    except Exception as e:
        logging.error(f"❌ Error: {str(e)}")
        return False, str(e)


def mark_videos_as_old(service_id: int, exclude_version: int = None) -> bool:
    """Mark all videos except the specified version as old"""
    try:
        params = {"exclude_version": exclude_version} if exclude_version else {}
        response = requests.patch(
            f"{API_BASE_URL}/service_videos/{service_id}/mark_old",
            params=params,
            timeout=10,
        )
        response.raise_for_status()
        return True
    except Exception as e:
        logging.warning(f"Error marking videos as old: {e}")
        return False


# -------------------------------------------------
# VIDEO VERSION MANAGEMENT
# -------------------------------------------------
def get_next_version_number(service_id: int) -> int:
    """Get the next version number for a service"""
    service_dir = os.path.join(VIDEOS_BASE_DIR, str(service_id))

    if not os.path.exists(service_dir):
        return 1

    video_files = [f for f in os.listdir(service_dir) if f.endswith(".mp4")]
    versions = []

    for video_file in video_files:
        try:
            version_part = video_file.split("_v")[-1].replace(".mp4", "")
            versions.append(int(version_part))
        except ValueError:
            continue

    return max(versions) + 1 if versions else 1


def save_video_with_version(
    video_source: str,
    service_id: int,
    service_name: str,
    source_type: str,
    is_upload: bool = False,
) -> tuple:
    """
    Save video with proper versioning
    Returns: (video_path, version, db_success, db_message)
    """
    service_dir = os.path.join(VIDEOS_BASE_DIR, str(service_id))
    os.makedirs(service_dir, exist_ok=True)

    version = get_next_version_number(service_id)
    safe_service_name = service_name.replace(" ", "_").replace("/", "-")
    filename = f"{safe_service_name}_v{version}.mp4"
    video_path = os.path.join(service_dir, filename)

    # Save video file
    if is_upload:
        shutil.copy2(video_source, video_path)
    else:
        shutil.move(video_source, video_path)

    logging.info(f"Video saved to: {video_path}")

    # Create database record
    db_success, db_message = create_video_record(
        service_id, service_name, version, source_type
    )

    # Mark old videos (only if DB record was successful)
    if db_success:
        mark_videos_as_old(service_id, exclude_version=version)

    return video_path, version, db_success, db_message


def get_service_video_list(service_id: int) -> List[Dict]:
    """Get list of all video versions for a service"""
    service_dir = os.path.join(VIDEOS_BASE_DIR, str(service_id))

    if not os.path.exists(service_dir):
        return []

    videos = []
    video_files = sorted(
        [f for f in os.listdir(service_dir) if f.endswith(".mp4")], reverse=True
    )

    for video_file in video_files:
        try:
            version = int(video_file.split("_v")[-1].replace(".mp4", ""))
            video_path = os.path.join(service_dir, video_file)

            videos.append(
                {
                    "filename": video_file,
                    "path": video_path,
                    "version": version,
                    "size_mb": os.path.getsize(video_path) / (1024 * 1024),
                    "created": datetime.fromtimestamp(os.path.getctime(video_path)),
                }
            )
        except (ValueError, IndexError):
            continue

    return videos


# -------------------------------------------------
# VIDEO GENERATION LOGIC
# -------------------------------------------------
def generate_video_from_content(
    selected_voice: str,
    service_id: int,
    service_name: str,
    uploaded_pdf: Optional[st.runtime.uploaded_file_manager.UploadedFile],
    service_content: Optional[Dict],
    source_type: str,
):
    """Generate training video from either PDF or form content"""
    try:
        progress = st.progress(0)
        status = st.empty()

        video_clips = []
        audio_paths = []

        # Process PDF
        if uploaded_pdf:
            status.text("📄 Extracting content from PDF...")
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(uploaded_pdf.read())
                pdf_path = tmp.name
            pages = extract_raw_content(pdf_path)
            raw_text = "\n".join(line for page in pages for line in page["lines"])

        # Process form content
        else:
            valid, msg = validate_service_content(service_content)
            if not valid:
                st.error(msg)
                return

            status.text("📄 Generating training PDF from form...")
            pdf_path = generate_service_pdf(service_content)

            with open(pdf_path, "rb") as f:
                st.download_button(
                    "📥 Download Training PDF",
                    data=f.read(),
                    file_name=os.path.basename(pdf_path),
                    mime="application/pdf",
                )

            pages = extract_raw_content(pdf_path)
            raw_text = "\n".join(line for page in pages for line in page["lines"])

        # Generate slides using AI
        status.text("🧠 Structuring training slides using AI...")
        slides_response = generate_slides_from_raw(raw_text)
        slides = slides_response["slides"]

        # Create video slides
        for i, slide in enumerate(slides):
            status.text(f"🎬 Creating slide {i + 1}/{len(slides)}")

            narration = " ".join(slide["bullets"])
            audio = asyncio.run(text_to_speech(narration, voice=selected_voice))
            audio_paths.append(audio)

            try:
                image = fetch_and_save_photo(slide["image_keyword"])
            except Exception:
                image = os.path.join("assets", "default_background.jpg")

            clip = create_slide(slide["title"], slide["bullets"], image, audio)
            clip = add_avatar_to_slide(clip, audio_duration=clip.duration)
            video_clips.append(clip)
            progress.progress(int((i + 1) / len(slides) * 80))

        status.text("🎞️ Rendering final video...")

        temp_final_path = combine_slides_and_audio(
            video_clips, audio_paths, service_name=f"{service_name}_temp"
        )

        video_path, version, db_success, db_message = save_video_with_version(
            video_source=temp_final_path,
            service_id=service_id,
            service_name=service_name,
            source_type=source_type,
            is_upload=False,
        )

        progress.progress(100)
        st.session_state["video_path"] = video_path
        st.session_state["video_version"] = version
        st.session_state["audio_paths"] = audio_paths
        st.session_state["db_success"] = db_success
        st.session_state["db_message"] = db_message

        status.empty()
        progress.empty()

        if db_success:
            st.success(
                f"✅ Training video generated successfully as version {version}!"
            )
            st.success(f"✅ {db_message}")
        else:
            st.success(f"✅ Video file saved as version {version}")
            st.error(f"⚠️ Database record failed: {db_message}")
            st.info(
                "💡 The video file is saved locally, but not recorded in the database. Check your API connection."
            )

        st.balloons()

    except Exception as e:
        st.error(f"❌ Error generating video: {e}")
        logging.exception("Video generation error")


# -------------------------------------------------
# MAIN UI
# -------------------------------------------------
st.markdown(
    """
<div class="video-header">
    <h1 style="margin: 0;">🎥 BSK Training Video Generator</h1>
    <p style="margin: 0.5rem 0 0 0;">Create professional training videos for data entry operators</p>
</div>
""",
    unsafe_allow_html=True,
)

# Sidebar
with st.sidebar:
    st.markdown("### 🎙️ Voice Settings")
    voice_keys = list(VOICES.keys())
    voice_labels = list(VOICES.values())
    voice_index = st.selectbox(
        "Select Narrator Voice",
        range(len(voice_keys)),
        format_func=lambda i: voice_labels[i],
    )
    selected_voice = voice_keys[voice_index]

    st.markdown("---")
    st.markdown("### 🎬 Video Generation")
    st.info("Choose a service and content source to create training videos")

    st.markdown("---")
    page_mode = st.radio(
        "Page Mode",
        ["🔹 Create New Video", "📂 Manage Videos"],
        label_visibility="collapsed",
    )

# Create Video Mode
if page_mode == "🔹 Create New Video":
    services = fetch_services_from_api()

    if not services:
        st.warning("⚠️ Unable to fetch services from API")
        st.stop()

    service_options = {
        f"{s['service_name']} (ID: {s['service_id']})": s["service_id"]
        for s in services
    }
    service_names = list(service_options.keys())

    # Service Selection
    st.markdown("## 📋 Select Service")

    col1, col2, col3 = st.columns([3, 1, 2])

    with col1:
        selected_service_display = st.selectbox(
            "Search and Select Service",
            options=service_names,
            help="Type to search for a service",
        )

    with col2:
        selected_service_id = service_options[selected_service_display]
        st.metric("Service ID", selected_service_id)

    with col3:
        existing_videos = get_service_video_list(selected_service_id)
        if existing_videos:
            latest_version = existing_videos[0]["version"]
            st.markdown(
                f'<div class="version-badge">Latest: v{latest_version} ({len(existing_videos)} total)</div>',
                unsafe_allow_html=True,
            )
        else:
            st.info("No existing videos")

    service_details = get_service_by_id(selected_service_id)

    if service_details:
        with st.expander("📖 View Service Details", expanded=False):
            st.json(service_details)

    # Show existing versions
    if existing_videos:
        with st.expander(
            f"🎬 Existing Versions ({len(existing_videos)})", expanded=False
        ):
            for video in existing_videos:
                col_a, col_b, col_c, col_d = st.columns([2, 1, 1, 1])
                with col_a:
                    st.text(f"v{video['version']} - {video['filename']}")
                with col_b:
                    st.text(f"{video['size_mb']:.2f} MB")
                with col_c:
                    st.text(video["created"].strftime("%Y-%m-%d"))
                with col_d:
                    if st.button("👁️ Preview", key=f"view_{video['version']}"):
                        st.session_state["preview_video_path"] = video["path"]
                        st.session_state["preview_video_version"] = video["version"]

    st.markdown("---")

    # Content Source Selection
    st.markdown("## 📄 Choose Content Source")

    content_source = st.radio(
        "How would you like to provide training content?",
        ["📝 Manual Form Entry", "📄 Upload PDF", "🎥 Upload Existing Video"],
        horizontal=True,
        key="content_source_radio",
    )

    st.markdown("---")

    # Upload Existing Video
    if content_source == "🎥 Upload Existing Video":
        st.markdown('<div class="service-card">', unsafe_allow_html=True)
        st.subheader("📤 Upload Training Video")

        uploaded_video = st.file_uploader(
            "Upload your pre-recorded training video",
            type=["mp4", "mov", "avi"],
            help="Upload an existing training video for this service",
            key="video_uploader",
        )

        # Show preview if video is selected
        if uploaded_video:
            st.video(uploaded_video)
            
            col1, col2 = st.columns([1, 4])
            with col1:
                upload_button = st.button("📤 Upload Video", type="primary", key="upload_video_btn")
            with col2:
                if st.button("🔄 Choose Different Video"):
                    st.rerun()
            
            # Only process when button is clicked
            if upload_button:
                with st.spinner("Uploading video..."):
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
                        tmp.write(uploaded_video.read())
                        temp_path = tmp.name

                    video_path, version, db_success, db_message = save_video_with_version(
                        video_source=temp_path,
                        service_id=selected_service_id,
                        service_name=service_details["service_name"],
                        source_type="uploaded",
                        is_upload=True,
                    )

                    os.remove(temp_path)

                    # Show status
                    if db_success:
                        st.markdown(
                            f"""
                        <div class="success-box">
                            <strong>✅ Upload Successful!</strong><br>
                            • Video saved as version {version}<br>
                            • Database record created<br>
                            • {db_message}
                        </div>
                        """,
                            unsafe_allow_html=True,
                        )
                    else:
                        st.markdown(
                            f"""
                        <div class="error-box">
                            <strong>⚠️ Partial Success</strong><br>
                            • Video file saved as version {version}<br>
                            • Database record failed: {db_message}<br>
                            • Check API connection and try again
                        </div>
                        """,
                            unsafe_allow_html=True,
                        )

                    st.video(video_path)

                    with open(video_path, "rb") as f:
                        st.download_button(
                            "📥 Download Video",
                            data=f.read(),
                            file_name=os.path.basename(video_path),
                            mime="video/mp4",
                        )

                    if st.button("🔄 Upload Another", key="upload_another_btn"):
                        st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    # PDF Upload
    elif content_source == "📄 Upload PDF":
        st.markdown('<div class="service-card">', unsafe_allow_html=True)
        st.subheader("📄 Upload Training PDF")

        uploaded_pdf = st.file_uploader(
            "Upload PDF document",
            type=["pdf"],
            help="PDF content will be used to generate the training video",
            key="pdf_uploader",
        )

        if uploaded_pdf and st.button("🚀 Generate Video from PDF", type="primary"):
            generate_video_from_content(
                selected_voice=selected_voice,
                service_id=selected_service_id,
                service_name=service_details["service_name"],
                uploaded_pdf=uploaded_pdf,
                service_content=None,
                source_type="pdf_generated",
            )
        st.markdown("</div>", unsafe_allow_html=True)

    # Manual Form Entry
    else:
        st.markdown('<div class="service-card">', unsafe_allow_html=True)
        with st.form("service_form"):
            st.subheader("📋 Service Training Information")

            col1, col2 = st.columns(2)

            with col1:
                service_description = st.text_area("Service Description *", height=100)
                how_to_apply = st.text_area(
                    "Step-by-Step Application Process *", height=100
                )

            with col2:
                eligibility_criteria = st.text_area(
                    "Eligibility Criteria *", height=100
                )
                required_docs = st.text_area("Required Documents *", height=100)

            st.subheader("🎯 Training Specific Information")
            col3, col4 = st.columns(2)

            with col3:
                operator_tips = st.text_area("Operator Tips", height=100)
                service_link = st.text_input("Official Service Link")

            with col4:
                troubleshooting = st.text_area("Common Issues", height=100)
                fees_and_timeline = st.text_input("Fees & Processing Time")

            submitted = st.form_submit_button(
                "🚀 Generate Training Video", type="primary"
            )

        if submitted:
            service_content = {
                "service_name": service_details["service_name"],
                "service_id": selected_service_id,
                "service_description": service_description,
                "how_to_apply": how_to_apply,
                "eligibility_criteria": eligibility_criteria,
                "required_docs": required_docs,
                "operator_tips": operator_tips,
                "troubleshooting": troubleshooting,
                "service_link": service_link,
                "fees_and_timeline": fees_and_timeline,
            }

            generate_video_from_content(
                selected_voice=selected_voice,
                service_id=selected_service_id,
                service_name=service_details["service_name"],
                uploaded_pdf=None,
                service_content=service_content,
                source_type="form_generated",
            )
        st.markdown("</div>", unsafe_allow_html=True)

    # Display Result (ONLY for generated videos, not uploads)
    if (
        "video_path" in st.session_state
        and content_source != "🎥 Upload Existing Video"
    ):
        st.markdown("---")
        st.markdown('<div class="video-preview">', unsafe_allow_html=True)
        st.subheader("🎬 Generated Training Video")

        if st.session_state.get("db_success"):
            st.success(
                f"✅ Video saved as version {st.session_state.get('video_version', 'N/A')}"
            )
            st.success(f"✅ {st.session_state.get('db_message', '')}")
        else:
            st.warning(f"⚠️ Video saved locally but database record failed")
            st.error(st.session_state.get("db_message", "Unknown error"))

        with open(st.session_state["video_path"], "rb") as f:
            st.video(f.read())

        st.download_button(
            "📥 Download Video",
            data=open(st.session_state["video_path"], "rb").read(),
            file_name=os.path.basename(st.session_state["video_path"]),
            mime="video/mp4",
        )

        if st.button("🔄 Generate New"):
            # Clear only generation-related session state
            for key in [
                "video_path",
                "video_version",
                "audio_paths",
                "db_success",
                "db_message",
            ]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # Preview (ONLY show when explicitly clicked from existing versions)
    if (
        "preview_video_path" in st.session_state
        and content_source == "🎥 Upload Existing Video"
    ):
        st.markdown("---")
        st.markdown('<div class="video-preview">', unsafe_allow_html=True)
        st.subheader(
            f"👁️ Preview - Version {st.session_state.get('preview_video_version', 'N/A')}"
        )
        with open(st.session_state["preview_video_path"], "rb") as f:
            st.video(f.read())

        if st.button("❌ Close Preview"):
            del st.session_state["preview_video_path"]
            if "preview_video_version" in st.session_state:
                del st.session_state["preview_video_version"]
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# Manage Videos Mode
else:
    st.markdown("## 📂 Video Library Management")

    if not os.path.exists(VIDEOS_BASE_DIR):
        st.info("No videos found in library")
        st.stop()

    service_dirs = [
        d
        for d in os.listdir(VIDEOS_BASE_DIR)
        if os.path.isdir(os.path.join(VIDEOS_BASE_DIR, d))
    ]

    if not service_dirs:
        st.info("No videos available")
        st.stop()

    services = fetch_services_from_api()
    service_map = {s["service_id"]: s["service_name"] for s in services}

    st.subheader(f"🎬 Videos for {len(service_dirs)} services")

    for service_id in sorted(service_dirs, key=lambda x: int(x)):
        service_id_int = int(service_id)
        service_name = service_map.get(service_id_int, f"Service {service_id}")

        videos = get_service_video_list(service_id_int)

        with st.expander(
            f"🎬 {service_name} (ID: {service_id}) - {len(videos)} versions",
            expanded=False,
        ):
            if not videos:
                st.info("No videos found")
                continue

            for video in videos:
                col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 1])

                with col1:
                    st.text(f"Version {video['version']}")

                with col2:
                    st.text(f"{video['size_mb']:.2f} MB")

                with col3:
                    st.text(video["created"].strftime("%Y-%m-%d"))

                with col4:
                    with open(video["path"], "rb") as f:
                        st.download_button(
                            "📥",
                            data=f.read(),
                            file_name=video["filename"],
                            mime="video/mp4",
                            key=f"dl_{service_id}_{video['version']}",
                        )

                with col5:
                    if st.button("🗑️", key=f"del_{service_id}_{video['version']}"):
                        os.remove(video["path"])
                        st.success(f"Deleted version {video['version']}")
                        st.rerun()

                with st.container():
                    with open(video["path"], "rb") as f:
                        st.video(f.read())

                st.markdown("---")
