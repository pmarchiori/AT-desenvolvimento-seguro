import time

from jose import jwt

#chave secreta
SECRET_KEY = "chave_secreta"

def create_access_token(user: str):
    payload = {"user": user, "expires": time.time() + 3600}
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def verify_access_token(token: str):
    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        expire = data.get("expires")
        if expire is None or expire < time.time():
            return None
        return data
    except Exception:
        return None
