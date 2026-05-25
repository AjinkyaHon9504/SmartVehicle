"""
SmartVehicle — Quick Plate Test
Run: python test_plate.py <path_to_image>
Example: python test_plate.py test_plate.jpg
"""

import sys
import os
import cv2
import numpy as np

# ── make sure Django app path is on sys.path ──────────────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Smart.settings")

import django
django.setup()

# ── now import your existing services ─────────────────────────────
from app.services.yolo_service   import detect_plate, crop_plate
from app.services.ocr_service    import extract_text
from app.services.firebase_service import check_plate, add_log
from firebase_admin import db

# ──────────────────────────────────────────────────────────────────
# COLOURS FOR TERMINAL OUTPUT
GREEN  = "\033[92m"
RED    = "\033[91m"
CYAN   = "\033[96m"
YELLOW = "\033[93m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

# ──────────────────────────────────────────────────────────────────
def run_test(image_path: str):
    print(f"\n{BOLD}{CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
    print(f"{BOLD}{CYAN}   SmartVehicle — Plate Recognition Test   {RESET}")
    print(f"{BOLD}{CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}\n")

    # ── STEP 1: Load image ────────────────────────────────────────
    if not os.path.exists(image_path):
        print(f"{RED}✖  File not found: {image_path}{RESET}")
        print(f"{YELLOW}   Usage: python test_plate.py <path_to_image>{RESET}\n")
        return

    image = cv2.imread(image_path)
    if image is None:
        print(f"{RED}✖  Could not read image. Make sure it is a valid JPG/PNG.{RESET}\n")
        return

    print(f"  📁  Image loaded : {image_path}")
    print(f"  📐  Size         : {image.shape[1]} x {image.shape[0]} px\n")

    # ── STEP 2: YOLO — detect plate bounding box ─────────────────
    print(f"  🔍  Running YOLO plate detection ...")
    detections = detect_plate(image)

    if not detections:
        print(f"\n{RED}  ✖  No license plate detected in this image.{RESET}")
        print(f"{YELLOW}     Try a clearer photo or closer angle.\n{RESET}")
        return

    best = max(detections, key=lambda d: d["confidence"])
    x1, y1, x2, y2 = best["bbox"]
    conf = best["confidence"]
    print(f"  ✔  Plate found!  Confidence: {GREEN}{conf*100:.1f}%{RESET}")
    print(f"     Bounding box  : ({x1}, {y1}) → ({x2}, {y2})\n")

    # ── STEP 3: Crop the plate region ─────────────────────────────
    plate_crop = crop_plate(image, best["bbox"])

    # save the cropped plate so you can inspect it
    crop_path = image_path.replace(".", "_CROP.")
    cv2.imwrite(crop_path, plate_crop)
    print(f"  🖼   Cropped plate saved → {crop_path}\n")

    # ── STEP 4: OCR — read text from the plate crop ───────────────
    print(f"  📖  Running EasyOCR on cropped plate ...")
    plate_text = extract_text(plate_crop)

    if not plate_text:
        print(f"\n{RED}  ✖  OCR could not read any text from the plate.{RESET}")
        print(f"{YELLOW}     The crop may be too blurry or too small.\n{RESET}")
        return

    print(f"  ✔  Plate text read : {BOLD}{YELLOW}{plate_text}{RESET}\n")

    # ── STEP 5: Firebase authorization check ──────────────────────
    print(f"  🔥  Checking Firebase authorization ...")
    authorized = check_plate(plate_text)
    status = "AUTHORIZED" if authorized else "NOT_AUTHORIZED"

    if authorized:
        print(f"\n  {GREEN}{BOLD}✅  RESULT  : {status}{RESET}")
        print(f"  {GREEN}   Plate \"{plate_text}\" is in the authorized list.{RESET}")
        print(f"  {GREEN}   → Gate would OPEN 🚗{RESET}\n")
    else:
        print(f"\n  {RED}{BOLD}❌  RESULT  : {status}{RESET}")
        print(f"  {RED}   Plate \"{plate_text}\" is NOT in the authorized list.{RESET}")
        print(f"  {RED}   → Gate stays CLOSED 🚫{RESET}\n")

    # ── STEP 6: Write log to Firebase ─────────────────────────────
    print(f"  📝  Writing detection log to Firebase ...")
    add_log(plate_text, status)
    print(f"  ✔  Log saved.\n")

    # ── SUMMARY ───────────────────────────────────────────────────
    print(f"{BOLD}{CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
    print(f"  Plate          : {BOLD}{plate_text}{RESET}")
    print(f"  Confidence     : {conf*100:.1f}%")
    print(f"  Authorization  : {GREEN + 'AUTHORIZED ✅' if authorized else RED + 'NOT AUTHORIZED ❌'}{RESET}")
    print(f"{BOLD}{CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}\n")


# ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"\n{YELLOW}Usage: python test_plate.py <image_path>{RESET}")
        print(f"Example: python test_plate.py test_plate.jpg\n")
        sys.exit(1)

    run_test(sys.argv[1])
