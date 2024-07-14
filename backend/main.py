from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
import logging
import os
import json
import cv2
from typing import List
from tempfile import NamedTemporaryFile
from detect import detect_people  # Assuming this function is defined in detect.py
from track import track_people  # Assuming this function is defined in track.py
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import os
app = FastAPI()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure the videos and frames directories exist
os.makedirs("videos", exist_ok=True)
os.makedirs("frames", exist_ok=True)

class VideoPath(BaseModel):
    video_path: str

@app.post("/upload_video/")
async def upload_video(file: UploadFile = File(...)):
    file_location = f"videos/{file.filename}"
    with open(file_location, "wb") as f:
        f.write(file.file.read())
    logger.info(f"File '{file.filename}' saved at '{file_location}'")
    return {"info": f"File '{file.filename}' saved at '{file_location}'"}

@app.post("/process_video/")
async def process_video(video_path: VideoPath):
    video_path_str = video_path.video_path
    logger.info(f"Received video path: {video_path_str}")

    if not os.path.exists(video_path_str):
        logger.error(f"Video file '{video_path_str}' not found")
        raise HTTPException(status_code=404, detail=f"Video file '{video_path_str}' not found")

    cap = cv2.VideoCapture(video_path_str)
    if not cap.isOpened():
        logger.error(f"Error opening video file '{video_path_str}'")
        raise HTTPException(status_code=500, detail=f"Error opening video file '{video_path_str}'")

    frame_number = 0
    tracking_results = []

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_number += 1

        # Perform detection on the current frame
        detections = detect_people(frame)

        # Perform tracking on detected objects across frames
        tracked_objects = track_people(detections)

        # Draw rectangles and labels on the frame for visualization
        for (x1, y1, x2, y2, conf) in detections:
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
            cv2.putText(frame, f'Person {conf:.2f}', (int(x1), int(y1)-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36, 255, 12), 2)

        for track in tracked_objects:
            x1, y1, x2, y2, track_id = track[:5]
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (255, 0, 0), 2)
            cv2.putText(frame, f'ID {int(track_id)}', (int(x1), int(y1)-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)

        # Save the frame with visualizations
        frame_path = f"frames/frame_{frame_number}.jpg"
        cv2.imwrite(frame_path, frame)

        tracking_results.append({
            "frame_number": frame_number,
            "detections": detections,
            "tracked_objects": tracked_objects
        })

    cap.release()
    with open('tracking_results.json', 'w') as f:
        json.dump(tracking_results, f)

    return {"info": f"Processed video '{video_path_str}'"}

@app.get("/download_tracking_results/")
async def download_tracking_results():
    tracking_results_path = "tracking_results.json"
    if os.path.exists(tracking_results_path):
        with open(tracking_results_path, "r") as f:
            tracking_results = json.load(f)
        return JSONResponse(content=tracking_results, status_code=200)
    else:
        return JSONResponse(content={"error": "Tracking results file not found"}, status_code=404)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
