from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.domains.chat import api as chat_api
from app.domains.chat.model import ChatResponse


def create_test_client() -> TestClient:
    app = FastAPI()
    app.include_router(chat_api.router, prefix="/api/chat")
    return TestClient(app)


def test_ask_chatbot_returns_chat_response(monkeypatch):
    class FakeChatService:
        def get_response(self, chat_request):
            return ChatResponse(message=f"Bot response to: {chat_request.message}")

    monkeypatch.setattr(chat_api, "ChatService", FakeChatService)

    client = create_test_client()

    response = client.post(
        "/api/chat/ask",
        json={
            "message": "I want chocolate",
            "history": [],
        },
    )

    assert response.status_code == 200
    assert response.json() == {"message": "Bot response to: I want chocolate"}


def test_ask_chatbot_accepts_history(monkeypatch):
    captured_request = {}

    class FakeChatService:
        def get_response(self, chat_request):
            captured_request["message"] = chat_request.message
            captured_request["history"] = chat_request.history

            return ChatResponse(message="History received")

    monkeypatch.setattr(chat_api, "ChatService", FakeChatService)

    client = create_test_client()

    response = client.post(
        "/api/chat/ask",
        json={
            "message": "What did I ask before?",
            "history": [
                {
                    "role": "user",
                    "content": "Hello",
                },
                {
                    "role": "assistant",
                    "content": "Hi, how can I help?",
                },
            ],
        },
    )

    assert response.status_code == 200
    assert response.json() == {"message": "History received"}

    assert captured_request["message"] == "What did I ask before?"
    assert len(captured_request["history"]) == 2
    assert captured_request["history"][0].role == "user"
    assert captured_request["history"][0].content == "Hello"
    assert captured_request["history"][1].role == "assistant"
    assert captured_request["history"][1].content == "Hi, how can I help?"


def test_ask_chatbot_returns_400_when_service_raises_value_error(monkeypatch):
    class FakeChatService:
        def get_response(self, chat_request):
            raise ValueError("Invalid customer data")

    monkeypatch.setattr(chat_api, "ChatService", FakeChatService)

    client = create_test_client()

    response = client.post(
        "/api/chat/ask",
        json={
            "message": "Hello",
            "history": [],
        },
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid customer data"}


def test_ask_chatbot_returns_500_when_service_raises_unexpected_error(monkeypatch):
    class FakeChatService:
        def get_response(self, chat_request):
            raise RuntimeError("OpenAI failed")

    monkeypatch.setattr(chat_api, "ChatService", FakeChatService)

    client = create_test_client()

    response = client.post(
        "/api/chat/ask",
        json={
            "message": "Hello",
            "history": [],
        },
    )

    assert response.status_code == 500
    assert response.json() == {
        "detail": "Something went wrong while generating the chatbot response."
    }


def test_ask_chatbot_returns_422_when_message_is_empty():
    client = create_test_client()

    response = client.post(
        "/api/chat/ask",
        json={
            "message": "",
            "history": [],
        },
    )

    assert response.status_code == 422


def test_ask_chatbot_returns_422_for_invalid_history_role():
    client = create_test_client()

    response = client.post(
        "/api/chat/ask",
        json={
            "message": "Hello",
            "history": [
                {
                    "role": "bot",
                    "content": "Invalid role",
                }
            ],
        },
    )

    assert response.status_code == 422
