// @vitest-environment jsdom

import '@testing-library/jest-dom/vitest'

import { cleanup, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it } from 'vitest'

import Navbar from './Navbar'

describe('Navbar', () => {
	afterEach(() => {
		cleanup()
	})

	it('renders the ChocoWise brand title', () => {
		render(<Navbar />)

		expect(
			screen.getByRole('heading', {
				name: /chocowise/i,
			})
		).toBeInTheDocument()
	})

	it('renders the navbar header', () => {
		const { container } = render(<Navbar />)

		expect(container.querySelector('.chatbot-navbar')).toBeInTheDocument()
	})
})