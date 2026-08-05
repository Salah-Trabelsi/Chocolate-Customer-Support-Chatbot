const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';


export async function askChatbot(message, history) {

    const formattedHistory = history.map((item) => ({
        role: item.role === 'bot' ? 'assistant' : item.role,
        content: item.text || item.content,
    }))


    const response = await fetch(`${API_BASE_URL}/chat/ask`, {

        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },

        body: JSON.stringify({
            message,
            history: formattedHistory,
        }),

    })

    if (!response.ok) {
        throw new Error('Failed to get chatbot response')
    }

    const data = await response.json()
    return data.message

}