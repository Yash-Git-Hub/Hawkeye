import numpy as np
from sort import Sort

tracker = Sort()

def track_people(detections):
    tracked_objects = tracker.update(np.array(detections))
    return tracked_objects

if __name__ == "__main__":
    # Example detections format: [(x1, y1, x2, y2, conf), ...]
    detections = [(50, 50, 100, 100, 0.9), (200, 200, 250, 250, 0.8)]
    tracked_objects = track_people(detections)
    print(tracked_objects)
