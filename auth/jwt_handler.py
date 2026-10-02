import os
import secrets
import time

from jose import jwt

SECRET_KEY = os.getenv("SECRET_KEY") or secrets.token_urlsafe(32)
ALGORITHM = "HS256"

def create_access_token(
    user: str,
    expires_in: int = 3600,
    mfa_verified: bool = False,
    token_type: str = "access",
    actor_type: str = "user",
    role: str = None,
    scopes: list = None,
):
    payload = {
        "user": user,
        "sub": user,
        "expires": time.time() + expires_in,
        "mfa_verified": mfa_verified,
        "token_type": token_type,
        "actor_type": actor_type,
        "scope": " ".join(scopes or []),
    }
    if role:
        payload["role"] = role
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_access_token(token: str):
    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        expire = data.get("expires")
        if expire is None or expire < time.time():
            return None
        return data
    except Exception:
        return None
