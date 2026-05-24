import cv2
import threading
import time

from app.services.vehicle_service import detect_vehicles
from .firebase_utils import update_occupied


class VehicleCounterService:

    def __init__(self):
        self.running = False
        self.thread = None

    def start(self):

        if self.running:
            return

        self.running = True
        self.thread = threading.Thread(target=self._run)
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        self.running = False

    def _run(self):

        cap = cv2.VideoCapture(0)

        last_update = 0
        INTERVAL = 3

        while self.running:

            ret, frame = cap.read()

            if not ret:
                continue

            count, _ = detect_vehicles(frame)

            print("Vehicles:", count)

            # update firebase continuously
            if time.time() - last_update > INTERVAL:
                update_occupied(count)
                last_update = time.time()

        cap.release()


# GLOBAL INSTANCE (IMPORTANT)
service = VehicleCounterService()