import json
import logging
from collections.abc import Callable
from typing import Any, TypedDict

import websockets
from langchain_core.tools import BaseTool
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from app.utils.transcription import TranscriptionBuffer

logger = logging.getLogger(__name__)


class AgentState(TypedDict):
    tool_calls: list[dict[str, Any]]
    tool_results: list[dict[str, Any]]


class VoiceAgent:
    def __init__(
        self,
        model: str,
        voice: str,
        instructions: str,
        tools: list[BaseTool] | None = None,
        api_key: str = ""
    ):
        self.model = model
        self.voice = voice
        self.instructions = instructions
        self.tools = tools or []
        self.api_key = api_key
        self.ws: websockets.WebSocketClientProtocol | None = None
        self.graph = self._build_graph()
        self.transcription = TranscriptionBuffer()

    @property
    def websocket(self) -> websockets.WebSocketClientProtocol:
        """Get the websocket connection"""
        if self.ws is None:
            raise RuntimeError("Not connected to OpenAI API")
        return self.ws

    async def connect(self) -> None:
        """Connect to OpenAI Realtime API via WebSocket"""
        self.ws = await websockets.connect(
            f"wss://api.openai.com/v1/realtime?model={self.model}",
            additional_headers={
                "Authorization": f"Bearer {self.api_key}",
                "OpenAI-Beta": "realtime=v1",
            },
        )
        logger.info(f"Connected to OpenAI Realtime API (model: {self.model})")
        await self._initialize_session()

    async def handle_browser_message(self, message: str) -> None:
        """Handle incoming audio from browser WebSocket"""
        try:
            data = json.loads(message)
            msg_type = data.get("type")

            if msg_type == "audio":
                await self.websocket.send(
                    json.dumps({"type": "input_audio_buffer.append", "audio": data.get("audio")})
                )
            elif msg_type == "interrupt":
                await self.websocket.send(json.dumps({"type": "input_audio_buffer.clear"}))
                logger.info("User interrupted")
            elif msg_type == "commit_audio":
                await self.websocket.send(json.dumps({"type": "input_audio_buffer.commit"}))
            elif msg_type == "stop":
                # Graceful stop - clear buffers only (don't cancel, may not have active response)
                await self.websocket.send(json.dumps({"type": "input_audio_buffer.clear"}))
                logger.info("Conversation stopped by user")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON message: {e}")
        except Exception as e:
            logger.error(f"Error handling browser message: {e}")

    async def process_openai_events(self, browser_send: Callable) -> None:
        """Process events from OpenAI and forward to browser"""
        while True:
            try:
                event = json.loads(await self.websocket.recv())
                event_type = event.get("type")
            except Exception as e:
                logger.error(f"Error receiving/parsing OpenAI event: {e}")
                break

            try:
                # Session lifecycle events
                if event_type == "session.created":
                    logger.info(f"Session created: {event.get('session', {}).get('id')}")
                    await browser_send(
                        json.dumps({"type": "session_created", "session": event.get("session")})
                    )

                elif event_type == "session.updated":
                    await browser_send(
                        json.dumps({"type": "session_updated", "session": event.get("session")})
                    )

                # Audio output events
                elif event_type == "response.audio.delta":
                    audio_data = event.get("delta")
                    await browser_send(json.dumps({"type": "audio_delta", "audio": audio_data}))

                elif event_type == "response.audio_transcript.delta":
                    delta = event.get("delta", "")
                    await self.transcription.update_interim(delta)
                    await browser_send(json.dumps({"type": "transcript_delta", "text": delta}))

                elif event_type == "response.audio_transcript.done":
                    transcript = event.get("transcript", "")
                    await self.transcription.finalize_current()
                    logger.info(f"Agent: {transcript}")
                    await browser_send(json.dumps({"type": "transcript_done", "text": transcript}))

                elif event_type == "response.done":
                    try:
                        for output in event.get("response", {}).get("output", []):
                            if output.get("type") == "function_call":
                                await self._handle_function_call(output)
                    except Exception as e:
                        logger.error(f"Error processing function calls: {e}")

                elif event_type == "input_audio_buffer.speech_started":
                    await browser_send(json.dumps({"type": "speech_started"}))

                elif event_type == "input_audio_buffer.speech_stopped":
                    await browser_send(json.dumps({"type": "speech_stopped"}))

                elif event_type == "conversation.item.input_audio_transcription.completed":
                    transcript = event.get("transcript", "")
                    logger.info(f"User: {transcript}")
                    await browser_send(json.dumps({"type": "user_transcript", "text": transcript}))

                elif event_type == "rate_limits.updated":
                    rate_limits = event.get("rate_limits", [])
                    for limit_data in rate_limits:
                        if isinstance(limit_data, dict):
                            limit_type = limit_data.get("name", "unknown")
                            remaining = limit_data.get("remaining", 0)
                            limit = limit_data.get("limit", 0)
                            if limit > 0 and remaining / limit < 0.2:
                                logger.warning(
                                    f"Rate limit warning: {limit_type} at {remaining}/{limit}"
                                )

                elif event_type == "error":
                    error_code = event.get("error", {}).get("code", "")
                    if error_code != "response_cancel_not_active":
                        logger.error(f"OpenAI error: {event}")
                        try:
                            await browser_send(
                                json.dumps({"type": "error", "error": event.get("error")})
                            )
                        except Exception:
                            pass  # WebSocket may be closed

            except Exception as e:
                logger.error(f"Error processing OpenAI event {event_type}: {e}")

    async def disconnect(self) -> None:
        """Disconnect from OpenAI Realtime API"""
        if self.ws:
            await self.ws.close()
            self.ws = None
        await self.transcription.clear()

    async def _initialize_session(self) -> None:
        """Initialize session"""
        from app.config import get_settings

        settings = get_settings()

        session_update = {
            "type": "session.update",
            "session": {
                "modalities": ["audio", "text"],
                "instructions": self.instructions,
                "voice": self.voice,
                "input_audio_format": "pcm16",
                "output_audio_format": "pcm16",
                "input_audio_transcription": {"model": "whisper-1"},
                "turn_detection": {
                    "type": "server_vad",
                    "threshold": 0.3,
                    "prefix_padding_ms": 500,
                    "silence_duration_ms": 500,
                },
                "temperature": settings.TEMPERATURE,
                "max_response_output_tokens": 4096,
            },
        }

        if self.tools:
            session_update["session"]["tools"] = [
                {
                    "type": "function",
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": self._get_tool_parameters(tool),
                }
                for tool in self.tools
            ]
            session_update["session"]["tool_choice"] = "auto"

        await self.websocket.send(json.dumps(session_update))

    def _get_tool_parameters(self, tool: BaseTool) -> dict[str, Any]:
        """Extract tool parameters for OpenAI format"""
        if tool.args_schema is None:
            return {"type": "object", "properties": {}, "required": []}

        schema = tool.args_schema.model_json_schema()
        return {
            "type": "object",
            "properties": schema.get("properties", {}),
            "required": schema.get("required", []),
        }

    def _build_graph(self) -> CompiledStateGraph:
        """Build LangGraph StateGraph for managing agent workflow"""
        graph = StateGraph(AgentState)

        graph.add_node("execute_tool", self._execute_tool_node)
        graph.add_node("send_result", self._send_result_node)

        graph.add_edge(START, "execute_tool")
        graph.add_edge("execute_tool", "send_result")
        graph.add_edge("send_result", END)

        return graph.compile()

    async def _execute_tool_node(self, state: AgentState) -> AgentState:
        """Node: Execute tools from state"""
        tool_calls = state.get("tool_calls", [])
        results = []

        for tool_call in tool_calls:
            tool_name = tool_call.get("name")
            arguments = tool_call.get("arguments", {})

            tool = next((t for t in self.tools if t.name == tool_name), None)
            if not tool:
                results.append(
                    {
                        "call_id": tool_call.get("call_id"),
                        "result": f"Error: Tool {tool_name} not found",
                    }
                )
                continue

            try:
                result = await tool.ainvoke(arguments)
                logger.info(f"Tool result: {str(result)[:200]}...")
                results.append(
                    {
                        "call_id": tool_call.get("call_id"),
                        "result": str(result),
                    }
                )
            except Exception as e:
                logger.error(f"Tool execution error: {e}")
                results.append(
                    {
                        "call_id": tool_call.get("call_id"),
                        "result": f"Error: {str(e)}",
                    }
                )

        state["tool_results"] = results
        return state

    async def _send_result_node(self, state: AgentState) -> AgentState:
        """Node: Send tool results back to OpenAI"""
        for result in state.get("tool_results", []):
            await self.websocket.send(
                json.dumps(
                    {
                        "type": "conversation.item.create",
                        "item": {
                            "type": "function_call_output",
                            "call_id": result["call_id"],
                            "output": json.dumps({"result": result["result"]}),
                        },
                    }
                )
            )

        # Trigger new response generation
        await self.websocket.send(json.dumps({"type": "response.create"}))
        return state

    async def _handle_function_call(self, function_call: dict[str, Any]) -> None:
        """Handle function call from OpenAI using LangGraph"""
        call_id = function_call.get("call_id")
        function_name = function_call.get("name")
        arguments = json.loads(function_call.get("arguments", "{}"))
        logger.info(f"Executing tool: {function_name} with args: {arguments}")

        initial_state: AgentState = {
            "tool_calls": [{"call_id": call_id, "name": function_name, "arguments": arguments}],
            "tool_results": [],
        }

        await self.graph.ainvoke(initial_state)
