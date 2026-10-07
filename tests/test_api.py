"""
API integration tests for FastAPI backend
"""

import pytest
import sys
from pathlib import Path
from starlette.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_models_list_endpoint():
    response = client.get("/api/v1/models/")
    assert response.status_code == 200
    models = response.json()
    assert len(models) >= 3
    types = [m["type"] for m in models]
    assert "random_forest" in types
    assert "xgboost" in types
    assert "lstm" in types


def test_auth_demo_me():
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 200
    user = response.json()
    assert "email" in user
