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