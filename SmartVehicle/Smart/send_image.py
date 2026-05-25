"""
SmartVehicle - Image Sender (simulates ESP32 / camera module)
Sends the image to POST /upload/ exactly as real hardware would.

Run:   python send_image.py C:\path\to\your\image.jpg
"""

import sys
import io
import requests

# Fix Windows terminal encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SERVER   = "http://127.0.0.1:8000"
ENDPOINT = f"{SERVER}/upload/"

# Accept image path from command line, or fall back to default
if len(sys.argv) > 1:
    IMAGE = sys.argv[1]
else:
    IMAGE = "test_plate.jpg"

LINE = "-" * 45

print(f"\n{LINE}")
print(f"   SmartVehicle -- Sending image to server")
print(f"{LINE}\n")
print(f"  Endpoint : {ENDPOINT}")
print(f"  Image    : {IMAGE}\n")

try:
    with open(IMAGE, "rb") as f:
        print(f"  Sending POST request ...")
        response = requests.post(
            ENDPOINT,
            files={"image": (IMAGE, f, "image/jpeg")}
        )

    data = response.json()

    plate  = data.get("plate",      "N/A")
    status = data.get("status",     "N/A")
    conf   = data.get("confidence", None)

    print(f"\n{LINE}")
    print(f"  HTTP Status  : {response.status_code}")
    print(f"  Plate Text   : {plate}")
    if conf:
        print(f"  Confidence   : {float(conf)*100:.1f}%")

    if status == "AUTHORIZED":
        print(f"  Result       : *** AUTHORIZED *** -> Gate OPEN")
    elif status == "NOT_AUTHORIZED":
        print(f"  Result       : *** NOT AUTHORIZED *** -> Gate CLOSED")
    else:
        print(f"  Result       : {status}")

    print(f"\n  Full response : {data}")
    print(f"{LINE}\n")
    print(f"  Log written to Firebase -> check /logs/ on dashboard\n")

except FileNotFoundError:
    print(f"\n  ERROR: '{IMAGE}' not found.")
    print(f"  Save the plate image as 'test_plate.jpg' here:")
    print(f"  c:\\Users\\ajink\\OneDrive\\Desktop\\SmartVehicle\\SmartVehicle\\Smart\\\n")

except requests.exceptions.ConnectionError:
    print(f"\n  ERROR: Cannot connect to server at {SERVER}")
    print(f"  Make sure Django server is running:")
    print(f"  python manage.py runserver\n")

