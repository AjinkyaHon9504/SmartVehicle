import easyocr
import re
import cv2
import numpy as np

reader = easyocr.Reader(["en"], gpu=False)


# -------------------------
# IMAGE PREPROCESSING
# -------------------------
def preprocess(img):

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    gray = cv2.bilateralFilter(gray, 11, 17, 17)

    thresh = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        2
    )

    return thresh


# -------------------------
# CLEAN TEXT (IMPROVED)
# -------------------------
def clean_plate(text):

    text = text.upper()
    text = re.sub(r'[^A-Z0-9]', '', text)

    # safer replacements (ONLY common OCR mistakes)
    replacements = {
        "O": "0",
        "Q": "0",
        "I": "1",
        "Z": "2",
        "S": "5",
    }

    fixed = ""
    for c in text:
        fixed += replacements.get(c, c)

    return fixed


# -------------------------
# INDIAN PLATE VALIDATION
# -------------------------
def is_valid_plate(text):

    pattern = r'^[A-Z]{2}[0-9]{1,2}[A-Z]{1,3}[0-9]{3,4}$'

    return bool(re.match(pattern, text))


# -------------------------
# MAIN OCR
# -------------------------
def extract_text(image):

    # Try raw image first (EasyOCR performs much better on raw RGB/Grayscale images)
    results = reader.readtext(image)

    if not results:
        processed = preprocess(image)
        results = reader.readtext(processed)

    if not results:
        return None

    # take top 3 results instead of only 1
    results = sorted(results, key=lambda x: x[2], reverse=True)[:3]

    candidates = []

    for _, text, conf in results:

        cleaned = clean_plate(text)

        if len(cleaned) >= 8:  # ignore junk
            candidates.append((cleaned, conf))

    if not candidates:
        return None

    # choose best by confidence
    best = max(candidates, key=lambda x: x[1])[0]

    return best