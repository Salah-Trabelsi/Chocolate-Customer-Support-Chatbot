import { useCallback, useEffect, useRef, useState } from 'react'
import { RTVIEvent } from '@pipecat-ai/client-js'
import {
	usePipecatClient,
	usePipecatClientTransportState,
	useRTVIClientEvent,
} from '@pipecat-ai/client-react'

import {
	CONNECTED_VOICE_STATES,
	CONNECTING_VOICE_STATES,
	VOICE_API_URL,
} from '../config/voiceConfig'

const getEventText = (payload) => {
	if (typeof payload === 'string') return payload

	if (!payload || typeof payload !== 'object') return ''

	return payload.text || payload.data?.text || payload.accumulated_text || ''
}

const createMessageId = () => Date.now() + Math.floor(Math.random() * 1000)

export const useVoiceChat = ({ onAddVoiceMessage }) => {
	const [voiceError, setVoiceError] = useState(null)
	const [isUserSpeaking, setIsUserSpeaking] = useState(false)
	const [isBotSpeaking, setIsBotSpeaking] = useState(false)

	const lastVoiceMessageRef = useRef({ role: '', text: '' })

	const pipecatClient = usePipecatClient()
	const transportState = usePipecatClientTransportState()

	const normalizedTransportState = String(transportState || '').toLowerCase()

	const isVoiceConnected = CONNECTED_VOICE_STATES.includes(
		normalizedTransportState
	)

	const isVoiceConnecting = CONNECTING_VOICE_STATES.includes(
		normalizedTransportState
	)

	const isVoiceActive = isUserSpeaking || isBotSpeaking

	const addVoiceMessageSafely = useCallback(
		(role, rawText) => {
			const text = String(rawText || '').trim()

			if (!text) return

			const lastMessage = lastVoiceMessageRef.current

			if (lastMessage.role === role && lastMessage.text === text) return

			lastVoiceMessageRef.current = { role, text }

			onAddVoiceMessage({
				id: createMessageId(),
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
			[addVoiceMessageSafely]
		)
	)

	useRTVIClientEvent(
		RTVIEvent.UserLlmText,
		useCallback(
			(data) => {
				addVoiceMessageSafely('user', getEventText(data))
			},
			[addVoiceMessageSafely]
		)
	)

	useRTVIClientEvent(
		RTVIEvent.BotOutput,
		useCallback(
			(output) => {
				const spokenStatus = output?.spoken_status
				const isCompletedOutput = !spokenStatus || spokenStatus === 'completed'

				if (!isCompletedOutput) return

				addVoiceMessageSafely('bot', getEventText(output))
			},
			[addVoiceMessageSafely]
		)
	)

	useRTVIClientEvent(
		RTVIEvent.BotTranscript,
		useCallback(
			(transcript) => {
				addVoiceMessageSafely('bot', getEventText(transcript))
			},
			[addVoiceMessageSafely]
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

	return {
		voiceError,
		isVoiceConnected,
		isVoiceConnecting,
		isUserSpeaking,
		isBotSpeaking,
		isVoiceActive,
		handleVoiceClick,
	}
}

