import os
import resend

resend.api_key = os.getenv("RESEND_API_KEY")


def send_new_user_notification(
    user_email: str,
    user_name: str | None,
    user_id: int,
):
    admin_email = os.getenv("ADMIN_EMAIL")
    email_from = os.getenv("EMAIL_FROM")

    if not admin_email:
        raise RuntimeError("ADMIN_EMAIL is not configured")

    if not email_from:
        raise RuntimeError("EMAIL_FROM is not configured")

    name = user_name or "New user"

    params: resend.Emails.SendParams = {
        "from": email_from,
        "to": [admin_email],
        "subject": "New MALIK user approval request",
        "html": f"""
        <h2>New MALIK User</h2>

        <p>A new user is requesting access to MALIK.</p>

        <p>
            <strong>Name:</strong> {name}<br>
            <strong>Email:</strong> {user_email}<br>
            <strong>User ID:</strong> {user_id}
        </p>

        <p>
            Please open the MALIK admin panel to approve or reject this user.
        </p>
        """,
    }

    return resend.Emails.send(params)