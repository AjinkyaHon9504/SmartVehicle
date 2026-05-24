import firebase_admin

from firebase_admin import credentials
from firebase_admin import db


# Prevent duplicate initialization
if not firebase_admin._apps:

    cred = credentials.Certificate(
        "firebase/firebase.json"
    )

    firebase_admin.initialize_app(cred, {
        "databaseURL":
        "https://carmanagement-5b8f2-default-rtdb.asia-southeast1.firebasedatabase.app/"
    })

    print("[OK] Firebase Initialized")