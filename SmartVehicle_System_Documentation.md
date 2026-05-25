# SmartVehicle Parking System
## Complete Technical Architecture, Workflow & Implementation Guide

---

> **Document Version:** 1.0  
> **Project:** SmartVehicle — AI-Powered Smart Parking Management System  
> **Technology Stack:** Django · Firebase Realtime DB · YOLOv8 · EasyOCR · OpenCV · Python  
> **Author:** Ajinkya  
> **Date:** May 2026

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [High-Level System Architecture](#2-high-level-system-architecture)
3. [Hardware Components](#3-hardware-components)
4. [Software Stack & Dependencies](#4-software-stack--dependencies)
5. [Project Directory Structure](#5-project-directory-structure)
6. [System Startup Sequence](#6-system-startup-sequence)
7. [Firebase Realtime Database Schema](#7-firebase-realtime-database-schema)
8. [Pipeline 1 — License Plate Detection & Authorization](#8-pipeline-1--license-plate-detection--authorization)
9. [Pipeline 2 — Live Vehicle Counting via Webcam](#9-pipeline-2--live-vehicle-counting-via-webcam)
10. [REST API Endpoints](#10-rest-api-endpoints)
11. [Dashboard & Web UI](#11-dashboard--web-ui)
12. [Full End-to-End Workflow Scenarios](#12-full-end-to-end-workflow-scenarios)
13. [Security & Credential Management](#13-security--credential-management)
14. [Key Design Decisions & Trade-offs](#14-key-design-decisions--trade-offs)
15. [Deployment Notes](#15-deployment-notes)

---

## 1. Project Overview

SmartVehicle is an AI-powered smart parking management system that integrates hardware cameras, computer vision, machine learning, and cloud real-time databases into a seamless web dashboard.

The system performs two primary functions:

| Function | Trigger | Technology |
|---|---|---|
| **License Plate Detection & Authorization** | REST API POST with image | YOLOv8 Custom Model + EasyOCR + Firebase |
| **Live Vehicle Counting** | Admin activates webcam thread | YOLOv8 COCO Model + OpenCV + Firebase |

The system is built to serve a physical parking lot, where:
- A **camera/webcam** monitors the parking lot at all times.
- An **entry-point camera** captures incoming vehicles for plate recognition.
- A **web dashboard** gives the administrator full real-time visibility and control.

---

## 2. High-Level System Architecture

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                         SMARTVEHICLE SYSTEM ARCHITECTURE                     ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║   ┌─────────────────────────────────────────────────────────────────────┐   ║
║   │                      HARDWARE LAYER                                  │   ║
║   │                                                                      │   ║
║   │   ┌─────────────────────┐        ┌──────────────────────────┐       │   ║
║   │   │  ENTRY CAMERA       │        │  PARKING LOT CAMERA      │       │   ║
║   │   │  (Plate Capture)    │        │  (Overhead / Wide-angle) │       │   ║
║   │   │                     │        │                          │       │   ║
║   │   │  • Captures         │        │  • Continuously counts   │       │   ║
║   │   │    incoming vehicle │        │    parked vehicles       │       │   ║
║   │   │  • Sends image to   │        │  • Connected to server   │       │   ║
║   │   │    REST API via     │        │    as webcam (index 0)   │       │   ║
║   │   │    HTTP POST        │        │  • Reads via cv2         │       │   ║
║   │   └──────────┬──────────┘        └───────────┬──────────────┘       │   ║
║   └──────────────│───────────────────────────────│──────────────────────┘   ║
║                  │                               │                           ║
║                  ▼                               ▼                           ║
║   ┌─────────────────────────────────────────────────────────────────────┐   ║
║   │                       DJANGO BACKEND SERVER                          │   ║
║   │                   (Python · Django · REST Framework)                 │   ║
║   │                                                                      │   ║
║   │  ┌──────────────────────┐      ┌──────────────────────────────┐     │   ║
║   │  │  PIPELINE 1          │      │  PIPELINE 2                  │     │   ║
║   │  │  Plate Authorization │      │  Vehicle Counter Service     │     │   ║
║   │  │                      │      │                              │     │   ║
║   │  │  POST /upload/       │      │  GET /vehicles/detect/start/ │     │   ║
║   │  │  ┌───────────────┐   │      │  ┌──────────────────────┐   │     │   ║
║   │  │  │ YOLO Custom   │   │      │  │ YOLOv8n COCO Model   │   │     │   ║
║   │  │  │ plate_detect. │   │      │  │ (Car/Bus/Truck/Moto) │   │     │   ║
║   │  │  │ pt            │   │      │  │ OpenCV VideoCapture  │   │     │   ║
║   │  │  └──────┬────────┘   │      │  └──────────┬───────────┘   │     │   ║
║   │  │         │            │      │             │               │     │   ║
║   │  │  ┌──────▼────────┐   │      │             │               │     │   ║
║   │  │  │  EasyOCR      │   │      │             │               │     │   ║
║   │  │  │  Text Extract │   │      │             │               │     │   ║
║   │  │  └──────┬────────┘   │      │             │               │     │   ║
║   │  └─────────│────────────┘      └─────────────│───────────────┘     │   ║
║   │            │                                 │                     │   ║
║   │            └───────────────┬─────────────────┘                     │   ║
║   │                            │                                        │   ║
║   │             ┌──────────────▼──────────────────┐                    │   ║
║   │             │     Firebase Realtime DB         │                    │   ║
║   │             │   Admin SDK (Read / Write)        │                    │   ║
║   │             └──────────────┬──────────────────┘                    │   ║
║   │                            │                                        │   ║
║   │             ┌──────────────▼──────────────────┐                    │   ║
║   │             │  Dashboard Views (Django)         │                    │   ║
║   │             │  Reads Firebase → HTML templates  │                    │   ║
║   │             └──────────────┬──────────────────┘                    │   ║
║   └────────────────────────────│───────────────────────────────────────┘   ║
║                                │                                            ║
║                                ▼                                            ║
║   ┌─────────────────────────────────────────────────────────────────────┐   ║
║   │                    FIREBASE REALTIME DATABASE                        │   ║
║   │             (Google Cloud · Asia Southeast Region)                   │   ║
║   │                                                                      │   ║
║   │   authorized_plates/    logs/    parking/                            │   ║
║   └──────────────────────────────────────────────────────────────────────┘  ║
║                                │                                            ║
║                                ▼                                            ║
║   ┌─────────────────────────────────────────────────────────────────────┐   ║
║   │                     WEB BROWSER (Admin)                              │   ║
║   │          Premium Dark Glassmorphic Dashboard UI                      │   ║
║   │   Dashboard · Vehicles · Logs · Slots · Detection Control            │   ║
║   └─────────────────────────────────────────────────────────────────────┘   ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

---

## 3. Hardware Components

### 3.1 Entry-Point Camera (License Plate Capture)

| Property | Details |
|---|---|
| **Role** | Captures images of vehicles entering the parking lot |
| **Placement** | At the gate/boom barrier at the entrance |
| **How it feeds data** | Any client (mobile app, barrier controller, Raspberry Pi) sends an HTTP POST request to `/upload/` with the captured image |
| **Format** | JPEG/PNG multipart form upload |
| **Direction** | Image data flows → Django REST API |

**Why it matters:** The entry camera is the first trigger of the authorization chain. When a vehicle arrives, this camera takes a frame of the front license plate and sends it to the server which performs YOLO-based plate detection, OCR text reading, and Firebase authorization checks — all within milliseconds.

**Supported Deployments:**
- A Raspberry Pi with Pi Camera module running a script that POSTs the image on a GPIO-triggered button press or motion sensor.
- Any IP camera that can invoke a webhook/HTTP POST.
- A laptop or phone showing the captured image at an angle to the built-in webcam.
- Automated capture scripts running on edge hardware at the gate.

---

### 3.2 Parking Lot Camera (Vehicle Counting Webcam)

| Property | Details |
|---|---|
| **Role** | Continuously counts the number of vehicles currently parked |
| **Placement** | Overhead or elevated position to see the full parking lot |
| **Connection** | Connected to the server as the default webcam (`cv2.VideoCapture(0)`) |
| **Update interval** | Every 3 seconds, the counted vehicle number is pushed to Firebase |
| **Direction** | Webcam → OpenCV frame → YOLOv8 inference → Firebase update |

**Why it matters:** The parking lot camera removes the need for physical sensors or loop detectors in each slot. A single wide-angle camera overhead the entire lot can count all parked vehicles at once using object detection (YOLO), eliminating the cost of per-slot hardware.

**Index 0 Assumption:** The system uses `cv2.VideoCapture(0)` which means the first available camera on the system. If running on a dedicated server or Raspberry Pi connected to a USB camera, that USB camera becomes index 0 automatically.

---

### 3.3 Hardware-Software Interface Diagram

```
PHYSICAL PARKING LOT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    ┌──────────────────────────────────────────────┐
    │                  ENTRANCE GATE               │
    │                                              │
    │   ┌────────────┐     ┌─────────────────┐    │
    │   │  VEHICLE → │────▶│  ENTRY CAM      │    │
    │   │  ARRIVES   │     │  Captures Plate │    │
    │   └────────────┘     └────────┬────────┘    │
    │                               │             │
    │                    HTTP POST  │             │
    │                    /upload/   │             │
    └───────────────────────────────│─────────────┘
                                    │
                                    ▼
    ┌──────────────────────────────────────────────┐
    │              PARKING LOT AREA                │
    │                                              │
    │   ┌─────────────────────────────────────┐   │
    │   │         OVERHEAD CAMERA             │   │
    │   │  ┌──┐ ┌──┐ ┌──┐ ┌──┐ ┌──┐ ┌──┐   │   │
    │   │  │🚗│ │🚗│ │  │ │🚗│ │  │ │  │   │   │
    │   │  └──┘ └──┘ └──┘ └──┘ └──┘ └──┘   │   │
    │   │  Slot1 Slot2 Slot3 Slot4 Slot5 Sl6 │   │
    │   └─────────────────────────────────────┘   │
    │             │ USB/RTSP to Server             │
    └─────────────│────────────────────────────────┘
                  │
                  ▼ cv2.VideoCapture(0)
         DJANGO SERVER counts vehicles
         every 3 seconds via YOLOv8
```

---

## 4. Software Stack & Dependencies

### 4.1 Core Dependencies

| Library | Version | Purpose |
|---|---|---|
| **Django** | 6.0.5 | Web framework — routes, views, templates, admin |
| **djangorestframework** | Latest | REST API endpoints for `POST /upload/` |
| **django-cors-headers** | Latest | Allow cross-origin requests (for IoT device POSTs) |
| **firebase-admin** | Latest | Firebase Admin SDK — read/write Realtime Database |
| **ultralytics** | Latest | YOLOv8 model runner (both custom & COCO models) |
| **easyocr** | Latest | Deep-learning based OCR for reading plate text |
| **opencv-python** | Latest | Frame capture, image decoding, preprocessing |
| **numpy** | Latest | Buffer-to-image conversion for uploaded files |
| **Pillow** | Latest | Image support dependency |
| **torch** | Latest | Deep learning backend for EasyOCR & YOLO inference |

### 4.2 AI Models Used

| Model File | Type | Purpose | Input | Output |
|---|---|---|---|---|
| `app/models/plate_detector.pt` | Custom YOLOv8 | License plate bounding box detection | Vehicle image | List of `{bbox, confidence}` |
| `yolov8n.pt` | COCO Pre-trained YOLOv8n | Multi-class vehicle detection | Camera frame | Count + `{class, bbox, confidence}` |

---

## 5. Project Directory Structure

```
SmartVehicle/
├── .gitignore                          ← Git exclusions (venv, firebase secrets, etc.)
├── requirements.txt                    ← Python package list for setup
│
└── SmartVehicle/
    └── Smart/                          ← Django project root (manage.py here)
        │
        ├── manage.py                   ← Django CLI entry point
        ├── db.sqlite3                  ← Local SQLite (Django admin/session only)
        ├── yolov8n.pt                  ← COCO pretrained YOLOv8n (vehicle counter)
        │
        ├── firebase/
        │   └── firebase.json           ← 🔐 Firebase service account credentials (KEEP SECRET)
        │
        ├── Smart/                      ← Django project settings package
        │   ├── settings.py             ← App config, installed apps, DB, CORS, templates
        │   ├── urls.py                 ← Root URL dispatcher (includes app.urls)
        │   ├── wsgi.py                 ← WSGI server entry point
        │   └── asgi.py                 ← ASGI server entry point
        │
        └── app/                        ← Main Django application
            │
            ├── apps.py                 ← AppConfig — triggers firebase_init.py on startup
            ├── firebase_init.py        ← Firebase Admin SDK initialization (runs once)
            ├── firebase_utils.py       ← Update occupied_slots in Firebase (overflow-safe)
            ├── dashboard_views.py      ← All HTML dashboard page views
            ├── views.py                ← REST API views (upload, start/stop detection)
            ├── urls.py                 ← App-level URL routing
            ├── pipeline.py             ← Pipeline 1: Image → YOLO → OCR → Firebase log
            ├── vehicle_pipeline.py     ← Pipeline 2: Webcam → YOLO → Firebase update
            │
            ├── models/
            │   └── plate_detector.pt   ← Custom YOLO model for license plate detection
            │
            ├── services/
            │   ├── yolo_service.py     ← Loads custom YOLO model, detect_plate()
            │   ├── ocr_service.py      ← EasyOCR reader, preprocessing, clean_plate()
            │   ├── vehicle_service.py  ← Loads COCO YOLO, detect_vehicles()
            │   ├── firebase_service.py ← check_plate(), add_log(), update_slots()
            │   └── ml_model.py         ← Global model loader (plate + reader)
            │
            └── templates/
                └── dashboard/
                    ├── base_layout.html    ← Master layout: sidebar, header, JS clock
                    ├── index.html          ← Dashboard home with stat cards + webcam control
                    ├── vehicles.html       ← Authorized vehicles table with plate styling
                    ├── add_vehicle.html    ← Vehicle registration form
                    ├── logs.html           ← Detection event history + search + status badges
                    ├── slots.html          ← Parking capacity configuration
                    └── vehicle_detect.html ← Standalone webcam control console
```

---

## 6. System Startup Sequence

When you run `python manage.py runserver`, the following boot sequence happens in precise order:

```
python manage.py runserver
         │
         ▼
1. Django Framework Initialization
   └── Loads Smart/settings.py
       ├── INSTALLED_APPS → registers 'app.apps.AppConfig'
       ├── DATABASES → SQLite for Django admin/sessions
       ├── CORS_ALLOW_ALL_ORIGINS = True (allows IoT POST requests)
       ├── TEMPLATES DIRS → app/templates/ (for HTML rendering)
       └── ROOT_URLCONF → Smart.urls
         │
         ▼
2. AppConfig.ready() is called  [app/apps.py]
   └── import app.firebase_init
         │
         ▼
3. Firebase Initialization  [firebase_init.py]
   ├── Loads firebase/firebase.json (Google service account credentials)
   ├── Connects to Firebase project: carmanagement-5b8f2
   ├── Region: asia-southeast1
   └── Prints: "[OK] Firebase Initialized"
         │
         ▼
4. YOLO Models Loaded (lazy, on first request)
   ├── yolo_service.py   → loads app/models/plate_detector.pt  (custom)
   └── vehicle_service.py → loads yolov8n.pt  (COCO pretrained)
         │
         ▼
5. EasyOCR Reader Initialized  [ocr_service.py]
   ├── Language: English
   ├── GPU: False (CPU inference)
   └── Downloads model weights on first run (~43 MB cached after)
         │
         ▼
6. Django URL Router Ready
   ├── /admin/       → Django admin panel
   ├── /upload/      → Pipeline 1 REST endpoint
   ├── /             → Dashboard home
   ├── /vehicles/    → Vehicles list page
   ├── /logs/        → Detection logs page
   ├── /slots/       → Slot config page
   └── /vehicles/detect/start/ & /stop/ → Webcam thread control
         │
         ▼
7. Server Ready → http://127.0.0.1:8000/
```

---

## 7. Firebase Realtime Database Schema

The entire application's runtime data is stored in a single Firebase Realtime Database. Here is the full schema:

```json
{
  "authorized_plates": {
    "MH12AB1234": {
      "owner": "Rajesh Sharma",
      "vehicle": "White Honda City",
      "allowed": true,
      "created_at": "2026-05-24 10:00:00"
    },
    "MH04XY9876": {
      "owner": "Priya Mehta",
      "vehicle": "Black Toyota SUV",
      "allowed": true,
      "created_at": "2026-05-24 11:30:00"
    }
  },

  "logs": {
    "-Nabc123def456": {
      "plate": "MH12AB1234",
      "status": "AUTHORIZED",
      "confidence": 0.921,
      "time": "2026-05-24 14:05:22"
    },
    "-Nxyz789uvw000": {
      "plate": "DL5SAB1234",
      "status": "NOT_AUTHORIZED",
      "confidence": 0.874,
      "time": "2026-05-24 14:11:07"
    }
  },

  "parking": {
    "total_slots": 50,
    "occupied_slots": 18
  }
}
```

### Schema Explanation

| Node | Data Type | Purpose | Who Writes | Who Reads |
|---|---|---|---|---|
| `authorized_plates` | Object (dict) | Whitelist of registered vehicle plates | Admin Dashboard (add/delete) | Pipeline 1 (authorization check) |
| `logs` | Object (push-key keyed) | Append-only log of every vehicle scanned | Pipeline 1 automatically | Logs dashboard page |
| `parking` | Object | Current total and occupied slot counts | Pipeline 2 (auto), Admin dashboard | Dashboard home, all pages |

**Why Firebase Realtime DB?**
- Any edge device (Raspberry Pi, phone, embedded camera unit) can write to and read from Firebase over HTTPS without needing to be on the same network as the server.
- The dashboard and Firebase are always consistent — no cache invalidation needed.
- Data is persistent and backed up by Google Cloud.
- Supports unlimited concurrent readers (useful if multiple dashboards or screens show parking info).

---

## 8. Pipeline 1 — License Plate Detection & Authorization

This is the most complex pipeline in the system. It accepts an image, detects a license plate, reads the text via OCR, and checks if the vehicle is authorized — all in one synchronous HTTP request.

### 8.1 Trigger

```
Any client device sends:
POST /upload/
Content-Type: multipart/form-data
Body: image=<image_file>
```

### 8.2 Complete Step-by-Step Flow

```
CLIENT (Camera / IoT Device / Test Client)
      │
      │ POST /upload/ with image file
      ▼
┌─────────────────────────────────────────────────────────────────┐
│  views.py → upload_image()                                       │
│                                                                   │
│  image = request.FILES.get("image")                              │
│  if not image: return {"error": "No image uploaded"}             │
│  result = process_image(image)                                    │
│  return Response(result)                                          │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 1: Image Decoding  [pipeline.py]                           │
│                                                                   │
│  file_bytes = np.frombuffer(image_file.read(), np.uint8)         │
│  image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)              │
│                                                                   │
│  WHY: Django's UploadedFile is a binary stream, not a numpy      │
│  array. OpenCV needs a numpy uint8 array. np.frombuffer reads    │
│  the raw bytes and cv2.imdecode decodes JPEG/PNG to BGR matrix.  │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 2: YOLO License Plate Detection  [yolo_service.py]         │
│                                                                   │
│  Model: app/models/plate_detector.pt (CUSTOM TRAINED)            │
│                                                                   │
│  results = model(image)[0]                                        │
│  for box in results.boxes:                                        │
│      bbox = (x1, y1, x2, y2)  ← pixel coordinates               │
│      confidence = float(box.conf[0])                             │
│                                                                   │
│  Returns: List of {bbox, confidence}                             │
│                                                                   │
│  VALIDATION:                                                      │
│  • If len(detections) == 0  → return {"status": "NO_PLATE"}     │
│  • If confidence < 0.50     → return {"status": "LOW_CONFIDENCE"}│
│                                                                   │
│  WHY CUSTOM MODEL? The standard YOLO COCO model does not detect  │
│  license plates as a class. A custom model fine-tuned            │
│  specifically on license plate images provides dramatically       │
│  higher detection precision for this use case.                   │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 3: Plate Region Crop  [pipeline.py]                        │
│                                                                   │
│  detection = detections[0]  ← take first (highest conf) plate   │
│  x1, y1, x2, y2 = detection["bbox"]                             │
│  crop = image[y1:y2, x1:x2]                                     │
│                                                                   │
│  WHY: Feeding the full vehicle image to OCR would result in      │
│  misreads from other text visible in the frame (road signs,      │
│  brand names, etc.). Cropping isolates exactly the plate region. │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 4: Image Preprocessing  [ocr_service.py → preprocess()]   │
│                                                                   │
│  gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)                    │
│  │  WHY: OCR works on single-channel images. Grayscale           │
│  │  eliminates color noise without losing structural detail.     │
│                                                                   │
│  gray = cv2.bilateralFilter(gray, 11, 17, 17)                    │
│  │  WHY: Bilateral filter smooths noise WHILE preserving edges   │
│  │  (unlike Gaussian blur which blurs edges). This is critical   │
│  │  for license plates where the character edges must stay sharp.│
│                                                                   │
│  thresh = cv2.adaptiveThreshold(                                 │
│      gray, 255,                                                  │
│      cv2.ADAPTIVE_THRESH_GAUSSIAN_C,                             │
│      cv2.THRESH_BINARY, 31, 2                                    │
│  )                                                                │
│  │  WHY: Adaptive thresholding handles non-uniform lighting     │
│  │  (shadows, reflections, angle). A global threshold would     │
│  │  fail when half the plate is shadowed. Gaussian adaptive     │
│  │  computes the threshold for small local 31×31 regions.       │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 5: EasyOCR Text Extraction  [ocr_service.py]               │
│                                                                   │
│  reader = easyocr.Reader(["en"], gpu=False)  ← loaded once      │
│  results = reader.readtext(processed)                            │
│                                                                   │
│  # Take top 3 results sorted by confidence                       │
│  results = sorted(results, key=lambda x: x[2], reverse=True)[:3]│
│                                                                   │
│  for _, text, conf in results:                                   │
│      cleaned = clean_plate(text)                                 │
│      if len(cleaned) >= 8:                                       │
│          candidates.append((cleaned, conf))                      │
│                                                                   │
│  best = max(candidates, key=lambda x: x[1])[0]                  │
│                                                                   │
│  WHY TOP 3? EasyOCR may detect multiple text regions on the     │
│  plate (character groups separated by space). Taking 3 and       │
│  selecting the highest confidence candidate gives a more         │
│  reliable read than trusting a single detection.                 │
│                                                                   │
│  WHY len >= 8? Indian plates are at least 8 chars (e.g.          │
│  MH12AB12). Anything shorter is noise or partial detection.      │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 6: Plate Text Cleaning  [ocr_service.py → clean_plate()]  │
│                                                                   │
│  text = text.upper()                                             │
│  text = re.sub(r'[^A-Z0-9]', '', text)  ← strip non-alphanum   │
│                                                                   │
│  OCR Character Substitutions (common visual confusion):          │
│  ┌─────────┬──────────┬──────────────────────────────────────┐  │
│  │ Seen As │ Fixed To │ Reason                               │  │
│  ├─────────┼──────────┼──────────────────────────────────────┤  │
│  │   O     │    0     │ Letter O and digit Zero look same    │  │
│  │   Q     │    0     │ Q often misread for 0 in plates      │  │
│  │   I     │    1     │ Letter I and digit 1 look same       │  │
│  │   Z     │    2     │ Z and 2 look similar                 │  │
│  │   S     │    5     │ S and 5 are visually similar         │  │
│  └─────────┴──────────┴──────────────────────────────────────┘  │
│                                                                   │
│  → If no valid candidates: return {"status": "NO_TEXT"}          │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 7: Firebase Authorization Check  [pipeline.py]             │
│                                                                   │
│  auth_ref = db.reference("authorized_plates")                    │
│  auth_data = auth_ref.get() or {}                                │
│  authorized = plate_text in auth_data                            │
│  status = "AUTHORIZED" if authorized else "NOT_AUTHORIZED"       │
│                                                                   │
│  WHY: Authorization is a simple dictionary key lookup in         │
│  Firebase. The plate text (cleaned) is checked against the       │
│  admin-managed whitelist of registered vehicles. This is         │
│  O(1) for Firebase's indexed structure.                          │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 8: Write Detection Log to Firebase  [pipeline.py]          │
│                                                                   │
│  logs_ref = db.reference("logs")                                 │
│  logs_ref.push({                                                 │
│      "plate": plate_text,                                        │
│      "status": status,                                           │
│      "confidence": confidence,                                   │
│      "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")       │
│  })                                                              │
│                                                                   │
│  WHY .push()? Firebase's push() generates a unique time-based   │
│  key (like -NxyzABC123). This creates an append-only log.        │
│  Using .set() with a fixed key would overwrite the last record.  │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│  RESPONSE to Client                                              │
│                                                                   │
│  {                                                               │
│    "plate": "MH12AB1234",                                        │
│    "status": "AUTHORIZED",       ← or "NOT_AUTHORIZED"          │
│    "confidence": 0.921                                           │
│  }                                                               │
└─────────────────────────────────────────────────────────────────┘
```

### 8.3 Pipeline 1 — Decision Tree

```
Image Received
      │
      ├─ No image attached? ──────────────────▶ {"error": "No image uploaded"}
      │
      ▼
YOLO Plate Detection
      │
      ├─ No plates found? ────────────────────▶ {"status": "NO_PLATE"}
      │
      ├─ Confidence < 50%? ───────────────────▶ {"status": "LOW_CONFIDENCE"}
      │
      ▼
Crop Plate Region → Preprocess → EasyOCR
      │
      ├─ No readable text? ───────────────────▶ {"status": "NO_TEXT"}
      │
      ▼
Clean Plate Text
      │
      ├─ Less than 8 characters? ────────────▶ {"status": "NO_TEXT"}
      │
      ▼
Firebase Authorization Check
      │
      ├─ Plate found in authorized_plates? ──▶ status = "AUTHORIZED"
      │
      └─ Not found? ─────────────────────────▶ status = "NOT_AUTHORIZED"
                │
                ▼
      Log to Firebase logs/
                │
                ▼
      Return JSON { plate, status, confidence }
```

---

## 9. Pipeline 2 — Live Vehicle Counting via Webcam

This pipeline runs as a persistent **background daemon thread** on the server, continuously capturing and processing webcam frames to count parked vehicles.

### 9.1 Trigger

```
Admin opens Dashboard → Clicks "Start Detection Thread"
      │
      ▼
GET /vehicles/detect/start/   → views.py → start_detection()
      │
      ▼
service.start()  [vehicle_pipeline.py]
```

### 9.2 Service Architecture

```python
class VehicleCounterService:
    def __init__(self):
        self.running = False
        self.thread = None

    def start(self):
        if self.running:          ← Prevents duplicate threads
            return
        self.running = True
        self.thread = threading.Thread(target=self._run)
        self.thread.daemon = True  ← Thread dies if server stops
        self.thread.start()

    def stop(self):
        self.running = False      ← Signal thread to exit loop

# GLOBAL SINGLETON — created ONCE at module import
service = VehicleCounterService()
```

**The Singleton Pattern:** The `service` object is created at module import time. Every HTTP request to `/start/` and `/stop/` operates on the **same instance**. This ensures there is never more than one webcam thread running, no matter how many times the button is clicked.

### 9.3 The Detection Loop

```
service.start()
      │
      ▼
┌──────────────────────────────────────────────────────────────────┐
│  Background Daemon Thread: _run()                                 │
│                                                                    │
│  cap = cv2.VideoCapture(0)   ← Open webcam (USB index 0)         │
│  last_update = 0                                                  │
│  INTERVAL = 3  seconds                                            │
│                                                                    │
│  ┌────────────── LOOP (while self.running) ──────────────────┐   │
│  │                                                            │   │
│  │  ret, frame = cap.read()                                  │   │
│  │  │  WHY CHECK ret? If the camera disconnects, cap.read() │   │
│  │  │  returns ret=False. We skip that frame with continue. │   │
│  │  if not ret: continue                                      │   │
│  │                                                            │   │
│  │  count, detections = detect_vehicles(frame)               │   │
│  │  │                                                        │   │
│  │  │  YOLOv8n COCO model inspects every pixel of the frame │   │
│  │  │  Classes filtered: car(2), motorcycle(3), bus(5),     │   │
│  │  │  truck(7) — everything else is ignored                │   │
│  │                                                            │   │
│  │  print("Vehicles:", count)                               │   │
│  │                                                            │   │
│  │  if time.time() - last_update > INTERVAL (3s):           │   │
│  │      update_occupied(count)   ← Firebase write           │   │
│  │      last_update = time.time()                            │   │
│  │  │                                                        │   │
│  │  │  WHY 3s INTERVAL? YOLO runs on every frame (60fps+)  │   │
│  │  │  but writing to Firebase on every frame would         │   │
│  │  │  cause rate limiting and cost. 3s interval is        │   │
│  │  │  frequent enough for a parking system without         │   │
│  │  │  hammering the database.                              │   │
│  │                                                            │   │
│  └────────────────────────────────────────────────────────────┘   │
│                                                                    │
│  service.stop() called → self.running = False                     │
│  Loop exits naturally on next iteration                           │
│  cap.release()   ← Release webcam hardware                        │
└──────────────────────────────────────────────────────────────────┘
```

### 9.4 Firebase Update — Overflow Safety

```python
# firebase_utils.py
def update_occupied(count):
    ref = db.reference("parking")
    data = ref.get() or {}
    total = data.get("total_slots", 0)

    # prevent overflow — can never exceed physical slots
    safe_count = min(count, total)

    ref.update({"occupied_slots": safe_count})
```

**Why overflow-safe?** YOLOv8 running on an overhead camera sometimes detects parked vehicles just outside the lot boundaries (on roads, neighboring lots). The `min(count, total)` cap ensures the occupied count never exceeds the physically configured total, preventing negative "available slots" on the dashboard.

---

## 10. REST API Endpoints

| Method | URL | View | Auth | Description |
|---|---|---|---|---|
| `POST` | `/upload/` | `upload_image()` | None | Plate detection + authorization check. Returns JSON result. |
| `GET` | `/vehicles/detect/start/` | `start_detection()` | None | Starts the webcam counting background thread. |
| `GET` | `/vehicles/detect/stop/` | `stop_detection()` | None | Stops the webcam counting thread. |
| `GET` | `/` | `dashboard_home()` | Session | Dashboard with live stat cards. |
| `GET` | `/vehicles/` | `vehicles_page()` | Session | List all registered authorized plates. |
| `GET/POST` | `/vehicles/add/` | `add_vehicle()` | Session | Form to register a new authorized plate. |
| `GET` | `/vehicles/delete/<plate>/` | `delete_vehicle()` | Session | Remove an authorized plate from Firebase. |
| `GET` | `/logs/` | `logs_page()` | Session | List all detection events, newest first. |
| `GET/POST` | `/slots/` | `slots_page()` | Session | View/update parking capacity in Firebase. |
| `GET/POST/DELETE` | `/admin/` | Django Admin | Staff login | Manage Django users/sessions. |

---

## 11. Dashboard & Web UI

### 11.1 Template Inheritance Architecture

All dashboard pages follow a master-child Django template inheritance pattern:

```
base_layout.html  (Master)
│   Defines: sidebar, header, CSS variables, Google Fonts,
│            Bootstrap 5.3, Font Awesome 6.5, JS clock ticker
│
├── index.html          → {% block content %} Dashboard stats + Webcam control
├── vehicles.html       → {% block content %} Authorized vehicles table
├── add_vehicle.html    → {% block content %} Registration form
├── logs.html           → {% block content %} Detection logs table
└── slots.html          → {% block content %} Slot calibration panel
```

`vehicle_detect.html` is standalone (does not extend base) as it is a dedicated full-screen webcam control console.

### 11.2 Dashboard Page: Context Variables

| Page | URL | Django View | Firebase Data Read | Template Variables |
|---|---|---|---|---|
| `index.html` | `/` | `dashboard_home` | `parking/`, `logs/`, `authorized_plates/` | `total_slots`, `occupied_slots`, `available_slots`, `unauthorized`, `total_logs`, `total_vehicles` |
| `vehicles.html` | `/vehicles/` | `vehicles_page` | `authorized_plates/` | `vehicles` (dict) |
| `add_vehicle.html` | `/vehicles/add/` | `add_vehicle` | None (POST only) | — |
| `logs.html` | `/logs/` | `logs_page` | `logs/` (reversed) | `logs` (list of dicts) |
| `slots.html` | `/slots/` | `slots_page` | `parking/` | `parking` (dict) |

### 11.3 UI Design System

The UI uses a custom glassmorphism CSS design system built into `base_layout.html`:

| CSS Variable | Value | Used For |
|---|---|---|
| `--bg-dark` | `#060913` | Body background |
| `--bg-glass` | `rgba(15, 23, 42, 0.55)` | Glass card backgrounds |
| `--primary` | `#6366f1` | Indigo accent (active states, buttons) |
| `--primary-glow` | `rgba(99, 102, 241, 0.35)` | Button glow effects |
| `--success` | `#10b981` | Authorized status, active webcam |
| `--danger` | `#f43f5e` | Unauthorized status, stop button |
| `--cyan-accent` | `#0ea5e9` | Radial dial, confidence bars |
| `--warning` | `#f59e0b` | Mid-range occupancy warning |

---

## 12. Full End-to-End Workflow Scenarios

### Scenario A: Vehicle Arrives at Entrance Gate

```
1. Vehicle approaches entrance gate
2. Entry camera captures front of vehicle
3. Camera system sends HTTP POST to server:
      POST http://server-ip:8000/upload/
      Content-Type: multipart/form-data
      image = <jpeg-bytes>

4. Server processes (< 1 second typical):
      YOLO detects plate bounding box
      Crop → Preprocess → EasyOCR reads "MH12AB1234"
      Firebase lookup: "MH12AB1234" ∈ authorized_plates?

5a. IF AUTHORIZED:
      Firebase logs/ ← push { plate, "AUTHORIZED", confidence, time }
      Response: { "plate": "MH12AB1234", "status": "AUTHORIZED" }
      → Gate controller receives 200 OK with "AUTHORIZED"
      → Boom barrier opens

5b. IF NOT AUTHORIZED:
      Firebase logs/ ← push { plate, "NOT_AUTHORIZED", confidence, time }
      Response: { "plate": "DL5SAB9999", "status": "NOT_AUTHORIZED" }
      → Gate stays closed
      → Alert triggers (if implemented on client)

6. Dashboard auto-refreshes:
      Admin sees new log entry in /logs/
      "Unauthorized" count on dashboard home increments
```

### Scenario B: Admin Monitors Parking Lot Occupancy

```
1. Admin logs into web dashboard at http://127.0.0.1:8000/
2. Navigates to Dashboard home (/)
3. Clicks "Start Detection Thread" button
4. Dashboard sends: GET /vehicles/detect/start/

5. Django spawns background daemon thread:
      cv2.VideoCapture(0) → overhead webcam
      LOOP:
          Read frame every ~30ms
          YOLOv8n detects: 12 cars, 2 buses, 1 truck
          Vehicle count = 15
          Every 3 seconds → Firebase update:
              parking/occupied_slots = min(15, 50) = 15

6. Dashboard home displays live data:
      Total Capacity: 50
      Occupied: 15
      Available: 35
      Radial Dial: 30% filled (cyan arc)

7. Admin clicks "Stop Detection Thread"
   GET /vehicles/detect/stop/
   → self.running = False
   → Thread loop exits
   → cap.release() called
   → Webcam freed
```

### Scenario C: Admin Registers a New VIP Vehicle

```
1. Admin navigates to /vehicles/add/
2. Fills form:
      Plate Number: MH04VVIP01
      Owner: CEO
      Vehicle Description: Black Mercedes S-Class
3. Clicks "Save Clearance"
4. Django POST handler runs:
      db.reference("authorized_plates").update({
          "MH04VVIP01": {
              "owner": "CEO",
              "vehicle": "Black Mercedes S-Class",
              "allowed": True,
              "created_at": "2026-05-24 15:00:00"
          }
      })
5. Redirect to /vehicles/
6. New plate appears in the vehicles table
7. From this moment, any camera detecting "MH04VVIP01" 
   will return AUTHORIZED status
```

---

## 13. Security & Credential Management

### 13.1 Firebase Credentials

The Firebase service account key (`firebase.json`) must never be committed to version control.

```
firebase/firebase.json        ← Contains Google Cloud private key
                                 Treat like a password
```

Best practices:
- Keep the file local only.
- Add to `.gitignore` before first commit.
- For production, use environment variables or Google Secret Manager instead of file-based credentials.

### 13.2 Django Secret Key

In `settings.py`, the `SECRET_KEY` should be rotated and kept in an environment variable in production:

```python
# Current (development only)
SECRET_KEY = 'django-insecure-...'

# Production approach
import os
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
```

### 13.3 CORS Policy

```python
CORS_ALLOW_ALL_ORIGINS = True
```

This allows any device on any domain to call `/upload/`. This is intentional for development, enabling Raspberry Pi, phones, and test scripts to POST images without CORS restrictions. In production, restrict to specific IP ranges of your camera hardware.

---

## 14. Key Design Decisions & Trade-offs

| Decision | Chosen Approach | Why | Trade-off |
|---|---|---|---|
| **Database** | Firebase Realtime DB | Real-time sync, accessible from any network, no extra server | Requires internet; cannot work fully offline |
| **Plate Detection** | Custom YOLO model | Much higher precision for license plates specifically | Requires custom training dataset and retraining if plate styles change |
| **Vehicle Counting** | COCO YOLOv8n | Pre-trained on cars/trucks/buses out of the box, no custom training needed | General model, may count vehicles beyond lot boundary |
| **OCR Engine** | EasyOCR | Deep learning based, more robust to perspective/lighting than Tesseract | CPU-only is slower (~400ms/image); GPU would be ~10x faster |
| **Thread Safety** | Singleton service pattern | One global instance prevents multiple webcam threads from spawning | If server restarts mid-detection, thread state is lost (must click Start again) |
| **Confidence Threshold** | 0.50 (50%) | Balance between false positives and false negatives | Blurry or distant plates near 50% may flip between accept/reject |
| **Firebase Update Interval** | 3 seconds | Prevents rate limiting, reduces Firebase write cost | Count can be up to 3 seconds stale on the dashboard |
| **OCR Substitutions** | Global O→0, I→1, S→5 | Catches most common OCR errors on plates | May incorrectly convert letters in plates that genuinely contain O, I, S |

---

## 15. Deployment Notes

### Development Setup

```bash
# 1. Navigate to project root
cd SmartVehicle/Smart/

# 2. Install all dependencies
pip install -r requirements.txt

# 3. Run migrations (for Django admin/sessions only)
python manage.py migrate

# 4. Create superuser for admin panel
python manage.py createsuperuser

# 5. Start development server
python manage.py runserver
# → http://127.0.0.1:8000/
# → Admin: http://127.0.0.1:8000/admin/
```

### Production Recommendations

| Component | Development | Production |
|---|---|---|
| Web server | Django dev server | Gunicorn + Nginx |
| Database | SQLite | PostgreSQL |
| Firebase credentials | Local file | Environment variable / Secret Manager |
| DEBUG | True | False |
| ALLOWED_HOSTS | `[]` (all) | Specific domain/IP |
| CORS | All origins | Camera hardware IPs only |
| GPU | No | Yes (10x faster inference) |

---

*End of SmartVehicle System Documentation*  
*Repository: https://github.com/AjinkyaHon9504/SmartVehicle*
