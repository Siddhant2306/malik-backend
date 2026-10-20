import logging

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.users import Users
from app.services.email_service import send_new_user_notification

logger = logging.getLogger(__name__)


class UserAlreadyRegisteredError(ValueError):
    """Raised when a concurrent registration wins the unique-key race."""


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
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise UserAlreadyRegisteredError("User is already registered.") from error
    db.refresh(user)

    # A mail provider outage must not roll back a successfully-created pending
    # account. Administrators can still see the request in the approval queue.
    try:
        send_new_user_notification(
            user_email=user.email,
            user_name=user.name,
            user_id=user.id,
        )
    except Exception:
        logger.exception("Could not send approval notification for user %s.", user.id)

    return user
