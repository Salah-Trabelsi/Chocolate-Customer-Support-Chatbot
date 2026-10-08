import { PipecatClientAudio, PipecatClientProvider } from '@pipecat-ai/client-react'

import { pipecatClient } from '../services/pipecatClient'

const AppProviders = ({ children }) => {
	return (
		<PipecatClientProvider client={pipecatClient}>
			<PipecatClientAudio />
			{children}
		</PipecatClientProvider>
	)
}

export default AppProviders