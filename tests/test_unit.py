"""Unit tests for Lab 4 CI/CD pipeline gate 1."""
import os
import tempfile
import pytest
from app.app import app


@pytest.fixture
def client(monkeypatch):
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    monkeypatch.setattr("app.app.DB_PATH", path)
    monkeypatch.setattr("app.app.SIMULATE_ERROR_RATE", 0.0)
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c
    if os.path.exists(path):
        os.remove(path)


def test_health_returns_up(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.get_json()["status"] == "UP"


def test_root_contains_version_and_slot(client):
    res = client.get("/")
    assert res.status_code == 200
    body = res.get_json()
    assert "version" in body and "slot" in body


def test_create_item_rejects_empty_name(client):
    res = client.post("/items", json={"name": "   "})
    assert res.status_code == 400


def test_secret_check_never_exposes_plaintext(client, monkeypatch):
    monkeypatch.setattr("app.app.API_SECRET_KEY", "super-secret-value-123")
    res = client.get("/secret-check")
    assert res.status_code == 200
    text = res.get_data(as_text=True)
    assert "super-secret-value-123" not in text
    assert res.get_json()["configured"] is True
