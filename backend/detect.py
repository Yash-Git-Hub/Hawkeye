import torch
import cv2
import numpy as np

# Load the YOLOv5 model
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)

def detect_people(image):
    results = model(image)
    bboxes = results.xyxy[0].numpy()
    detections = []
    for bbox in bboxes:
        x1, y1, x2, y2, conf, cls = bbox
        if int(cls) == 0:  # class 0 is person
            detections.append((x1, y1, x2, y2, conf))

    return detections

if __name__ == "__main__":
    image_path = 'path/to/your/image.jpg'
    img = cv2.imread(image_path)
    detections = detect_people(img)
    print(detections)
