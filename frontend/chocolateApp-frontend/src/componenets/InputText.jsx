import { useCallback, useEffect, useRef, useState } from 'react'
import { RTVIEvent } from '@pipecat-ai/client-js'
import {
	usePipecatClient,
	usePipecatClientTransportState,
	useRTVIClientEvent,
} from '@pipecat-ai/client-react'

const VOICE_API_URL =
	import.meta.env.VITE_VOICE_API_URL || 'http://localhost:7860/start'

function InputText({ onSendMessage, isLoading, onClearChat, onAddVoiceMessage }) {
	const [inputValue, setInputValue] = useState('')
	const [voiceError, setVoiceError] = useState(null)
	const [isUserSpeaking, setIsUserSpeaking] = useState(false)
	const [isBotSpeaking, setIsBotSpeaking] = useState(false)
	const lastVoiceMessageRef = useRef({ role: '', text: '' })

	const pipecatClient = usePipecatClient()
	const transportState = usePipecatClientTransportState()

	const normalizedTransportState = String(transportState || '').toLowerCase()

	const isVoiceConnected = ['ready', 'connected'].includes(
		normalizedTransportState
	)

	const isVoiceConnecting = ['connecting', 'authenticating'].includes(
		normalizedTransportState
	)

	const isVoiceActive = isUserSpeaking || isBotSpeaking
	const isInteractionLocked = isLoading || isVoiceActive

	const getEventText = useCallback((payload) => {
		if (typeof payload === 'string') return payload
		if (!payload || typeof payload !== 'object') return ''
		return payload.text || payload.data?.text || payload.accumulated_text || ''
	}, [])

	const addVoiceMessageSafely = useCallback(
		(role, rawText) => {
			const text = String(rawText || '').trim()
			if (!text) return

			const last = lastVoiceMessageRef.current
			if (last.role === role && last.text === text) return

			lastVoiceMessageRef.current = { role, text }

			onAddVoiceMessage({
				id: Date.now() + Math.floor(Math.random() * 1000),
				role,
				text,
				source: 'voice',
			})
		},
		[onAddVoiceMessage]
	)

	useRTVIClientEvent(
		RTVIEvent.UserTranscript,
		useCallback(
			(transcript) => {
				if (transcript?.final === false) return
				addVoiceMessageSafely('user', getEventText(transcript))
			},
			[addVoiceMessageSafely, getEventText]
		)
	)

	useRTVIClientEvent(
		RTVIEvent.UserStartedSpeaking,
		useCallback(() => {
			setIsUserSpeaking(true)
		}, [])
	)

	useRTVIClientEvent(
		RTVIEvent.UserStoppedSpeaking,
		useCallback(() => {
			setIsUserSpeaking(false)
		}, [])
	)

	useRTVIClientEvent(
		RTVIEvent.BotStartedSpeaking,
		useCallback(() => {
			setIsBotSpeaking(true)
		}, [])
	)

	useRTVIClientEvent(
		RTVIEvent.BotStoppedSpeaking,
		useCallback(() => {
			setIsBotSpeaking(false)
		}, [])
	)

	useEffect(() => {
		if (!isVoiceConnected && !isVoiceConnecting) {
			setIsUserSpeaking(false)
			setIsBotSpeaking(false)
		}
	}, [isVoiceConnected, isVoiceConnecting])

	useRTVIClientEvent(
		RTVIEvent.UserLlmText,
		useCallback(
			(data) => {
				addVoiceMessageSafely('user', getEventText(data))
			},
			[addVoiceMessageSafely, getEventText]
		)
	)

	useRTVIClientEvent(
		RTVIEvent.BotOutput,
		useCallback(
			(output) => {
				const spokenStatus = output?.spoken_status
				const shouldEmit = !spokenStatus || spokenStatus === 'completed'
				if (!shouldEmit) return

				addVoiceMessageSafely('bot', getEventText(output))
			},
			[addVoiceMessageSafely, getEventText]
		)
	)

	useRTVIClientEvent(
		RTVIEvent.BotTranscript,
		useCallback(
			(transcript) => {
				addVoiceMessageSafely('bot', getEventText(transcript))
			},
			[addVoiceMessageSafely, getEventText]
		)
	)

	const handleSubmit = (event) => {
		event.preventDefault()

		if (isInteractionLocked) return
		if (!inputValue.trim()) return

		onSendMessage(inputValue)
		setInputValue('')
	}

	const handleVoiceClick = async () => {
		if (!pipecatClient) return

		setVoiceError(null)

		try {
			if (isVoiceConnected || isVoiceConnecting) {
				await pipecatClient.disconnect()
				return
			}

			await pipecatClient.startBotAndConnect({
				endpoint: VOICE_API_URL,
			})
		} catch (error) {
			console.error('Voice connection error:', error)
			setVoiceError('Voice connection failed. Please check the voice server.')
		}
	}

	return (
		<footer className="chat-input-wrap" id="chat-input-anchor">
			<form className="chat-input-form" onSubmit={handleSubmit}>
				<button
					type="button"
					className="clear-action"
					aria-label="Clear chat"
					title="Clear chat"
					onClick={onClearChat}
				>
					<span aria-hidden="true">🧹</span>
				</button>

				<button
					type="button"
					className={`send-action voice-action ${
						isVoiceConnected ? 'voice-action-active' : ''
					}`}
					aria-label="Voice input"
					title={
						isVoiceConnected
							? 'Stop voice chat'
							: isVoiceConnecting
							? 'Connecting voice...'
							: 'Start voice chat'
					}
					disabled={isInteractionLocked}
					onClick={handleVoiceClick}
				>
					<svg viewBox="0 0 24 24" aria-hidden="true">
						<path d="M12 4a3 3 0 0 0-3 3v5a3 3 0 1 0 6 0V7a3 3 0 0 0-3-3z" />
						<path d="M18 11a6 6 0 0 1-12 0" />
						<path d="M12 17v3" />
						<path d="M9 20h6" />
					</svg>
				</button>

				{isVoiceActive ? (
					<div className="voice-live-panel" aria-live="polite">
						<div className="voice-live-bars" aria-hidden="true">
							<span />
							<span />
							<span />
							<span />
							<span />
							<span />
						</div>
						<span className="voice-live-text">
							{isUserSpeaking
								? 'Listening... speak now'
								: 'Assistant is responding...'}
						</span>
					</div>
				) : (
					<input
						type="text"
						placeholder="Write your question..."
						aria-label="Question input"
						value={inputValue}
						onChange={(event) => setInputValue(event.target.value)}
						disabled={isInteractionLocked}
					/>
				)}

				<button
					type="submit"
					className="send-action"
					aria-label="Send message"
					disabled={isInteractionLocked}
				>
					<svg viewBox="0 0 24 24" aria-hidden="true">
						<path d="M4 12L20 4l-4 16-3.5-6.5z" />
					</svg>
				</button>
			</form>

			{voiceError && <p className="voice-error">{voiceError}</p>}
		</footer>
	)
}

export default InputText