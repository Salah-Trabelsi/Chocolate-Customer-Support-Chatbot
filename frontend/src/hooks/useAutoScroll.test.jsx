// @vitest-environment jsdom

import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { cleanup, render } from '@testing-library/react'

import { useAutoScroll } from './useAutoScroll'

const TestComponent = ({ messages = [], isLoading = false, isTyping = false }) => {
	useAutoScroll({ messages, isLoading, isTyping })

	return (
		<>
			<div className="chat-thread">
				{messages.map((message) => (
					<div key={message.id} className="message-row">
						{message.text}
					</div>
				))}
			</div>

			<div id="chat-input-anchor" />
		</>
	)
}

describe('useAutoScroll', () => {
	beforeEach(() => {
		Element.prototype.scrollIntoView = vi.fn()
	})

	afterEach(() => {
		cleanup()
		vi.clearAllMocks()
	})

	it('scrolls to the last message when messages change', () => {
		render(
			<TestComponent
				messages={[
					{
						id: 1,
						text: 'Hello',
					},
				]}
			/>
		)

		expect(Element.prototype.scrollIntoView).toHaveBeenCalledWith({
			behavior: 'smooth',
			block: 'end',
		})
	})

	it('uses auto scroll behavior while loading', () => {
		render(
			<TestComponent
				messages={[
					{
						id: 1,
						text: 'Hello',
					},
				]}
				isLoading={true}
			/>
		)

		expect(Element.prototype.scrollIntoView).toHaveBeenCalledWith({
			behavior: 'auto',
			block: 'end',
		})
	})

	it('uses auto scroll behavior while typing', () => {
		render(
			<TestComponent
				messages={[
					{
						id: 1,
						text: 'Hello',
					},
				]}
				isTyping={true}
			/>
		)

		expect(Element.prototype.scrollIntoView).toHaveBeenCalledWith({
			behavior: 'auto',
			block: 'end',
		})
	})

	it('scrolls to the input anchor when loading finishes', () => {
		const { rerender } = render(
			<TestComponent
				messages={[
					{
						id: 1,
						text: 'Hello',
					},
				]}
				isLoading={true}
			/>
		)

		vi.clearAllMocks()

		rerender(
			<TestComponent
				messages={[
					{
						id: 1,
						text: 'Hello',
					},
				]}
				isLoading={false}
			/>
		)

		expect(Element.prototype.scrollIntoView).toHaveBeenCalledWith({
			behavior: 'smooth',
			block: 'end',
		})
	})
})