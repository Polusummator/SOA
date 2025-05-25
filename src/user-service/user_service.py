from fastapi import FastAPI, HTTPException, Cookie, Response
import uvicorn
import bcrypt
import datetime

import schemas
from database import UsersDB
import auth

from kafka_profucer import KafkaProducer

app = FastAPI()
db = UsersDB()
kafka_producer = KafkaProducer()

@app.post("/user/register")
def register(user: schemas.UserAuth):
    db_user = db.get_user_by_username(user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="User already exists")
    try:
        created_user = db.create_user(user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    event = {
        "event_type": "user_registered",
        "user_id": created_user["id"],
        "username": created_user["username"],
        "email": created_user["email"],
        "registration_date": created_user["created_at"],
        "metadata": {
            "source": "user-service"
        }
    }
    kafka_producer.produce(
        topic="user-events",
        key=str(created_user["id"]),
        value=event
    )
    return {"msg": "User registered"}

@app.post("/user/login")
def login(user: schemas.UserAuth, response: Response):
    db_user = db.get_user_by_username(user.username)
    if (not db_user or
        not bcrypt.checkpw(user.password.encode(), db_user.password.encode()) or
        db_user.email != user.email):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = auth.create_token(user.username)
    response.set_cookie(key="token", value=token)
    return {"msg": "Login successful", "token": token}

@app.get("/user/me/info")
def get_my_info(token: str = Cookie(None)):
    username, ok = auth.check_token(token)
    if not ok:
        raise HTTPException(status_code=401, detail="Invalid token")
    db_user = db.get_user_by_username(username)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db_profile = db.get_profile_by_userid(db_user.id)
    return {
        "id": db_user.id,
        "username": db_user.username,
        "email": db_user.email,
        "first_name": db_profile.first_name,
        "last_name": db_profile.last_name,
        "bio": db_profile.bio,
        "birthday": db_profile.birthday,
        "phone_number": db_profile.phone_number,
        "second_email": db_profile.second_email,
    }

@app.put("/user/me/info")
def update_my_info(profile: schemas.ProfileUpdate, token: str = Cookie(None)):
    username, ok = auth.check_token(token)
    if not ok:
        raise HTTPException(status_code=401, detail="Invalid token")
    db_user = db.get_user_by_username(username)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    p = schemas.Profile(**profile.model_dump(exclude_unset=True), user_id=db_user.id)
    try:
        db.update_profile(p)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"msg": "User updated"}

@app.get("/user/auth")
def auth_user(token: str = Cookie(default=None)):
    if not token:
        return None
    username, ok = auth.check_token(token)
    if not ok:
        return None
    db_user = db.get_user_by_username(username)
    if not db_user:
        return None
    return db_user.id

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)