from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.users import Users


def get_current_db_user(
    db: Session,
    firebase_user: dict,
) -> Users:
    firebase_uid = firebase_user["uid"]

    user = (
        db.query(Users)
        .filter(Users.firebase_uid == firebase_uid)
        .first()
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User account not found",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    return user