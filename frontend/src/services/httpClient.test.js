import { beforeEach, describe, expect, it, vi } from 'vitest'

import { postRequest } from './httpClient'

describe('postRequest', () => {
	beforeEach(() => {
		vi.restoreAllMocks()
	})

	it('sends a POST request with JSON body and headers', async () => {
		const mockResponse = {
			message: 'Success',
		}

		global.fetch = vi.fn().mockResolvedValue({
			ok: true,
			json: vi.fn().mockResolvedValue(mockResponse),
		})

		const result = await postRequest('http://localhost:8000/api/chat/ask', {
			message: 'Hello',
			history: [],
		})

		expect(fetch).toHaveBeenCalledWith('http://localhost:8000/api/chat/ask', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify({
				message: 'Hello',
				history: [],
			}),
		})

		expect(result).toEqual(mockResponse)
	})

	it('throws an error when the response is not ok', async () => {
		global.fetch = vi.fn().mockResolvedValue({
			ok: false,
		})

		await expect(
			postRequest('http://localhost:8000/api/chat/ask', {
				message: 'Hello',
			})
		).rejects.toThrow('Request failed')
	})
})