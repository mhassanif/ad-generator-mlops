"""
Basic tests for API functionality
"""
import pytest
from src.api.app import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_health_endpoint():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "model_loaded" in data


def test_predict_endpoint():
    """Test prediction endpoint with valid input"""
    payload = {
        "brand": "Nike",
        "product_name": "Running Shoes"
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "ad_creative" in data
    assert len(data["ad_creative"]) > 0


def test_predict_missing_brand():
    """Test prediction endpoint with missing brand"""
    payload = {
        "product_name": "Running Shoes"
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 422  # Validation error


def test_metrics_endpoint():
    """Test that metrics endpoint is accessible"""
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "api_predictions_total" in response.text
