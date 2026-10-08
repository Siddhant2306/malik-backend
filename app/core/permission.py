from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_firebase_user
from app.db.session import get_db
from app.services.auth_service import get_current_db_user


def get_current_admin(
    firebase_user: dict = Depends(get_current_firebase_user),
    db: Session = Depends(get_db),
):
    user = get_current_db_user(
        db=db,
        firebase_user=firebase_user,
    )

    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    return user