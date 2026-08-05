import './App.css'
import { PipecatClientAudio, PipecatClientProvider } from '@pipecat-ai/client-react'

import Home from './pages/Home'
import { pipecatClient } from './services/pipecatClient'

function App() {
	return (
		<PipecatClientProvider client={pipecatClient}>
			<PipecatClientAudio />
			<Home />
		</PipecatClientProvider>
	)
}

export default App