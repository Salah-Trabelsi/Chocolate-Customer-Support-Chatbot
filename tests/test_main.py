from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_root_endpoint_returns_api_status_message():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "Chocolate Customer Support API is running 🍫"
    }