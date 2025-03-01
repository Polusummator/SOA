from jose import jwt, JWTError
import secrets
from datetime import datetime, timedelta

SECRET_KEY = secrets.token_urlsafe(32)
ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 30

def create_token(username: str):
    token_expires = datetime.now() + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    data = {
        "username": username,
        "exp": token_expires.timestamp(),
    }
    token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    return token

def check_token(token: str):
    if not token:
        return None, False
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("username")
    except JWTError:
        return None, False
    return username, True