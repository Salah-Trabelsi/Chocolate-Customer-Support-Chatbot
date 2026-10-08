import { postRequest } from './httpClient'

const API_BASE_URL =
	import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

const formatChatHistory = (history = []) =>
	history.map((item) => ({
		role: item.role === 'bot' ? 'assistant' : item.role,
		content: item.text || item.content,
	}))

export const askChatbot = async (message, history = []) => {
	const formattedHistory = formatChatHistory(history)

	const data = await postRequest(`${API_BASE_URL}/chat/ask`, {
		message,
		history: formattedHistory,
	})

	return data.message
}