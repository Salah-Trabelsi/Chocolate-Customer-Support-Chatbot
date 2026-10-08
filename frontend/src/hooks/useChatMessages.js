import { useEffect, useRef, useState } from 'react'

import { askChatbot } from '../services/api'
import { initialMessages } from '../constants/chatMessages'
import { normalizeText } from '../utils/textUtils'

const createMessageId = () => Date.now() + Math.floor(Math.random() * 1000)

export const useChatMessages = () => {
	const [messages, setMessages] = useState(initialMessages)
	const [isLoading, setIsLoading] = useState(false)
	const [isTyping, setIsTyping] = useState(false)

	const typingIntervalRef = useRef(null)

	const stopTyping = () => {
		if (typingIntervalRef.current) {
			clearInterval(typingIntervalRef.current)
			typingIntervalRef.current = null
		}
	}

	const typeBotResponse = (botMessageId, fullText) => {
		let index = 0
		const typingSpeed = 15
		const step = 3

		setIsTyping(true)

		typingIntervalRef.current = setInterval(() => {
			index += step

			setMessages((currentMessages) =>
				currentMessages.map((message) =>
					message.id === botMessageId
						? {
								...message,
								text: fullText.slice(0, index),
								isTyping: index < fullText.length,
						  }
						: message
				)
			)

			if (index >= fullText.length) {
				stopTyping()
				setIsTyping(false)

				setMessages((currentMessages) =>
					currentMessages.map((message) =>
						message.id === botMessageId
							? {
									...message,
									text: fullText,
									isTyping: false,
							  }
							: message
					)
				)
			}
		}, typingSpeed)
	}

	const handleSendMessage = async (text) => {
		if (!text.trim() || isLoading || isTyping) return

		const userMessage = {
			id: createMessageId(),
			role: 'user',
			text,
		}

		const historyBeforeNewMessage = messages

		const isOnlyInitialMessage =
			messages.length === initialMessages.length &&
			messages[0]?.id === initialMessages[0]?.id

		setMessages((currentMessages) =>
			isOnlyInitialMessage ? [userMessage] : [...currentMessages, userMessage]
		)

		setIsLoading(true)

		try {
			const botResponse = await askChatbot(text, historyBeforeNewMessage)

			const botMessage = {
				id: createMessageId(),
				role: 'bot',
				text: '',
				isTyping: true,
			}

			setMessages((currentMessages) => [...currentMessages, botMessage])
			setIsLoading(false)

			typeBotResponse(botMessage.id, botResponse)
		} catch (error) {
			console.error(error)

			const errorMessage = {
				id: createMessageId(),
				role: 'bot',
				text: 'Sorry, something went wrong. Please try again 🍫',
				isError: true,
			}

			setMessages((currentMessages) => [...currentMessages, errorMessage])
			setIsLoading(false)
			setIsTyping(false)
		}
	}

	const handleClearChat = () => {
		stopTyping()
		setMessages(initialMessages)
		setIsLoading(false)
		setIsTyping(false)
	}

	const handleAddVoiceMessage = (message) => {
		setMessages((currentMessages) => {
			const isOnlyInitialMessage =
				currentMessages.length === initialMessages.length &&
				currentMessages[0]?.id === initialMessages[0]?.id

			const nextMessage = {
				...message,
				id: message.id || createMessageId(),
				source: message.source || 'voice',
			}

			if (isOnlyInitialMessage) {
				return [nextMessage]
			}

			const lastMessage = currentMessages[currentMessages.length - 1]

			if (!lastMessage) {
				return [nextMessage]
			}

			const isConsecutiveVoiceBotMessage =
				nextMessage.source === 'voice' &&
				nextMessage.role === 'bot' &&
				lastMessage.source === 'voice' &&
				lastMessage.role === 'bot'

			if (isConsecutiveVoiceBotMessage) {
				const lastText = normalizeText(lastMessage.text)
				const nextText = normalizeText(nextMessage.text)

				if (!nextText || lastText === nextText || lastText.includes(nextText)) {
					return currentMessages
				}

				if (nextText.includes(lastText)) {
					return [
						...currentMessages.slice(0, -1),
						{
							...lastMessage,
							text: nextMessage.text,
						},
					]
				}

				return [
					...currentMessages.slice(0, -1),
					{
						...lastMessage,
						text: `${lastMessage.text} ${nextMessage.text}`
							.replace(/\s+/g, ' ')
							.trim(),
					},
				]
			}

			const isConsecutiveVoiceUserMessage =
				nextMessage.source === 'voice' &&
				nextMessage.role === 'user' &&
				lastMessage.source === 'voice' &&
				lastMessage.role === 'user'

			if (isConsecutiveVoiceUserMessage) {
				const lastText = normalizeText(lastMessage.text)
				const nextText = normalizeText(nextMessage.text)

				if (!nextText || lastText === nextText) {
					return currentMessages
				}
			}

			return [...currentMessages, nextMessage]
		})
	}

	useEffect(() => stopTyping, [])

	return {
		messages,
		isLoading,
		isTyping,
		handleSendMessage,
		handleClearChat,
		handleAddVoiceMessage,
	}
}