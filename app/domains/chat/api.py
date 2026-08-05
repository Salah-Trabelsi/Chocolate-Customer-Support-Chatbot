from fastapi import APIRouter, HTTPException, status

from app.domains.chat.model import ChatRequest, ChatResponse
from app.domains.chat.service import ChatService


router = APIRouter()

@router.post("/ask", response_model=ChatResponse)
async def ask_chatbot(chat_request: ChatRequest) -> ChatResponse:
    """
    Ask the chatbot a question and get a response.

    This endpoint allows users to send a message to the chatbot along with an optional chat history.
    The chatbot will process the input and return a relevant response.

    Args:
        chat_request (ChatRequest): The request body containing the user's message and chat history.

    Returns:
        ChatResponse: The response from the chatbot containing the assistant's message.
    """
    chat_service = ChatService()

    try:
        return chat_service.get_response(chat_request)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error)
        )
    
    except Exception as error:
        print("Chatbot error:", error)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong while generating the chatbot response.",
        )