from django.shortcuts import render, redirect

from firebase_admin import db

from datetime import datetime


# DASHBOARD HOME
def dashboard_home(request):

    parking = db.reference("parking").get() or {}

    logs = db.reference("logs").get() or {}

    authorized = db.reference("authorized_plates").get() or {}

    unauthorized_count = 0

    for key, value in logs.items():

        if value.get("status") == "NOT_AUTHORIZED":
            unauthorized_count += 1

    context = {

        "total_slots": parking.get("total_slots", 0),

        "occupied_slots": parking.get("occupied_slots", 0),

        "available_slots":
            parking.get("total_slots", 0)
            - parking.get("occupied_slots", 0),

        "total_logs": len(logs),

        "unauthorized": unauthorized_count,

        "total_vehicles": len(authorized)
    }

    return render(request, "dashboard/index.html", context)


# VIEW VEHICLES
def vehicles_page(request):

    vehicles = db.reference("authorized_plates").get() or {}

    return render(request, "dashboard/vehicles.html", {
        "vehicles": vehicles
    })


# ADD VEHICLE
def add_vehicle(request):

    if request.method == "POST":

        plate = request.POST.get("plate")
        owner = request.POST.get("owner")
        vehicle = request.POST.get("vehicle")

        db.reference("authorized_plates").update({

            plate: {

                "owner": owner,

                "vehicle": vehicle,

                "allowed": True,

                "created_at":
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        })

        return redirect("vehicles")

    return render(request, "dashboard/add_vehicle.html")


# DELETE VEHICLE
def delete_vehicle(request, plate):

    db.reference(f"authorized_plates/{plate}").delete()

    return redirect("vehicles")


# LOGS PAGE
def logs_page(request):

    logs = db.reference("logs").get() or {}

    logs_list = []

    for key, value in logs.items():

        logs_list.append(value)

    logs_list.reverse()

    return render(request, "dashboard/logs.html", {

        "logs": logs_list
    })


# SLOT PAGE
def slots_page(request):

    parking = db.reference("parking").get() or {}

    if request.method == "POST":

        total_slots = int(
            request.POST.get("total_slots")
        )

        occupied_slots = int(
            request.POST.get("occupied_slots")
        )

        db.reference("parking").set({

            "total_slots": total_slots,

            "occupied_slots": occupied_slots
        })

        return redirect("slots")

    return render(request, "dashboard/slots.html", {

        "parking": parking
    })