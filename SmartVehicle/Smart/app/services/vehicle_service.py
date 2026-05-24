from ultralytics import YOLO

# COCO pretrained model
model = YOLO("yolov8n.pt")

# COCO vehicle classes
VEHICLE_CLASSES = {
    2: "car",
    3: "motorcycle",
    5: "bus",
    7: "truck"
}


def detect_vehicles(frame):
    results = model(frame)[0]

    count = 0
    detections = []

    for box in results.boxes:

        cls = int(box.cls[0])
        conf = float(box.conf[0])

        if cls in VEHICLE_CLASSES:

            count += 1

            x1, y1, x2, y2 = map(int, box.xyxy[0])

            detections.append({
                "class": VEHICLE_CLASSES[cls],
                "confidence": conf,
                "bbox": (x1, y1, x2, y2)
            })

    return count, detections