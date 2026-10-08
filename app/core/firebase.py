import os

import firebase_admin
from firebase_admin import credentials


def initialize_firebase():
    if firebase_admin._apps:
        return

    if os.path.exists("/etc/secrets/firebase-service-account.json"):
        cred = credentials.Certificate(
            "/etc/secrets/firebase-service-account.json"
        )
    else:
        cred = credentials.Certificate(
            "firebase-service-account.json"
        )

    firebase_admin.initialize_app(cred)