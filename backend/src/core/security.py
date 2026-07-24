from datetime import datetime, timedelta, timezone

import bcrypt
from jose import jwt

from backend.src.core.config import settings


# Hashing and verifying passwords using bcrypt
def hash_password(plain_password: str) -> str:
    # Receives a text password and returns the hashed
    password_bytes = plain_password.encode("utf-8")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password_bytes, salt).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Verify if the provided plain password matches the hashed password
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8")
        )
    except ValueError:
        return False

# JWT token generation and verification
def create_access_token(user_id: str, role: str) -> str:
    """generate a JWT token with user_id and role as payload, with expiration time."""
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {
        "sub": user_id,
        "role": role,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    """Decode and verify the JWT token, returning the payload if valid."""
    return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
