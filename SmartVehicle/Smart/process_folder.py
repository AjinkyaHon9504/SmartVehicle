"""
SmartVehicle — Batch Image Processing
Sends all valid license plate images in the specified folder to the
POST /upload/ endpoint to test OCR and Firebase authorization.

Run: python process_folder.py
"""

import os
import sys
import io
import requests

# Fix Windows terminal encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SERVER = "http://127.0.0.1:8000"
ENDPOINT = f"{SERVER}/upload/"
FOLDER = r"C:\Users\ajink\OneDrive\Desktop\SmartVehicle\imagesnumberplate"

LINE = "=" * 65

def process():
    print(f"\n{LINE}")
    print(f"   SmartVehicle — Batch Folder Processing Test")
    print(f"{LINE}\n")
    print(f"  Target Folder : {FOLDER}")
    print(f"  Endpoint      : {ENDPOINT}\n")

    if not os.path.exists(FOLDER):
        print(f"  ERROR: Folder '{FOLDER}' does not exist.")
        return

    # Find valid image files
    valid_extensions = (".jpg", ".jpeg", ".png", ".webp")
    images = [
        f for f in os.listdir(FOLDER)
        if f.lower().endswith(valid_extensions)
    ]

    if not images:
        print("  No valid images found in the target folder.")
        return

    print(f"  Found {len(images)} images to process. Starting batch runs...\n")

    for i, img_name in enumerate(images, 1):
        img_path = os.path.join(FOLDER, img_name)
        print(f"  [{i}/{len(images)}] Processing: {img_name}")

        try:
            with open(img_path, "rb") as f:
                response = requests.post(
                    ENDPOINT,
                    files={"image": (img_name, f, "image/jpeg")}
                )

            if response.status_code == 200:
                data = response.json()
                plate = data.get("plate", "N/A")
                status = data.get("status", "N/A")
                conf = data.get("confidence", None)

                conf_str = f"{float(conf)*100:.1f}%" if conf is not None else "N/A"
                
                status_color = "🟢 AUTHORIZED" if status == "AUTHORIZED" else "🔴 NOT_AUTHORIZED"
                
                print(f"      ↳ Detected  : {plate} ({conf_str})")
                print(f"      ↳ Result    : {status_color}")
            else:
                print(f"      ↳ ERROR     : Server returned status code {response.status_code}")
                try:
                    print(f"      ↳ Detail    : {response.text[:200]}")
                except Exception:
                    pass

        except requests.exceptions.ConnectionError:
            print(f"      ↳ ERROR     : Cannot connect to server at {SERVER}. Make sure Django is running.")
            break
        except Exception as e:
            print(f"      ↳ ERROR     : {str(e)}")

        print()

    print(f"{LINE}\n  Batch processing completed.\n")

if __name__ == "__main__":
    process()
