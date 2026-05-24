from ultralytics import YOLO
import easyocr

# load once globally
plate_model = YOLO("models/license_plate.pt")
reader = easyocr.Reader(["en"])