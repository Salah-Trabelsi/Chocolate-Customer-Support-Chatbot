from __future__ import annotations
import re
from typing import Any

from langchain_core.messages import (
    AIMessage,
    ToolMessage,
    SystemMessage,
    convert_to_messages,
    convert_to_openai_messages,
)

from pipecat.frames.frames import LLMTextFrame
from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.services.openai.llm import OpenAILLMService
from pipecat.utils.tracing.service_decorators import traced_llm



# In our chocolate chatbot graph, the main LangGraph node is called "agent".
# Some LangGraph/LangChain streams may also expose "model".
_SPOKEN_NODES = {"agent", "model"}


VOICE_MODE_PROMPT = """
You are currently speaking to the customer by voice.

Voice response rules:
- Speak naturally and conversationally.
- Keep responses short and easy to listen to.
- Do not use Markdown.
- Do not use emojis.
- Do not say labels like "Description", "Brand", "Origin", or "Price" unless necessary.
- Do not read long lists unless the customer asks for many options.
- For recommendations, give a maximum of 3 products first.
- Keep each product explanation short and natural.
- Say prices clearly for voice.
- Say CHF as "CHF" or "Swiss francs", not just "francs".
- Say EUR as "euros".
- If an order is placed, always mention the order ID, total price, and payment status before asking about payment.
- If a price has a converted EUR total, mention it naturally, for example: "That is approximately 9 euros and 70 cents using our demo exchange rate."
- For payment verification, explain briefly: "For payment security, I need to verify your details once more."
- Ask one clear follow-up question at the end.
"""


def _clean_text_for_voice(text: str) -> str:
    """Remove Markdown and emojis before sending text to TTS."""

    # Remove Markdown bold/italic/backticks/headings.
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"\*(.*?)\*", r"\1", text)
    text = re.sub(r"`(.*?)`", r"\1", text)
    text = re.sub(r"#+\s*", "", text)

    # Remove bullet symbols.
    text = re.sub(r"^\s*[-•]\s+", "", text, flags=re.MULTILINE)

    # Remove common emoji/unicode symbol ranges.
    text = re.sub(
        r"[\U0001F300-\U0001FAFF\U00002700-\U000027BF\U00002600-\U000026FF]",
        "",
        text,
    )

    # Clean extra whitespace.
    text = re.sub(r"\s+", " ", text).strip()

    return text


def _spoken_text(event: dict) -> str | None:
    """Extract streamed text from LangGraph events."""

    if event.get("event") != "on_chat_model_stream":
        return None

    node = (event.get("metadata") or {}).get("langgraph_node")

    if node not in _SPOKEN_NODES:
        return None

    chunk = event.get("data", {}).get("chunk")
    text = getattr(chunk, "text", None)

    return text if isinstance(text, str) and text else None


def _final_state(event: dict, best: list | None) -> list | None:
    """Keep the longest final message list from LangGraph events."""

    if event.get("event") != "on_chain_end":
        return best

    output = event.get("data", {}).get("output")

    if isinstance(output, dict) and isinstance(output.get("messages"), list):
        messages = output["messages"]

        if best is None or len(messages) > len(best):
            return messages

    return best


def _tool_exchange(input_messages: list, final_messages: list) -> list:
    """
    Persist only tool-call messages and tool responses back into Pipecat context.

    The spoken assistant answer is added by Pipecat's assistant aggregator.
    """

    new_messages = final_messages[len(input_messages):]

    return [
        message
        for message in new_messages
        if isinstance(message, ToolMessage)
        or (isinstance(message, AIMessage) and message.tool_calls)
    ]


class LangGraphLLMService(OpenAILLMService):
    """Run our compiled LangGraph chatbot as the Pipecat LLM stage."""

    def __init__(self, *, graph: Any, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._graph = graph

    @traced_llm
    async def _process_context(self, context: LLMContext) -> None:
        messages = [
            SystemMessage(content=VOICE_MODE_PROMPT),
            *convert_to_messages(
                [
                    message
                    for message in context.get_messages()
                    if message.get("role") != "system"
                ]
            ),
        ]

        await self.start_ttfb_metrics()

        result = await self._graph.ainvoke(
            {
                "messages": messages,
            }
        )

        await self.stop_ttfb_metrics()

        final_messages = result.get("messages", [])
        final_message = final_messages[-1] if final_messages else None
        final_text = getattr(final_message, "content", "")

        if isinstance(final_text, str) and final_text.strip():
            voice_text = _clean_text_for_voice(final_text)

            if voice_text:
                await self.push_frame(LLMTextFrame(voice_text))

        if final_messages:
            to_persist = _tool_exchange(messages, final_messages)

            if to_persist:
                context.add_messages(convert_to_openai_messages(to_persist))