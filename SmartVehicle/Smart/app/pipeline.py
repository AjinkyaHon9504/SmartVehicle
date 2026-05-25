import cv2
import numpy as np

from app.services.yolo_service import detect_plate
from app.services.ocr_service import extract_text

from firebase_admin import db

from datetime import datetime


def process_image(image_file):

    file_bytes = np.frombuffer(image_file.read(), np.uint8)

    image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    if image is None:
        return {
            "status": "ERROR",
            "error": "Failed to decode image file. Ensure it is a valid JPEG/PNG."
        }

    detections = detect_plate(image)

    # ── decide what region to run OCR on ─────────────────────────
    if len(detections) == 0:
        # YOLO found no plate bounding box — fall back to full image OCR
        # (handles close-up / already-cropped plate photos)
        crop = image
        confidence = 0.75   # assume reasonable confidence for direct shots
    else:
        detection = detections[0]
        x1, y1, x2, y2 = detection["bbox"]
        confidence = detection["confidence"]

        # low confidence filter
        if confidence < 0.50:
            return {"status": "LOW_CONFIDENCE"}

        crop = image[y1:y2, x1:x2]

    # ── OCR on the selected region ────────────────────────────────
    plate_text = extract_text(crop)

    if not plate_text:
        return {"status": "NO_TEXT"}

    # ── Firebase authorization check ──────────────────────────────
    auth_ref  = db.reference("authorized_plates")
    auth_data = auth_ref.get() or {}
    authorized = plate_text in auth_data
    status = "AUTHORIZED" if authorized else "NOT_AUTHORIZED"

    # ── Write log ─────────────────────────────────────────────────
    logs_ref = db.reference("logs")
    logs_ref.push({
        "plate":      plate_text,
        "status":     status,
        "confidence": confidence,
        "time":       datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    return {
        "plate":      plate_text,
        "status":     status,
        "confidence": confidence
    }