from sqlalchemy.orm import Session

from app.models.users import Users
from app.services.email_service import send_new_user_notification


def get_user_by_firebase_uid(
    db: Session,
    firebase_uid: str,
) -> Users | None:
    return (
        db.query(Users)
        .filter(Users.firebase_uid == firebase_uid)
        .first()
    )


def create_user_from_firebase(
    db: Session,
    firebase_uid: str,
    email: str,
    name: str | None = None,
) -> Users:

    existing_user = get_user_by_firebase_uid(
        db,
        firebase_uid,
    )

    if existing_user:
        return existing_user

    user = Users(
        firebase_uid=firebase_uid,
        email=email,
        name=name,
        role="user",
        status="pending",
        is_active=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    # Send approval request ONLY during registration
    send_new_user_notification(
        user_email=user.email,
        user_name=user.name,
        user_id=user.id,
    )

    return user