"""
Vastarion Garage — API Test Suite
Tests: Auth, Vehicles, Service Records, Users
Uses SQLite in-memory DB (no PostgreSQL needed)
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from main import app

# --- In-memory SQLite setup ---
SQLALCHEMY_TEST_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_TEST_URL, connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

# --- Fixtures ---
@pytest.fixture(autouse=True)
def reset_db():
    """Her testten önce veritabanını sıfırla."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def signup_user(email="test@vastarion.com", password="Test123"):
    return client.post("/auth/signup", json={"email": email, "password": password})


def login_user(email="test@vastarion.com", password="Test123"):
    return client.post("/auth/login", data={"username": email, "password": password})


def auth_header(email="test@vastarion.com", password="Test123"):
    signup_user(email, password)
    resp = login_user(email, password)
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# ==================== AUTH TESTS ====================

class TestAuth:
    def test_signup_success(self):
        resp = signup_user()
        assert resp.status_code == 200
        data = resp.json()
        assert data["email"] == "test@vastarion.com"
        assert "id" in data

    def test_signup_duplicate_email(self):
        signup_user()
        resp = signup_user()  # aynı email
        assert resp.status_code == 400

    def test_signup_weak_password_no_digit(self):
        resp = client.post("/auth/signup", json={"email": "a@b.com", "password": "abcdef"})
        assert resp.status_code == 422  # validation error

    def test_signup_short_password(self):
        resp = client.post("/auth/signup", json={"email": "a@b.com", "password": "Ab1"})
        assert resp.status_code == 422

    def test_login_success(self):
        signup_user()
        resp = login_user()
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self):
        signup_user()
        resp = login_user(password="WrongPass1")
        assert resp.status_code == 400

    def test_login_nonexistent_user(self):
        resp = login_user(email="ghost@vastarion.com")
        assert resp.status_code == 400


# ==================== VEHICLE TESTS ====================

class TestVehicles:
    VEHICLE = {
        "vin": "WBAPH5C55BA123456",
        "brand": "BMW",
        "model": "M5 CS",
        "year": 2024,
        "mileage": 1500,
        "color": "Obsidian Black"
    }

    def test_create_vehicle(self):
        headers = auth_header()
        resp = client.post("/vehicles/", json=self.VEHICLE, headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["vin"] == self.VEHICLE["vin"]
        assert data["brand"] == "BMW"

    def test_list_my_vehicles(self):
        headers = auth_header()
        client.post("/vehicles/", json=self.VEHICLE, headers=headers)
        resp = client.get("/vehicles/my-vehicles", headers=headers)
        assert resp.status_code == 200
        vehicles = resp.json()
        assert len(vehicles) == 1
        assert vehicles[0]["brand"] == "BMW"

    def test_update_vehicle(self):
        headers = auth_header()
        client.post("/vehicles/", json=self.VEHICLE, headers=headers)
        resp = client.put(
            f"/vehicles/{self.VEHICLE['vin']}",
            json={"mileage": 5000, "color": "Arctic Silver"},
            headers=headers
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["mileage"] == 5000
        assert data["color"] == "Arctic Silver"

    def test_delete_vehicle(self):
        headers = auth_header()
        client.post("/vehicles/", json=self.VEHICLE, headers=headers)
        resp = client.delete(f"/vehicles/{self.VEHICLE['vin']}", headers=headers)
        assert resp.status_code == 200

        # Silindikten sonra listede olmamalı
        resp = client.get("/vehicles/my-vehicles", headers=headers)
        assert len(resp.json()) == 0

    def test_create_vehicle_unauthorized(self):
        resp = client.post("/vehicles/", json=self.VEHICLE)
        assert resp.status_code == 401


# ==================== USERS TESTS ====================

class TestUsers:
    def test_get_current_user(self):
        headers = auth_header()
        resp = client.get("/users/me", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["email"] == "test@vastarion.com"
        assert "created_at" in data

    def test_get_current_user_unauthorized(self):
        resp = client.get("/users/me")
        assert resp.status_code == 401


# ==================== HEALTHCHECK ====================

class TestHealthcheck:
    def test_root(self):
        resp = client.get("/")
        assert resp.status_code == 200
        assert "message" in resp.json()