import streamlit as st
import requests
import tempfile
import os

st.title("Hawkeye: CCTV People Tracking")

uploaded_file = st.file_uploader("Upload a video", type=["mp4", "avi", "mov"])

if uploaded_file is not None:
    temp_video = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
    temp_video.write(uploaded_file.read())
    temp_video.close()

    st.video(temp_video.name)

    with open(temp_video.name, "rb") as video_file:
        files = {"file": video_file}
        upload_response = requests.post("http://localhost:8000/upload_video/", files=files)
        if upload_response.status_code == 200:
            st.success("Video uploaded successfully!")
        else:
            st.error("Failed to upload video.")

    video_path = f"videos/{os.path.basename(temp_video.name)}"
    process_response = requests.post("http://localhost:8000/process_video/", json={"video_path": video_path})
    if process_response.status_code == 200:
        st.success("Video processed successfully!")
        
        # Download tracking results
        download_response = requests.get("http://localhost:8000/download_tracking_results/")
        if download_response.status_code == 200:
            tracking_results = download_response.json()
            st.write("Tracking Results:")
            st.json(tracking_results)
        else:
            st.error("Failed to download tracking results.")
    else:
        st.error("Failed to process video.")
