"""
SmartVehicle — Direct OCR Test (no YOLO needed)
Use this when you already have a cropped/close-up plate image.

Run: python quick_ocr.py <image_path>
Example: python quick_ocr.py test_plate.jpg
"""

import sys
import io
import cv2
import numpy as np
import easyocr
import re

# Fix Windows terminal encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

GREEN  = "\033[92m"
RED    = "\033[91m"
CYAN   = "\033[96m"
YELLOW = "\033[93m"
BOLD   = "\033[1m"
RESET  = "\033[0m"


def preprocess(img):
    gray  = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray  = cv2.bilateralFilter(gray, 11, 17, 17)
    thresh = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 31, 2
    )
    return thresh


def clean_plate(text):
    text = text.upper()
    text = re.sub(r'[^A-Z0-9]', '', text)
    fixes = {"O": "0", "Q": "0", "I": "1", "Z": "2", "S": "5"}
    return "".join(fixes.get(c, c) for c in text)


def run(image_path):
    print(f"\n{BOLD}{CYAN}======================================{RESET}")
    print(f"{BOLD}{CYAN}   SmartVehicle - Direct OCR Test      {RESET}")
    print(f"{BOLD}{CYAN}======================================{RESET}\n")

    img = cv2.imread(image_path)
    if img is None:
        print(f"{RED}✖  Cannot read: {image_path}{RESET}\n")
        return

    print(f"  📁  Image : {image_path}")
    print(f"  📐  Size  : {img.shape[1]} x {img.shape[0]} px\n")

    # Preprocess
    print(f"  🔧  Preprocessing (grayscale → bilateral filter → adaptive threshold)...")
    processed = preprocess(img)
    cv2.imwrite("processed_plate.jpg", processed)
    print(f"  ✔  Saved preprocessed image → processed_plate.jpg\n")

    # OCR
    print(f"  📖  Loading EasyOCR (first time takes ~10 seconds) ...")
    reader = easyocr.Reader(["en"], gpu=False)
    results = reader.readtext(processed)

    if not results:
        print(f"\n{RED}  ✖  No text detected.{RESET}\n")
        return

    # Show all raw OCR results
    print(f"\n  📋  Raw OCR results:")
    for bbox, text, conf in results:
        print(f"      Text: {YELLOW}{text!r:20}{RESET}  Confidence: {conf*100:.1f}%")

    # Pick top 3 by confidence, clean, filter ≥ 6 chars
    top3 = sorted(results, key=lambda x: x[2], reverse=True)[:3]
    candidates = []
    for _, text, conf in top3:
        cleaned = clean_plate(text)
        if len(cleaned) >= 6:
            candidates.append((cleaned, conf))

    print(f"\n  🧹  After cleaning & filtering:")
    for text, conf in candidates:
        print(f"      {YELLOW}{text:20}{RESET}  ({conf*100:.1f}%)")

    if not candidates:
        print(f"\n{RED}  ✖  No valid plate text found after cleaning.{RESET}\n")
        return

    best_text, best_conf = max(candidates, key=lambda x: x[1])

    print(f"\n{BOLD}{CYAN}======================================{RESET}")
    print(f"  {BOLD}PLATE TEXT  : {GREEN}{best_text}{RESET}")
    print(f"  Confidence  : {best_conf*100:.1f}%")
    print(f"{BOLD}{CYAN}======================================{RESET}\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"\n{YELLOW}Usage: python quick_ocr.py <image_path>{RESET}")
        print(f"Example: python quick_ocr.py test_plate.jpg\n")
        sys.exit(1)
    run(sys.argv[1])
