import logging

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from firebase_admin import auth

from app.core.firebase import initialize_firebase

security = HTTPBearer()
logger = logging.getLogger(__name__)

initialize_firebase()


def get_current_firebase_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    token = credentials.credentials

    try:
        decoded_token = auth.verify_id_token(token)

        return decoded_token

    except Exception:
        logger.warning("Firebase token verification failed.")

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token",
        )
