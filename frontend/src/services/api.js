import { postRequest } from './httpClient'

const API_BASE_URL =
	import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

const MAX_HISTORY_MESSAGES = 8

const formatChatHistory = (history = []) =>
	history
		.filter((item) => item.id !== 1)
		.slice(-MAX_HISTORY_MESSAGES)
		.map((item) => ({
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