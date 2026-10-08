from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_firebase_user
from app.db.session import get_db
from app.services.user_service import get_user_by_firebase_uid, create_user_from_firebase

router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Authentication"],
)


@router.get("/me")
def get_current_user(
    firebase_user: dict = Depends(get_current_firebase_user),
    db: Session = Depends(get_db),
):
    firebase_uid = firebase_user["uid"]

    user = get_user_by_firebase_uid(
        db,
        firebase_uid,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User account is not registered.",
        )

    return {
        "id": user.id,
        "firebase_uid": user.firebase_uid,
        "email": user.email,
        "name": user.name,
        "role": user.role,
        "status": user.status,
        "is_active": user.is_active,
    }

@router.post("/register")
def register_user(
    firebase_user: dict = Depends(get_current_firebase_user),
    db: Session = Depends(get_db),
):
    firebase_uid = firebase_user["uid"]
    email = firebase_user.get("email")
    name = firebase_user.get("name")

    if not email:
        raise HTTPException(
            status_code=400,
            detail="Firebase account does not contain an email.",
        )

    existing_user = get_user_by_firebase_uid(
        db,
        firebase_uid,
    )

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="User is already registered.",
        )

    user = create_user_from_firebase(
        db=db,
        firebase_uid=firebase_uid,
        email=email,
        name=name,
    )

    return {
        "message": "Registration successful. Waiting for admin approval.",
        "id": user.id,
        "email": user.email,
        "status": user.status,
    }