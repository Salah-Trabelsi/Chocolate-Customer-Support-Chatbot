export const VOICE_API_URL =
	import.meta.env.VITE_VOICE_API_URL || 'http://localhost:7860/start'

export const CONNECTED_VOICE_STATES = ['ready', 'connected']

export const CONNECTING_VOICE_STATES = ['connecting', 'authenticating']