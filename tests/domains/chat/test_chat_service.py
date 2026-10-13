from langchain_core.messages import AIMessage, HumanMessage

from app.domains.chat import service as chat_service_module
from app.domains.chat.model import ChatHistoryMessage, ChatRequest
from app.domains.chat.service import ChatService


def test_convert_history_to_messages_converts_user_and_assistant_messages():
    service = ChatService()

    history = [
        ChatHistoryMessage(
            role="user",
            content="Hello",
        ),
        ChatHistoryMessage(
            role="assistant",
            content="Hi, how can I help?",
        ),
    ]

    result = service._convert_history_to_messages(history)

    assert len(result) == 2

    assert isinstance(result[0], HumanMessage)
    assert result[0].content == "Hello"

    assert isinstance(result[1], AIMessage)
    assert result[1].content == "Hi, how can I help?"


def test_convert_history_to_messages_returns_empty_list_for_empty_history():
    service = ChatService()

    result = service._convert_history_to_messages([])

    assert result == []


def test_get_response_calls_chatbot_app_with_history_and_user_message(monkeypatch):
    captured_input = {}

    class FakeChatbotApp:
        def invoke(self, data):
            captured_input["data"] = data

            return {
                "messages": [
                    AIMessage(content="Bot response"),
                ]
            }

    monkeypatch.setattr(chat_service_module, "chatbot_app", FakeChatbotApp())

    service = ChatService()

    chat_request = ChatRequest(
        message="I want chocolate",
        history=[
            ChatHistoryMessage(
                role="user",
                content="Hello",
            ),
            ChatHistoryMessage(
                role="assistant",
                content="Hi, how can I help?",
            ),
        ],
    )

    result = service.get_response(chat_request)

    assert result.message == "Bot response"

    messages = captured_input["data"]["messages"]

    assert len(messages) == 3

    assert isinstance(messages[0], HumanMessage)
    assert messages[0].content == "Hello"

    assert isinstance(messages[1], AIMessage)
    assert messages[1].content == "Hi, how can I help?"

    assert isinstance(messages[2], HumanMessage)
    assert messages[2].content == "I want chocolate"


def test_get_response_uses_last_message_from_chatbot_result(monkeypatch):
    class FakeChatbotApp:
        def invoke(self, data):
            return {
                "messages": [
                    HumanMessage(content="User message"),
                    AIMessage(content="First bot message"),
                    AIMessage(content="Final bot message"),
                ]
            }

    monkeypatch.setattr(chat_service_module, "chatbot_app", FakeChatbotApp())

    service = ChatService()

    chat_request = ChatRequest(
        message="Hello",
        history=[],
    )

    result = service.get_response(chat_request)

    assert result.message == "Final bot message"
