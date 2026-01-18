# import streamlit as st
# import asyncio
# import logging
# import os
# import tempfile
# import requests
# from typing import Optional, List, Dict

# from utils.service_utils import create_service_sections, validate_service_content
# from utils.audio_utils import text_to_speech
# from utils.video_utils import create_slide, combine_slides_and_audio
# from services.unsplash_service import fetch_and_save_photo
# from services.gemini_service import generate_slides_from_raw
# from utils.avatar_utils import add_avatar_to_slide
# from utils.pdf_extractor import extract_raw_content
# from utils.pdf_utils import generate_service_pdf
# from moviepy.config import change_settings

# change_settings(
#     {"IMAGEMAGICK_BINARY": r"C:\Program Files\ImageMagick-7.1.2-Q16-HDRI\magick.exe"}
# )

# logging.basicConfig(level=logging.INFO)

# # API Configuration
# API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:54300")

# VOICES = {
#     "en-IN-NeerjaNeural": "Neerja (Female, Indian English)",
#     "en-IN-PrabhatNeural": "Prabhat (Male, Indian English)",
# }


# # -------------------------------------------------
# # API HELPER FUNCTIONS
# # -------------------------------------------------
# @st.cache_data(ttl=300)  # Cache for 5 minutes
# def fetch_services_from_api() -> List[Dict]:
#     """Fetch all services from the API"""
#     try:
#         response = requests.get(f"{API_BASE_URL}/services/")
#         response.raise_for_status()
#         return response.json()
#     except Exception as e:
#         st.error(f"Error fetching services from API: {e}")
#         return []


# def get_service_by_id(service_id: int) -> Optional[Dict]:
#     """Fetch a specific service by ID"""
#     try:
#         response = requests.get(f"{API_BASE_URL}/services/{service_id}")
#         response.raise_for_status()
#         return response.json()
#     except Exception as e:
#         st.error(f"Error fetching service details: {e}")
#         return None


# # -------------------------------------------------
# # MAIN
# # -------------------------------------------------
# def main():
#     st.set_page_config(
#         page_title="BSK Training Video Generator",
#         page_icon="🎥",
#         layout="wide",
#         initial_sidebar_state="expanded",
#     )

#     # Load CSS
#     css_path = os.path.join("assets", "style.css")
#     if os.path.exists(css_path):
#         with open(css_path) as f:
#             st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

#     # ---------------- SIDEBAR ----------------
#     with st.sidebar:
#         st.markdown("### 🎥 BSK Training Generator")
#         st.markdown("**Professional Training Videos**")
#         st.markdown("*Bangla Sahayta Kendra*")
#         st.markdown("---")

#         page = st.selectbox(
#             "Select Page:",
#             ["🎬 Create New Video", "📂 View Existing Videos"],
#             key="page_selector",
#         )

#         st.markdown("---")

#         voice_keys = list(VOICES.keys())
#         voice_labels = list(VOICES.values())
#         voice_index = st.selectbox(
#             "Select Narrator Voice:",
#             range(len(voice_keys)),
#             format_func=lambda i: voice_labels[i],
#         )
#         selected_voice = voice_keys[voice_index]

#         st.markdown("---")
#         st.markdown("### 🧑‍🏫 AI Avatar")
#         st.caption("Avatar will appear inside the generated training video.")

#     # ---------------- ROUTING ----------------
#     if page == "🎬 Create New Video":
#         show_create_video_page(selected_voice)
#     else:
#         show_existing_videos_page()


# # -------------------------------------------------
# # CREATE VIDEO PAGE
# # -------------------------------------------------
# def show_create_video_page(selected_voice):
#     st.title("🎥 BSK Training Video Generator")
#     st.markdown("**Create training videos for BSK data entry operators**")
#     st.markdown("---")

#     # Fetch services from API
#     services = fetch_services_from_api()
    
#     if not services:
#         st.warning("⚠️ Unable to fetch services from API. Please check your connection.")
#         return

#     # Create service lookup dictionaries
#     service_options = {
#         f"{s['service_name']} (ID: {s['service_id']})": s['service_id'] 
#         for s in services
#     }
#     service_names = list(service_options.keys())

#     # ---------------- SERVICE SELECTION ----------------
#     st.subheader("📋 Select Service")
    
#     col1, col2 = st.columns([3, 1])
    
#     with col1:
#         selected_service_display = st.selectbox(
#             "Search and Select Service",
#             options=service_names,
#             help="Type to search for a service"
#         )
    
#     with col2:
#         selected_service_id = service_options[selected_service_display]
#         st.metric("Service ID", selected_service_id)

#     # Get full service details
#     service_details = get_service_by_id(selected_service_id)
    
#     if service_details:
#         with st.expander("📖 View Service Details", expanded=False):
#             st.json(service_details)

#     st.markdown("---")

#     # ---------------- CONTENT SOURCE SELECTION ----------------
#     st.subheader("📄 Choose Content Source")
    
#     content_source = st.radio(
#         "How would you like to provide training content?",
#         ["📝 Manual Form Entry", "📄 Upload PDF", "🎥 Upload Existing Video"],
#         horizontal=True
#     )

#     st.markdown("---")

#     # ---------------- UPLOAD EXISTING VIDEO ----------------
#     if content_source == "🎥 Upload Existing Video":
#         st.subheader("📤 Upload Training Video")
        
#         uploaded_video = st.file_uploader(
#             "Upload your pre-recorded training video",
#             type=["mp4", "mov", "avi"],
#             help="Upload an existing training video for this service"
#         )
        
#         if uploaded_video:
#             # Save uploaded video
#             output_dir = "output_videos"
#             os.makedirs(output_dir, exist_ok=True)
            
#             safe_service_name = service_details['service_name'].replace(" ", "_")
#             video_filename = f"{safe_service_name}_training.mp4"
#             video_path = os.path.join(output_dir, video_filename)
            
#             with open(video_path, "wb") as f:
#                 f.write(uploaded_video.read())
            
#             st.success(f"✅ Video uploaded successfully: {video_filename}")
            
#             # Display uploaded video
#             st.video(video_path)
            
#             # Download button
#             with open(video_path, "rb") as f:
#                 st.download_button(
#                     "📥 Download Video",
#                     data=f.read(),
#                     file_name=video_filename,
#                     mime="video/mp4",
#                 )
            
#             if st.button("🔄 Upload Another"):
#                 st.rerun()
        
#         return  # Exit early for upload mode

#     # ---------------- PDF UPLOAD ----------------
#     elif content_source == "📄 Upload PDF":
#         st.subheader("📄 Upload Training PDF")
        
#         uploaded_pdf = st.file_uploader(
#             "Upload PDF document",
#             type=["pdf"],
#             help="PDF content will be used to generate the training video"
#         )
        
#         if uploaded_pdf and st.button("🚀 Generate Video from PDF"):
#             generate_video_from_content(
#                 selected_voice=selected_voice,
#                 service_name=service_details['service_name'],
#                 service_id=selected_service_id,
#                 uploaded_pdf=uploaded_pdf,
#                 service_content=None
#             )

#     # ---------------- MANUAL FORM ENTRY ----------------
#     else:  # Manual Form Entry
#         with st.form("service_form"):
#             st.subheader("📋 Service Training Information")

#             col1, col2 = st.columns(2)

#             with col1:
#                 service_description = st.text_area("Service Description *", height=100)
#                 how_to_apply = st.text_area(
#                     "Step-by-Step Application Process *", height=100
#                 )

#             with col2:
#                 eligibility_criteria = st.text_area("Eligibility Criteria *", height=100)
#                 required_docs = st.text_area("Required Documents *", height=100)

#             st.subheader("🎯 Training Specific Information")
#             col3, col4 = st.columns(2)

#             with col3:
#                 operator_tips = st.text_area("Operator Tips", height=100)
#                 service_link = st.text_input("Official Service Link")

#             with col4:
#                 troubleshooting = st.text_area("Common Issues", height=100)
#                 fees_and_timeline = st.text_input("Fees & Processing Time")

#             submitted = st.form_submit_button("🚀 Generate Training Video")

#         if submitted:
#             service_content = {
#                 "service_name": service_details['service_name'],
#                 "service_id": selected_service_id,
#                 "service_description": service_description,
#                 "how_to_apply": how_to_apply,
#                 "eligibility_criteria": eligibility_criteria,
#                 "required_docs": required_docs,
#                 "operator_tips": operator_tips,
#                 "troubleshooting": troubleshooting,
#                 "service_link": service_link,
#                 "fees_and_timeline": fees_and_timeline,
#             }
            
#             generate_video_from_content(
#                 selected_voice=selected_voice,
#                 service_name=service_details['service_name'],
#                 service_id=selected_service_id,
#                 uploaded_pdf=None,
#                 service_content=service_content
#             )

#     # ---------------- DISPLAY RESULT ----------------
#     if "video_path" in st.session_state:
#         st.markdown("---")
#         st.subheader("🎬 Generated Training Video")

#         with open(st.session_state["video_path"], "rb") as f:
#             st.video(f.read())

#         st.download_button(
#             "📥 Download Video",
#             data=open(st.session_state["video_path"], "rb").read(),
#             file_name=os.path.basename(st.session_state["video_path"]),
#             mime="video/mp4",
#         )

#         if st.button("🔄 Generate New"):
#             st.session_state.clear()
#             st.rerun()


# # -------------------------------------------------
# # VIDEO GENERATION LOGIC
# # -------------------------------------------------
# def generate_video_from_content(
#     selected_voice: str,
#     service_name: str,
#     service_id: int,
#     uploaded_pdf: Optional[st.runtime.uploaded_file_manager.UploadedFile],
#     service_content: Optional[Dict]
# ):
#     """Generate training video from either PDF or form content"""
#     try:
#         progress = st.progress(0)
#         status = st.empty()

#         video_clips = []
#         audio_paths = []

#         # ==================================================
#         # CASE 1: PDF EXISTS
#         # ==================================================
#         if uploaded_pdf:
#             status.text("📄 Extracting content from PDF...")

#             with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
#                 tmp.write(uploaded_pdf.read())
#                 pdf_path = tmp.name

#             pages = extract_raw_content(pdf_path)
#             raw_text = "\n".join(line for page in pages for line in page["lines"])

#         # ==================================================
#         # CASE 2: FORM CONTENT
#         # ==================================================
#         else:
#             valid, msg = validate_service_content(service_content)
#             if not valid:
#                 st.error(msg)
#                 return

#             # Generate PDF from form
#             status.text("📄 Generating training PDF from form...")
#             pdf_path = generate_service_pdf(service_content)

#             # Show download button
#             with open(pdf_path, "rb") as f:
#                 st.download_button(
#                     "📥 Download Training PDF",
#                     data=f.read(),
#                     file_name=os.path.basename(pdf_path),
#                     mime="application/pdf",
#                 )

#             # Extract text from the saved PDF
#             pages = extract_raw_content(pdf_path)
#             raw_text = "\n".join(line for page in pages for line in page["lines"])

#         # ==================================================
#         # GEMINI → SLIDES
#         # ==================================================
#         status.text("🧠 Structuring training slides using AI...")
#         slides_response = generate_slides_from_raw(raw_text)
#         slides = slides_response["slides"]

#         # ==================================================
#         # VIDEO PIPELINE
#         # ==================================================
#         for i, slide in enumerate(slides):
#             status.text(f"🎬 Creating slide {i + 1}/{len(slides)}")

#             narration = " ".join(slide["bullets"])
#             audio = asyncio.run(text_to_speech(narration, voice=selected_voice))
#             audio_paths.append(audio)

#             try:
#                 image = fetch_and_save_photo(slide["image_keyword"])
#             except Exception:
#                 image = os.path.join("assets", "default_background.jpg")

#             clip = create_slide(slide["title"], slide["bullets"], image, audio)
#             clip = add_avatar_to_slide(clip, audio_duration=clip.duration)
#             video_clips.append(clip)
#             progress.progress(int((i + 1) / len(slides) * 80))

#         status.text("🎞️ Rendering final video...")
#         final_path = combine_slides_and_audio(
#             video_clips, 
#             audio_paths, 
#             service_name=f"{service_name}_ID{service_id}"
#         )

#         progress.progress(100)
#         st.session_state["video_path"] = final_path
#         st.session_state["audio_paths"] = audio_paths

#         status.empty()
#         progress.empty()

#         st.success("✅ Training video generated successfully!")
#         st.balloons()

#     except Exception as e:
#         st.error(f"❌ Error generating video: {e}")
#         logging.exception("Video generation error")


# # -------------------------------------------------
# # EXISTING VIDEOS PAGE
# # -------------------------------------------------
# def show_existing_videos_page():
#     st.title("📂 Existing Training Videos")
#     st.markdown("---")

#     output_dir = "output_videos"
#     if not os.path.exists(output_dir):
#         st.info("No videos found.")
#         return

#     videos = [f for f in os.listdir(output_dir) if f.endswith(".mp4")]
#     if not videos:
#         st.info("No videos available.")
#         return

#     # Group videos by service if possible
#     st.subheader(f"📹 Found {len(videos)} training videos")
    
#     selected = st.selectbox("Select a video:", videos)
#     path = os.path.join(output_dir, selected)

#     col1, col2 = st.columns([3, 1])
    
#     with col1:
#         with open(path, "rb") as f:
#             st.video(f.read())
    
#     with col2:
#         st.metric("File Size", f"{os.path.getsize(path) / (1024*1024):.2f} MB")
        
#         with open(path, "rb") as f:
#             st.download_button(
#                 "📥 Download",
#                 data=f.read(),
#                 file_name=selected,
#                 mime="video/mp4",
#                 use_container_width=True
#             )
        
#         if st.button("🗑️ Delete", use_container_width=True):
#             os.remove(path)
#             st.success(f"Deleted {selected}")
#             st.rerun()


# # -------------------------------------------------
# # RUN
# # -------------------------------------------------
# if __name__ == "__main__":
#     main()



###################################################


import streamlit as st
import asyncio
import logging
import os
import tempfile
import requests
from typing import Optional, List, Dict
from datetime import datetime
import shutil

from utils.service_utils import create_service_sections, validate_service_content
from utils.audio_utils import text_to_speech
from utils.video_utils import create_slide, combine_slides_and_audio
from services.unsplash_service import fetch_and_save_photo
from services.gemini_service import generate_slides_from_raw
from utils.avatar_utils import add_avatar_to_slide
from utils.pdf_extractor import extract_raw_content
from utils.pdf_utils import generate_service_pdf
from moviepy.config import change_settings

change_settings(
    {"IMAGEMAGICK_BINARY": r"C:\Program Files\ImageMagick-7.1.2-Q16-HDRI\magick.exe"}
)

logging.basicConfig(level=logging.INFO)

# API Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:54300")
VIDEOS_BASE_DIR = "videos"

VOICES = {
    "en-IN-NeerjaNeural": "Neerja (Female, Indian English)",
    "en-IN-PrabhatNeural": "Prabhat (Male, Indian English)",
}


# -------------------------------------------------
# API HELPER FUNCTIONS
# -------------------------------------------------
@st.cache_data(ttl=300)
def fetch_services_from_api() -> List[Dict]:
    """Fetch all services from the API"""
    try:
        response = requests.get(f"{API_BASE_URL}/services/")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching services from API: {e}")
        return []


def get_service_by_id(service_id: int) -> Optional[Dict]:
    """Fetch a specific service by ID"""
    try:
        response = requests.get(f"{API_BASE_URL}/services/{service_id}")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching service details: {e}")
        return None


def get_service_videos(service_id: int) -> List[Dict]:
    """Fetch all videos for a specific service"""
    try:
        response = requests.get(f"{API_BASE_URL}/service_videos/{service_id}")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logging.warning(f"No videos found for service {service_id}: {e}")
        return []


def create_video_record(service_id: int, service_name: str, video_version: int, source_type: str) -> bool:
    """Create a new video record in the database"""
    try:
        payload = {
            "service_id": service_id,
            "service_name": service_name,
            "video_version": video_version,
            "source_type": source_type,
            "is_new": True
        }
        response = requests.post(f"{API_BASE_URL}/service_videos/", json=payload)
        response.raise_for_status()
        return True
    except Exception as e:
        st.error(f"Error creating video record: {e}")
        return False


def update_video_record(service_id: int, video_version: int) -> bool:
    """Update existing video record"""
    try:
        payload = {
            "updated_at": datetime.now().isoformat(),
            "is_new": True
        }
        response = requests.put(
            f"{API_BASE_URL}/service_videos/{service_id}/{video_version}",
            json=payload
        )
        response.raise_for_status()
        return True
    except Exception as e:
        st.error(f"Error updating video record: {e}")
        return False


def mark_videos_as_old(service_id: int, exclude_version: int = None) -> bool:
    """Mark all videos except the specified version as old"""
    try:
        params = {"exclude_version": exclude_version} if exclude_version else {}
        response = requests.patch(
            f"{API_BASE_URL}/service_videos/{service_id}/mark_old",
            params=params
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
    
    # Get all video files and extract version numbers
    video_files = [f for f in os.listdir(service_dir) if f.endswith('.mp4')]
    versions = []
    
    for video_file in video_files:
        try:
            # Extract version from filename: <service_name>_v<version>.mp4
            version_part = video_file.split('_v')[-1].replace('.mp4', '')
            versions.append(int(version_part))
        except ValueError:
            continue
    
    return max(versions) + 1 if versions else 1


def save_video_with_version(
    video_source: str,
    service_id: int,
    service_name: str,
    source_type: str,
    is_upload: bool = False
) -> tuple[str, int]:
    """
    Save video with proper versioning structure
    
    Returns:
        tuple: (video_path, version_number)
    """
    # Create service directory
    service_dir = os.path.join(VIDEOS_BASE_DIR, str(service_id))
    os.makedirs(service_dir, exist_ok=True)
    
    # Get next version number
    version = get_next_version_number(service_id)
    
    # Create filename
    safe_service_name = service_name.replace(" ", "_").replace("/", "-")
    filename = f"{safe_service_name}_v{version}.mp4"
    video_path = os.path.join(service_dir, filename)
    
    # Copy or move the video file
    if is_upload:
        shutil.copy2(video_source, video_path)
    else:
        shutil.move(video_source, video_path)
    
    # Create/update database record
    create_video_record(service_id, service_name, version, source_type)
    
    # Mark all previous versions as old
    mark_videos_as_old(service_id, exclude_version=version)
    
    logging.info(f"Video saved: {video_path} (version {version})")
    return video_path, version


def get_service_video_list(service_id: int) -> List[Dict]:
    """Get list of all video versions for a service"""
    service_dir = os.path.join(VIDEOS_BASE_DIR, str(service_id))
    
    if not os.path.exists(service_dir):
        return []
    
    videos = []
    video_files = sorted(
        [f for f in os.listdir(service_dir) if f.endswith('.mp4')],
        reverse=True  # Latest first
    )
    
    for video_file in video_files:
        try:
            version = int(video_file.split('_v')[-1].replace('.mp4', ''))
            video_path = os.path.join(service_dir, video_file)
            
            videos.append({
                'filename': video_file,
                'path': video_path,
                'version': version,
                'size_mb': os.path.getsize(video_path) / (1024 * 1024),
                'created': datetime.fromtimestamp(os.path.getctime(video_path))
            })
        except (ValueError, IndexError):
            continue
    
    return videos


# -------------------------------------------------
# MAIN
# -------------------------------------------------
def main():
    st.set_page_config(
        page_title="BSK Training Video Generator",
        page_icon="🎥",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Load CSS
    css_path = os.path.join("assets", "style.css")
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    # ---------------- SIDEBAR ----------------
    with st.sidebar:
        st.markdown("### 🎥 BSK Training Generator")
        st.markdown("**Professional Training Videos**")
        st.markdown("*Bangla Sahayta Kendra*")
        st.markdown("---")

        page = st.selectbox(
            "Select Page:",
            ["🎬 Create New Video", "📂 View Existing Videos"],
            key="page_selector",
        )

        st.markdown("---")

        voice_keys = list(VOICES.keys())
        voice_labels = list(VOICES.values())
        voice_index = st.selectbox(
            "Select Narrator Voice:",
            range(len(voice_keys)),
            format_func=lambda i: voice_labels[i],
        )
        selected_voice = voice_keys[voice_index]

        st.markdown("---")
        st.markdown("### 🧑‍🏫 AI Avatar")
        st.caption("Avatar will appear inside the generated training video.")

    # ---------------- ROUTING ----------------
    if page == "🎬 Create New Video":
        show_create_video_page(selected_voice)
    else:
        show_existing_videos_page()


# -------------------------------------------------
# CREATE VIDEO PAGE
# -------------------------------------------------
def show_create_video_page(selected_voice):
    st.title("🎥 BSK Training Video Generator")
    st.markdown("**Create training videos for BSK data entry operators**")
    st.markdown("---")

    # Fetch services from API
    services = fetch_services_from_api()
    
    if not services:
        st.warning("⚠️ Unable to fetch services from API. Please check your connection.")
        return

    # Create service lookup dictionaries
    service_options = {
        f"{s['service_name']} (ID: {s['service_id']})": s['service_id'] 
        for s in services
    }
    service_names = list(service_options.keys())

    # ---------------- SERVICE SELECTION ----------------
    st.subheader("📋 Select Service")
    
    col1, col2, col3 = st.columns([3, 1, 2])
    
    with col1:
        selected_service_display = st.selectbox(
            "Search and Select Service",
            options=service_names,
            help="Type to search for a service"
        )
    
    with col2:
        selected_service_id = service_options[selected_service_display]
        st.metric("Service ID", selected_service_id)
    
    with col3:
        # Show existing versions
        existing_videos = get_service_video_list(selected_service_id)
        if existing_videos:
            latest_version = existing_videos[0]['version']
            st.metric("Latest Version", f"v{latest_version}", delta=f"{len(existing_videos)} total")
        else:
            st.info("No existing videos")

    # Get full service details
    service_details = get_service_by_id(selected_service_id)
    
    if service_details:
        with st.expander("📖 View Service Details", expanded=False):
            st.json(service_details)

    # Show existing video versions
    if existing_videos:
        with st.expander(f"📹 Existing Versions ({len(existing_videos)})", expanded=False):
            for video in existing_videos:
                col_a, col_b, col_c, col_d = st.columns([2, 1, 1, 1])
                with col_a:
                    st.text(video['filename'])
                with col_b:
                    st.text(f"{video['size_mb']:.2f} MB")
                with col_c:
                    st.text(video['created'].strftime('%Y-%m-%d'))
                with col_d:
                    if st.button("👁️ View", key=f"view_{video['version']}"):
                        st.session_state['preview_video'] = video['path']

    st.markdown("---")

    # ---------------- CONTENT SOURCE SELECTION ----------------
    st.subheader("📄 Choose Content Source")
    
    content_source = st.radio(
        "How would you like to provide training content?",
        ["📝 Manual Form Entry", "📄 Upload PDF", "🎥 Upload Existing Video"],
        horizontal=True
    )

    st.markdown("---")

    # ---------------- UPLOAD EXISTING VIDEO ----------------
    if content_source == "🎥 Upload Existing Video":
        st.subheader("📤 Upload Training Video")
        
        uploaded_video = st.file_uploader(
            "Upload your pre-recorded training video",
            type=["mp4", "mov", "avi"],
            help="Upload an existing training video for this service"
        )
        
        if uploaded_video:
            # Save to temporary file first
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
                tmp.write(uploaded_video.read())
                temp_path = tmp.name
            
            # Save with version management
            video_path, version = save_video_with_version(
                video_source=temp_path,
                service_id=selected_service_id,
                service_name=service_details['service_name'],
                source_type="uploaded",
                is_upload=True
            )
            
            # Clean up temp file
            os.remove(temp_path)
            
            st.success(f"✅ Video uploaded successfully as version {version}")
            
            # Display uploaded video
            st.video(video_path)
            
            # Download button
            with open(video_path, "rb") as f:
                st.download_button(
                    "📥 Download Video",
                    data=f.read(),
                    file_name=os.path.basename(video_path),
                    mime="video/mp4",
                )
            
            if st.button("🔄 Upload Another"):
                st.rerun()
        
        return

    # ---------------- PDF UPLOAD ----------------
    elif content_source == "📄 Upload PDF":
        st.subheader("📄 Upload Training PDF")
        
        uploaded_pdf = st.file_uploader(
            "Upload PDF document",
            type=["pdf"],
            help="PDF content will be used to generate the training video"
        )
        
        if uploaded_pdf and st.button("🚀 Generate Video from PDF"):
            generate_video_from_content(
                selected_voice=selected_voice,
                service_id=selected_service_id,
                service_name=service_details['service_name'],
                uploaded_pdf=uploaded_pdf,
                service_content=None,
                source_type="pdf_generated"
            )

    # ---------------- MANUAL FORM ENTRY ----------------
    else:
        with st.form("service_form"):
            st.subheader("📋 Service Training Information")

            col1, col2 = st.columns(2)

            with col1:
                service_description = st.text_area("Service Description *", height=100)
                how_to_apply = st.text_area(
                    "Step-by-Step Application Process *", height=100
                )

            with col2:
                eligibility_criteria = st.text_area("Eligibility Criteria *", height=100)
                required_docs = st.text_area("Required Documents *", height=100)

            st.subheader("🎯 Training Specific Information")
            col3, col4 = st.columns(2)

            with col3:
                operator_tips = st.text_area("Operator Tips", height=100)
                service_link = st.text_input("Official Service Link")

            with col4:
                troubleshooting = st.text_area("Common Issues", height=100)
                fees_and_timeline = st.text_input("Fees & Processing Time")

            submitted = st.form_submit_button("🚀 Generate Training Video")

        if submitted:
            service_content = {
                "service_name": service_details['service_name'],
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
                service_name=service_details['service_name'],
                uploaded_pdf=None,
                service_content=service_content,
                source_type="form_generated"
            )

    # ---------------- DISPLAY RESULT ----------------
    if "video_path" in st.session_state:
        st.markdown("---")
        st.subheader("🎬 Generated Training Video")
        
        st.success(f"✅ Video saved as version {st.session_state.get('video_version', 'N/A')}")

        with open(st.session_state["video_path"], "rb") as f:
            st.video(f.read())

        st.download_button(
            "📥 Download Video",
            data=open(st.session_state["video_path"], "rb").read(),
            file_name=os.path.basename(st.session_state["video_path"]),
            mime="video/mp4",
        )

        if st.button("🔄 Generate New"):
            st.session_state.clear()
            st.rerun()
    
    # Preview video from existing versions
    if "preview_video" in st.session_state:
        st.markdown("---")
        st.subheader("👁️ Video Preview")
        with open(st.session_state["preview_video"], "rb") as f:
            st.video(f.read())


# -------------------------------------------------
# VIDEO GENERATION LOGIC
# -------------------------------------------------
def generate_video_from_content(
    selected_voice: str,
    service_id: int,
    service_name: str,
    uploaded_pdf: Optional[st.runtime.uploaded_file_manager.UploadedFile],
    service_content: Optional[Dict],
    source_type: str
):
    """Generate training video from either PDF or form content"""
    try:
        progress = st.progress(0)
        status = st.empty()

        video_clips = []
        audio_paths = []

        # ==================================================
        # CASE 1: PDF EXISTS
        # ==================================================
        if uploaded_pdf:
            status.text("📄 Extracting content from PDF...")

            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(uploaded_pdf.read())
                pdf_path = tmp.name

            pages = extract_raw_content(pdf_path)
            raw_text = "\n".join(line for page in pages for line in page["lines"])

        # ==================================================
        # CASE 2: FORM CONTENT
        # ==================================================
        else:
            valid, msg = validate_service_content(service_content)
            if not valid:
                st.error(msg)
                return

            # Generate PDF from form
            status.text("📄 Generating training PDF from form...")
            pdf_path = generate_service_pdf(service_content)

            # Show download button
            with open(pdf_path, "rb") as f:
                st.download_button(
                    "📥 Download Training PDF",
                    data=f.read(),
                    file_name=os.path.basename(pdf_path),
                    mime="application/pdf",
                )

            # Extract text from the saved PDF
            pages = extract_raw_content(pdf_path)
            raw_text = "\n".join(line for page in pages for line in page["lines"])

        # ==================================================
        # GEMINI → SLIDES
        # ==================================================
        status.text("🧠 Structuring training slides using AI...")
        slides_response = generate_slides_from_raw(raw_text)
        slides = slides_response["slides"]

        # ==================================================
        # VIDEO PIPELINE
        # ==================================================
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
        
        # Generate to temporary location first
        temp_final_path = combine_slides_and_audio(
            video_clips, 
            audio_paths, 
            service_name=f"{service_name}_temp"
        )

        # Save with version management
        final_path, version = save_video_with_version(
            video_source=temp_final_path,
            service_id=service_id,
            service_name=service_name,
            source_type=source_type,
            is_upload=False
        )

        progress.progress(100)
        st.session_state["video_path"] = final_path
        st.session_state["video_version"] = version
        st.session_state["audio_paths"] = audio_paths

        status.empty()
        progress.empty()

        st.success(f"✅ Training video generated successfully as version {version}!")
        st.balloons()

    except Exception as e:
        st.error(f"❌ Error generating video: {e}")
        logging.exception("Video generation error")


# -------------------------------------------------
# EXISTING VIDEOS PAGE
# -------------------------------------------------
def show_existing_videos_page():
    st.title("📂 Existing Training Videos")
    st.markdown("---")

    # Get all service directories
    if not os.path.exists(VIDEOS_BASE_DIR):
        st.info("No videos found.")
        return

    service_dirs = [d for d in os.listdir(VIDEOS_BASE_DIR) 
                    if os.path.isdir(os.path.join(VIDEOS_BASE_DIR, d))]
    
    if not service_dirs:
        st.info("No videos available.")
        return

    # Fetch services for display names
    services = fetch_services_from_api()
    service_map = {s['service_id']: s['service_name'] for s in services}

    # Group by service
    st.subheader(f"📹 Videos for {len(service_dirs)} services")
    
    for service_id in sorted(service_dirs, key=lambda x: int(x)):
        service_id_int = int(service_id)
        service_name = service_map.get(service_id_int, f"Service {service_id}")
        
        videos = get_service_video_list(service_id_int)
        
        with st.expander(f"🎬 {service_name} (ID: {service_id}) - {len(videos)} versions", expanded=False):
            if not videos:
                st.info("No videos found for this service")
                continue
            
            for video in videos:
                col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 1])
                
                with col1:
                    st.text(f"Version {video['version']}")
                
                with col2:
                    st.text(f"{video['size_mb']:.2f} MB")
                
                with col3:
                    st.text(video['created'].strftime('%Y-%m-%d'))
                
                with col4:
                    with open(video['path'], "rb") as f:
                        st.download_button(
                            "📥",
                            data=f.read(),
                            file_name=video['filename'],
                            mime="video/mp4",
                            key=f"dl_{service_id}_{video['version']}"
                        )
                
                with col5:
                    if st.button("🗑️", key=f"del_{service_id}_{video['version']}"):
                        os.remove(video['path'])
                        st.success(f"Deleted version {video['version']}")
                        st.rerun()
                
                # Show video
                with st.container():
                    with open(video['path'], "rb") as f:
                        st.video(f.read())
                
                st.markdown("---")


# -------------------------------------------------
# RUN
# -------------------------------------------------
if __name__ == "__main__":
    main()