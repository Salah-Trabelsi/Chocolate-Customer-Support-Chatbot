import { PipecatClient } from '@pipecat-ai/client-js'
import { SmallWebRTCTransport } from '@pipecat-ai/small-webrtc-transport'

export const pipecatClient = new PipecatClient({
	transport: new SmallWebRTCTransport({
		iceServers: [{ urls: 'stun:stun.l.google.com:19302' }],
	}),
	enableCam: false,
	enableMic: true,
})