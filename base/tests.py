import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from base.models import Supplier

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def test_user(db):
    user = User.objects.create_user(username="testuser", password="password123")
    return user

@pytest.fixture
def auth_client(api_client, test_user):
    # Obtain token via your login endpoint
    response = api_client.post("/login/", {"username": "testuser", "password": "password123"}, format="json")
    token = response.data.get("access")  # assuming JWT returns 'access'
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return api_client

@pytest.fixture
def supplier(db, test_user):
    return Supplier.objects.create(
        tpin=123456,
        name="Test Supplier",
        address="123 Test Street",
        created_by=test_user
    )

# ------------------ TESTS ------------------

def test_get_suppliers(auth_client, supplier):
    response = auth_client.get("/suppliers/")
    assert response.status_code == 200
    assert response.data["status"] == "success"
    assert any(s["name"] == "Test Supplier" for s in response.data["data"])

def test_create_supplier(auth_client):
    data = {
        "tpin": 654321,
        "name": "New Supplier",
        "address": "456 Another Street"
    }
    response = auth_client.post("/suppliers/", data, format="json")
    assert response.status_code == 201
    assert response.data["status"] == "success"
    assert Supplier.objects.filter(name="New Supplier").exists()

def test_update_supplier(auth_client, supplier):
    data = {"address": "Updated Address"}
    url = f"/suppliers/{supplier.id}/"
    response = auth_client.put(url, data, format="json")
    assert response.status_code == 200
    supplier.refresh_from_db()
    assert supplier.address == "Updated Address"

def test_delete_supplier(auth_client, supplier):
    url = f"/suppliers/{supplier.id}/"
    response = auth_client.delete(url)
    assert response.status_code == 204
    assert not Supplier.objects.filter(id=supplier.id).exists()
