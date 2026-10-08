from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.permission import get_current_admin
from app.db.session import get_db
from app.models.users import Users

router = APIRouter(
    prefix="/api/v1/admin/users",
    tags=["Admin Users"],
)


@router.get("")
def get_users(
    admin: Users = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    users = (
        db.query(Users)
        .order_by(Users.created_at.desc())
        .all()
    )

    return [
        {
            "id": user.id,
            "firebase_uid": user.firebase_uid,
            "email": user.email,
            "name": user.name,
            "role": user.role,
            "status": user.status,
            "is_active": user.is_active,
            "created_at": user.created_at,
        }
        for user in users
    ]


@router.post("/{user_id}/approve")
def approve_user(
    user_id: int,
    admin: Users = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    user = db.query(Users).filter(Users.id == user_id).first()

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    user.status = "approved"
    user.is_active = True

    db.commit()
    db.refresh(user)

    return {
        "message": "User approved successfully",
        "user_id": user.id,
        "status": user.status,
    }


@router.post("/{user_id}/reject")
def reject_user(
    user_id: int,
    admin: Users = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    user = db.query(Users).filter(Users.id == user_id).first()

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    user.status = "rejected"

    db.commit()
    db.refresh(user)

    return {
        "message": "User rejected successfully",
        "user_id": user.id,
        "status": user.status,
    }