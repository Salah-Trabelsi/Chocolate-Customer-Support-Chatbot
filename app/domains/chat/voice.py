from __future__ import annotations

import os

from dotenv import load_dotenv
from loguru import logger

from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.frames.frames import TTSSpeakFrame
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.worker import PipelineParams, PipelineWorker
from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.processors.aggregators.llm_response_universal import (
    LLMContextAggregatorPair,
    LLMUserAggregatorParams,
)
from pipecat.runner.types import RunnerArguments
from pipecat.runner.utils import create_transport
from pipecat.services.openai.stt import OpenAISTTService
from pipecat.services.openai.tts import OpenAITTSService
from pipecat.transports.base_transport import BaseTransport, TransportParams
from pipecat.workers.runner import WorkerRunner

from app.domains.chat.chatbot import app as chocolate_graph
from app.domains.chat.langgraph_llm_service import LangGraphLLMService


load_dotenv(override=True)


async def run_bot(
    transport: BaseTransport,
    runner_args: RunnerArguments,
) -> None:
    """Build and run the chocolate voice chatbot pipeline."""

    openai_api_key = os.getenv("OPENAI_API_KEY")

    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY is missing from your .env file.")

    stt = OpenAISTTService(api_key=openai_api_key)

    llm = LangGraphLLMService(
        api_key=openai_api_key,
        graph=chocolate_graph,
    )

    tts = OpenAITTSService(
        api_key=openai_api_key,
        settings=OpenAITTSService.Settings(
            voice="alloy",
        ),
    )

    context = LLMContext()

    user_aggregator, assistant_aggregator = LLMContextAggregatorPair(
        context,
        user_params=LLMUserAggregatorParams(
            vad_analyzer=SileroVADAnalyzer(),
        ),
    )

    pipeline = Pipeline(
        [
            transport.input(),
            stt,
            user_aggregator,
            llm,
            tts,
            transport.output(),
            assistant_aggregator,
        ]
    )

    worker = PipelineWorker(
        pipeline,
        params=PipelineParams(
            enable_metrics=True,
            enable_usage_metrics=True,
        ),
        idle_timeout_secs=runner_args.pipeline_idle_timeout_secs,
    )

    @transport.event_handler("on_client_connected")
    async def on_client_connected(transport, client):  # noqa: ANN001
        logger.info("Voice client connected")

        await worker.queue_frames(
            [
                TTSSpeakFrame(
                    "Hi! Welcome to the chocolate shop voice assistant. How can I help you today?",
                    append_to_context=True,
                )
            ]
        )

    @transport.event_handler("on_client_disconnected")
    async def on_client_disconnected(transport, client):  # noqa: ANN001
        logger.info("Voice client disconnected")
        await worker.cancel()

    runner = WorkerRunner(
        handle_sigint=runner_args.handle_sigint,
    )

    await runner.add_workers(worker)
    await runner.run()


async def bot(runner_args: RunnerArguments) -> None:
    """Pipecat runner entry point."""

    transport_params = {
        "webrtc": lambda: TransportParams(
            audio_in_enabled=True,
            audio_out_enabled=True,
        ),
    }

    transport = await create_transport(
        runner_args,
        transport_params,
    )

    await run_bot(
        transport=transport,
        runner_args=runner_args,
    )


if __name__ == "__main__":
    from pipecat.runner.run import main

    main()