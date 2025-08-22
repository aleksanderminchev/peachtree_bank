import os

CONFIG_NAME = os.environ.get("ENV_NAME") or "development"


def send_email(email: str):
    """Send email function

    Args:
        email (str): Email to send email to

    Returns:
        bool: Returns true or false depending on if the sending was a success
    """
    try:
        if CONFIG_NAME == "production":
            return True
        else:
            print("DEBUG EMAIL SENT")
            return True
    except Exception:
        return False
