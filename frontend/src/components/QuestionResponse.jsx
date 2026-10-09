import ReactMarkdown from 'react-markdown'

const QuestionResponse = ({ messages, isLoading }) => {
	return (
		<section className="chat-thread" aria-label="Chat messages">
			{messages.map((message) => {
				const isUserMessage = message.role === 'user'

				const bubbleClassName = isUserMessage
					? 'user-bubble'
					: message.isError
					? 'error-bubble'
					: 'bot-bubble'

				return (
					<article
						key={message.id}
						className={`message-row ${
							isUserMessage ? 'user-row' : 'bot-row'
						}`}
					>
						<div className={`message-bubble ${bubbleClassName}`}>
							<div className="bubble-content">
								<span className="bubble-icon" aria-hidden="true">
									{isUserMessage ? '👤' : '🤖'}
								</span>

								<div className="message-text">
									{isUserMessage ? (
										<span>{message.text}</span>
									) : (
										<ReactMarkdown>{message.text}</ReactMarkdown>
									)}
								</div>
							</div>
						</div>
					</article>
				)
			})}

			{isLoading && (
				<article className="message-row bot-row">
					<div className="message-bubble bot-bubble">
						<div className="bubble-content">
							<span className="bubble-icon" aria-hidden="true">
								🤖
							</span>

							<div className="message-text typing-dots">
								thinking
								<span>.</span>
								<span>.</span>
								<span>.</span>
							</div>
						</div>
					</div>
				</article>
			)}
		</section>
	)
}

export default QuestionResponse