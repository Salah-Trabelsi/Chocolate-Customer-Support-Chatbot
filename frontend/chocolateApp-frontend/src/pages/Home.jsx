import { useEffect, useRef, useState } from 'react'

import Navbar from '../componenets/Navbar'
import QuestionResponse from '../componenets/QuestionResponse'
import InputText from '../componenets/InputText'
import { askChatbot } from '../services/api'

const initialMessages = [
	{
		id: 1,
		role: 'bot',
		text: 'Hey, I am your chocolate chatbot 🍫 How can I help you?',
	},
]

function Home() {
	const [messages, setMessages] = useState(initialMessages)
	const [isLoading, setIsLoading] = useState(false)
	const [isTyping, setIsTyping] = useState(false)

	const typingIntervalRef = useRef(null)
	const prevIsBusyRef = useRef(false)

	const normalizeText = (value) => String(value || '').replace(/\s+/g, ' ').trim()

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
			id: Date.now(),
			role: 'user',
			text,
		}

		const historyBeforeNewMessage = messages
		const isFirstUserMessage =
			messages.length === initialMessages.length &&
			messages[0]?.id === initialMessages[0]?.id

		setMessages((currentMessages) =>
			isFirstUserMessage ? [userMessage] : [...currentMessages, userMessage]
		)
		setIsLoading(true)

		try {
			const botResponse = await askChatbot(text, historyBeforeNewMessage)

			const botMessage = {
				id: Date.now() + 1,
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
                id: Date.now() + 1,
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

	useEffect(() => {
		const isBusy = isLoading || isTyping
		const wasBusy = prevIsBusyRef.current
		prevIsBusyRef.current = isBusy

		if (!isBusy && wasBusy) {
			const inputAnchor = document.getElementById('chat-input-anchor')
			if (inputAnchor) {
				inputAnchor.scrollIntoView({ behavior: 'smooth', block: 'end' })
				return
			}
		}

		const lastMessageElement = document.querySelector('.chat-thread .message-row:last-child')
		if (lastMessageElement) {
			lastMessageElement.scrollIntoView({ behavior: isBusy ? 'auto' : 'smooth', block: 'end' })
			return
		}

		const inputAnchor = document.getElementById('chat-input-anchor')
		if (inputAnchor) {
			inputAnchor.scrollIntoView({ behavior: 'smooth', block: 'end' })
		}
	}, [messages, isLoading, isTyping])

	useEffect(() => stopTyping, [])

	const handleAddVoiceMessage = (message) => {
		setMessages((currentMessages) => {
			const isOnlyInitialMessage =
				currentMessages.length === initialMessages.length &&
				currentMessages[0]?.id === initialMessages[0]?.id

			const nextMessage = {
				...message,
				id: message.id || Date.now(),
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
						text: `${lastMessage.text} ${nextMessage.text}`.replace(/\s+/g, ' ').trim(),
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

	return (
		<div className="chatbot-page">
			<Navbar />

			<main className="chatbot-main">
				<QuestionResponse messages={messages} isLoading={isLoading} />
			</main>

			<InputText
				onSendMessage={handleSendMessage}
				onClearChat={handleClearChat}
				isLoading={isLoading || isTyping}
				onAddVoiceMessage={handleAddVoiceMessage}
			/>
		</div>
	)
}

export default Home