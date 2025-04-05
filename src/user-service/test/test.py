import pytest
from fastapi.testclient import TestClient
from user_service import app
from database import UsersDB

client = TestClient(app)

@pytest.fixture(autouse=True)
def clean_db():
    db = UsersDB()
    db.delete_all_users()
    yield

def test_register_user():
    response = client.post("/user/register", json={"username": "testuser", "password": "testpass", "email": "test@example.com"})
    assert response.status_code == 200
    assert response.json() == {"msg": "User registered"}

def test_register_existing_user():
    client.post("/user/register", json={"username": "testuser", "password": "testpass", "email": "test@example.com"})
    response = client.post("/user/register", json={"username": "testuser", "password": "testpass", "email": "test@example.com"})
    assert response.status_code == 400
    assert response.json() == {"detail": "User already exists"}

def test_register_user_existing_email():
    client.post("/user/register", json={"username": "testuser", "password": "testpass", "email": "test@example.com"})
    response = client.post("/user/register", json={"username": "newuser", "password": "testpass", "email": "test@example.com"})
    assert response.status_code == 400
    assert response.json() == {"detail": "Username/email already exists"}

def test_login_user():
    client.post("/user/register", json={"username": "testuser", "password": "testpass", "email": "test@example.com"})
    response = client.post("/user/login", json={"username": "testuser", "password": "testpass", "email": "test@example.com"})
    assert response.status_code == 200
    assert "token" in response.cookies

def test_login_invalid_credentials():
    response = client.post("/user/login", json={"username": "wronguser", "password": "wrongpass", "email": "wrong@example.com"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid credentials"}

def test_get_my_info():
    client.post("/user/register", json={"username": "testuser", "password": "testpass", "email": "test@example.com"})
    login_response = client.post("/user/login", json={"username": "testuser", "password": "testpass", "email": "test@example.com"})
    token = login_response.cookies.get("token")
    response = client.get("/user/me/info", cookies={"token": token})
    assert response.status_code == 200
    assert "username" in response.json()

def test_update_my_info():
    client.post("/user/register", json={"username": "testuser", "password": "testpass", "email": "test@example.com"})
    login_response = client.post("/user/login", json={"username": "testuser", "password": "testpass", "email": "test@example.com"})
    token = login_response.cookies.get("token")
    response = client.put("/user/me/info", json={"first_name": "NewName"}, cookies={"token": token})
    assert response.status_code == 200
    assert response.json() == {"msg": "User updated"}

def test_update_and_read_my_info():
    client.post("/user/register", json={"username": "testuser", "password": "testpass", "email": "test@example.com"})
    login_response = client.post("/user/login", json={"username": "testuser", "password": "testpass", "email": "test@example.com"})
    token = login_response.cookies.get("token")
    client.put("/user/me/info", json={"first_name": "NewName"}, cookies={"token": token})
    response = client.get("/user/me/info", cookies={"token": token})
    assert response.status_code == 200
    assert response.json()["first_name"] == "NewName"

# Invalid token tests

def test_get_my_info_invalid_token():
    response = client.get("/user/me/info", cookies={"token": "invalid-token"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid token"}

def test_update_my_info_invalid_token():
    response = client.put("/user/me/info", json={"first_name": "NewName"}, cookies={"token": "invalid-token"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid token"}

# Pydantic checks

def test_register_user_invalid_email():
    response = client.post("/user/register", json={"username": "testuser", "password": "testpass", "email": "invalid-email"})
    assert response.status_code == 422

def test_register_user_invalid_username():
    response = client.post("/user/register", json={"username": "a" * 51, "password": "testpass", "email": "test@example.com"})
    assert response.status_code == 422

def test_update_my_info_invalid_phone():
    client.post("/user/register", json={"username": "testuser", "password": "testpass", "email": "test@example.com"})
    login_response = client.post("/user/login", json={"username": "testuser", "password": "testpass", "email": "test@example.com"})
    token = login_response.cookies.get("token")
    response = client.put("/user/me/info", json={"phone_number": "invalid-phone"}, cookies={"token": token})
    assert response.status_code == 422

def test_update_my_info_invalid_first_name():
    client.post("/user/register", json={"username": "testuser", "password": "testpass", "email": "test@example.com"})
    login_response = client.post("/user/login", json={"username": "testuser", "password": "testpass", "email": "test@example.com"})
    token = login_response.cookies.get("token")
    response = client.put("/user/me/info", json={"first_name": "a" * 51}, cookies={"token": token})
    assert response.status_code == 422

def test_update_my_info_invalid_last_name():
    client.post("/user/register", json={"username": "testuser", "password": "testpass", "email": "test@example.com"})
    login_response = client.post("/user/login", json={"username": "testuser", "password": "testpass", "email": "test@example.com"})
    token = login_response.cookies.get("token")
    response = client.put("/user/me/info", json={"last_name": "a" * 51}, cookies={"token": token})
    assert response.status_code == 422

def test_update_my_info_invalid_second_email():
    client.post("/user/register", json={"username": "testuser", "password": "testpass", "email": "test@example.com"})
    login_response = client.post("/user/login", json={"username": "testuser", "password": "testpass", "email": "test@example.com"})
    token = login_response.cookies.get("token")
    response = client.put("/user/me/info", json={"second_email": "invalid-email"}, cookies={"token": token})
    assert response.status_code == 422

def test_update_my_info_invalid_birthday():
    client.post("/user/register", json={"username": "testuser", "password": "testpass", "email": "test@example.com"})
    login_response = client.post("/user/login", json={"username": "testuser", "password": "testpass", "email": "test@example.com"})
    token = login_response.cookies.get("token")
    response = client.put("/user/me/info", json={"birthday": "invalid-date"}, cookies={"token": token})
    assert response.status_code == 422

def test_update_my_info_invalid_bio():
    client.post("/user/register", json={"username": "testuser", "password": "testpass", "email": "test@example.com"})
    login_response = client.post("/user/login", json={"username": "testuser", "password": "testpass", "email": "test@example.com"})
    token = login_response.cookies.get("token")
    response = client.put("/user/me/info", json={"bio": "a" * 251}, cookies={"token": token})
    assert response.status_code == 422


def test_auth_user_valid_token():
    client.post("/user/register", json={"username": "testuser0", "password": "testpass", "email": "test0@example.com"})
    login_response = client.post("/user/login", json={"username": "testuser0", "password": "testpass", "email": "test0@example.com"})
    token = login_response.cookies.get("token")
    response = client.get("/user/auth", cookies={"token": token})
    assert response.status_code == 200
    assert isinstance(response.json(), int)


def test_auth_user_invalid_token():
    response = client.get("/user/auth", cookies={"token": "invalid-token"})
    assert response.status_code == 200
    assert response.json() is None


def test_auth_user_no_token():
    response = client.get("/user/auth")
    assert response.status_code == 200
    assert response.json() is None
