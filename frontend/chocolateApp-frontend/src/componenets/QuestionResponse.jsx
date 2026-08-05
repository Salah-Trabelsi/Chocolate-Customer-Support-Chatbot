import ReactMarkdown from 'react-markdown'

function QuestionResponse({ messages, isLoading }) {
	return (
		<section className="chat-thread" aria-label="Chat messages">
			{messages.map((message) => (
				<article
					key={message.id}
					className={`message-row ${message.role === 'user' ? 'user-row' : 'bot-row'}`}
				>
					<div
						className={`message-bubble ${
                        message.role === 'user'
                            ? 'user-bubble'
                            : message.isError
                                ? 'error-bubble'
                                : 'bot-bubble'
                    }`}
					>
						<div className="bubble-content">
							<span className="bubble-icon" aria-hidden="true">
								{message.role === 'user' ? '👤' : '🤖'}
							</span>
                            <div className="message-text">
                                {message.role === 'bot' ? (
                                    <ReactMarkdown>{message.text}</ReactMarkdown>
                                ) : (
                                    <span>{message.text}</span>
                                )}
                            </div>
						</div>
					</div>
				</article>
			))}

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