const DEFAULT_HEADERS = {
	'Content-Type': 'application/json',
}

export const postRequest = async (url, body) => {
	const response = await fetch(url, {
		method: 'POST',
		headers: DEFAULT_HEADERS,
		body: JSON.stringify(body),
	})

	if (!response.ok) {
		throw new Error('Request failed')
	}

	return response.json()
}