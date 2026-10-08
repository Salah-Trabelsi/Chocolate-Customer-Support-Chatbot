import Navbar from '../componenets/Navbar'
import QuestionResponse from '../componenets/QuestionResponse'
import InputText from '../componenets/InputText'

import { useAutoScroll } from '../hooks/useAutoScroll'
import { useChatMessages } from '../hooks/useChatMessages'

const Home = () => {
	const {
		messages,
		isLoading,
		isTyping,
		handleSendMessage,
		handleClearChat,
		handleAddVoiceMessage,
	} = useChatMessages()

	useAutoScroll({
		messages,
		isLoading,
		isTyping,
	})

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