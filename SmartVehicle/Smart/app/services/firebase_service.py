from firebase_admin import db
from datetime import datetime


# check authorization
def check_plate(plate):
    ref = db.reference("authorized_plates")
    data = ref.get() or {}

    return plate in data


# add logs
def add_log(plate, status):
    ref = db.reference("logs")
    new_ref = ref.push()

    new_ref.set({
        "plate": plate,
        "status": status,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })


# update slots
def update_slots(count):
    db.reference("parking/occupied_slots").set(count)