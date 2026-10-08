import os

import firebase_admin
from firebase_admin import credentials


def initialize_firebase():
    if firebase_admin._apps:
        return

    firebase_project_id = os.getenv("FIREBASE_PROJECT_ID")
    firebase_client_email = os.getenv("FIREBASE_CLIENT_EMAIL")
    firebase_private_key = os.getenv("FIREBASE_PRIVATE_KEY")

    if firebase_project_id and firebase_client_email and firebase_private_key:
        # Production: Render environment variables
        cred = credentials.Certificate({
            "type": "service_account",
            "project_id": firebase_project_id,
            "private_key": firebase_private_key.replace("\\n", "\n"),
            "client_email": firebase_client_email,
        })
    else:
        # Local development
        cred = credentials.Certificate(
            "firebase-service-account.json"
        )

    firebase_admin.initialize_app(cred)