from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_firebase_user
from app.db.session import get_db
from app.models.users import Users


def get_current_approved_user(
    firebase_user: dict = Depends(get_current_firebase_user),
    db: Session = Depends(get_db),
) -> Users:
    firebase_uid = firebase_user.get("uid")

    if not firebase_uid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Firebase token",
        )

    user = (
        db.query(Users)
        .filter(Users.firebase_uid == firebase_uid)
        .first()
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not registered",
        )

    if user.status != "approved" or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is not approved or active",
        )

    return user


def get_current_admin(
    user: Users = Depends(get_current_approved_user),
) -> Users:
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    return user