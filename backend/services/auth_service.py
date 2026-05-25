import bcrypt
import jwt

from datetime import datetime, timedelta

SECRET_KEY = "resume_analyzer_secret_key"

def hash_password(password: str):

    salt = bcrypt.gensalt()

    hashed = bcrypt.hashpw(
        password.encode("utf-8"),
        salt
    )

    return hashed.decode("utf-8")


def verify_password(
    plain_password: str,
    hashed_password: str
):

    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )


def create_access_token(data: dict):

    payload = data.copy()

    payload["exp"] = datetime.utcnow() + timedelta(days=1)

    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm="HS256"
    )

    return token