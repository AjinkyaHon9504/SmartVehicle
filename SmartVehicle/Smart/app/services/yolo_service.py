from ultralytics import YOLO

model = YOLO("app/models/plate_detector.pt")


def detect_plate(image):

    results = model(image)[0]

    detections = []

    for box in results.boxes:

        x1, y1, x2, y2 = map(int, box.xyxy[0])

        confidence = float(box.conf[0])

        detections.append({
            "bbox": (x1, y1, x2, y2),
            "confidence": confidence
        })

    return detections


def crop_plate(image, bbox):

    x1, y1, x2, y2 = bbox

    return image[y1:y2, x1:x2]