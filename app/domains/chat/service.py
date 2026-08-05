from langchain_core.messages import AIMessage, HumanMessage


from app.domains.chat.chatbot import app as chatbot_app
from app.domains.chat.model import ChatRequest, ChatResponse, ChatHistoryMessage



class ChatService:
    def _convert_history_to_messages(self, history: list[ChatHistoryMessage]):
        messages = []

        for item in history:
            if item.role == "user":
                messages.append(HumanMessage(content=item.content))

            if item.role == "assistant":
                messages.append(AIMessage(content=item.content))
        return messages
    


    def get_response(self, chat_request: ChatRequest) -> ChatResponse:
        messages = self._convert_history_to_messages(chat_request.history)
        messages.append(HumanMessage(content=chat_request.message))

        result = chatbot_app.invoke({
            "messages": messages
        })

        assistant_message = result["messages"][-1]

        return ChatResponse(
            message=assistant_message.content
        )