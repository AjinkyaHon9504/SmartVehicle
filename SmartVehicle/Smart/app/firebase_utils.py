from firebase_admin import db


def update_occupied(count):

    ref = db.reference("parking")

    data = ref.get() or {}

    total = data.get("total_slots", 0)

    # prevent overflow
    safe_count = min(count, total)

    ref.update({
        "occupied_slots": safe_count
    })