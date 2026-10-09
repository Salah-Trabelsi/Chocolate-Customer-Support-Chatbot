import { useState } from 'react'

import { useVoiceChat } from '../hooks/useVoiceChat'

const InputText = ({onSendMessage, isLoading, onClearChat, onAddVoiceMessage,}) => {
	const [inputValue, setInputValue] = useState('')

	const {
		voiceError,
		isVoiceConnected,
		isVoiceConnecting,
		isUserSpeaking,
		isVoiceActive,
		handleVoiceClick,
	} = useVoiceChat({ onAddVoiceMessage })

	const isTextInputLocked = isLoading || isVoiceActive

	const handleSubmit = (event) => {
		event.preventDefault()

		if (isTextInputLocked) return
		if (!inputValue.trim()) return

		onSendMessage(inputValue)
		setInputValue('')
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
					} ${isVoiceConnecting ? 'voice-action-connecting' : ''}`}
					aria-label="Voice input"
					title={
						isVoiceConnected
							? 'Stop voice chat'
							: isVoiceConnecting
							? 'Connecting voice...'
							: 'Start voice chat'
					}
					disabled={isLoading}
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
						disabled={isTextInputLocked}
					/>
				)}

				<button
					type="submit"
					className="send-action"
					aria-label="Send message"
					disabled={isTextInputLocked}
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