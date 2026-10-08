import { useEffect, useRef } from 'react'

export const useAutoScroll = ({ messages, isLoading, isTyping }) => {
	const prevIsBusyRef = useRef(false)

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

		const lastMessageElement = document.querySelector(
			'.chat-thread .message-row:last-child'
		)

		if (lastMessageElement) {
			lastMessageElement.scrollIntoView({
				behavior: isBusy ? 'auto' : 'smooth',
				block: 'end',
			})
			return
		}

		const inputAnchor = document.getElementById('chat-input-anchor')

		if (inputAnchor) {
			inputAnchor.scrollIntoView({ behavior: 'smooth', block: 'end' })
		}
	}, [messages, isLoading, isTyping])
}