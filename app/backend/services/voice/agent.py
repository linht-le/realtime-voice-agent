import json
from collections.abc import Callable
from datetime import datetime
from typing import Any, TypedDict

import websockets
from langchain_core.tools import BaseTool
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from app.backend.logger import get_logger
from app.backend.services.voice.transcription import TranscriptionBuffer

logger = get_logger(__name__)


class AgentState(TypedDict):
    tool_calls: list[dict[str, Any]]
    tool_results: list[dict[str, Any]]


class VoiceAgent:
    def __init__(
        self,
        model: str,
        api_key: str,
        user_settings: dict[str, Any],
        instructions: str,
        tools: list[BaseTool] | None = None,
    ):
        self.model = model
        self.api_key = api_key
        self.user_settings = user_settings
        self.instructions = instructions
        self.tools = tools or []
        self.ws: websockets.WebSocketClientProtocol | None = None
        self.graph = self._build_graph()
        self.transcription = TranscriptionBuffer()
        self.session_start_time: datetime | None = None
        self.speech_end_ms: int | None = None
        self.ai_first_audio_ms: int | None = None
        self.current_response_tools: list[str] = []

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
            elif msg_type in ("interrupt", "stop"):
                await self.websocket.send(json.dumps({"type": "input_audio_buffer.clear"}))
            elif msg_type == "commit_audio":
                await self.websocket.send(json.dumps({"type": "input_audio_buffer.commit"}))
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON message: {e}")
        except Exception as e:
            logger.error(f"Error handling browser message: {e}")

    async def process_openai_events(self, browser_send: Callable) -> None:
        """Process events from OpenAI and forward to browser"""
        while True:
            try:
                raw_event = await self.websocket.recv()
                event = json.loads(raw_event)
                event_type = event.get("type")

            except Exception as e:
                logger.error(f"Error receiving/parsing OpenAI event: {e}")
                break

            try:
                # Session lifecycle: Connection established
                if event_type == "session.created":
                    self.session_start_time = datetime.now()
                    await browser_send(
                        json.dumps({"type": "session_created", "session": event.get("session")})
                    )

                # Session lifecycle: Settings updated
                elif event_type == "session.updated":
                    await browser_send(
                        json.dumps({"type": "session_updated", "session": event.get("session")})
                    )

                # Session lifecycle: Session error (auth, config issues)
                elif event_type == "session.error":
                    error_info = event.get("error", {})
                    logger.error(f"Session error: {error_info}")
                    await browser_send(json.dumps({"type": "session_error", "error": error_info}))

                # Session lifecycle: Session expired (token timeout)
                elif event_type == "session.expired":
                    logger.warning("Session expired")
                    await browser_send(
                        json.dumps(
                            {
                                "type": "session_expired",
                                "message": "Session expired, please reconnect",
                            }
                        )
                    )

                # Session lifecycle: Session closed
                elif event_type == "session.closed":
                    logger.info("Session closed by server")
                    await browser_send(
                        json.dumps({"type": "session_closed", "message": "Session closed"})
                    )

                # Response lifecycle: AI starts creating response
                elif event_type == "response.created":
                    await browser_send(
                        json.dumps(
                            {"type": "response_created", "timestamp": datetime.now().isoformat()}
                        )
                    )

                # Response lifecycle: Response failed
                elif event_type == "response.failed":
                    error_info = event.get("error", {})
                    logger.error(f"Response failed: {error_info}")
                    await browser_send(
                        json.dumps(
                            {
                                "type": "response_failed",
                                "error": error_info,
                                "timestamp": datetime.now().isoformat(),
                            }
                        )
                    )

                # Response lifecycle: Response cancelled (user interrupt)
                elif event_type == "response.cancelled":
                    logger.info("Response cancelled")
                    await browser_send(
                        json.dumps(
                            {"type": "response_cancelled", "timestamp": datetime.now().isoformat()}
                        )
                    )
                    # Clear current response tools tracking
                    self.current_response_tools.clear()

                # Audio output: AI starts generating audio (first audio event)
                elif event_type == "response.audio.started":
                    # Mark exact moment AI starts audio generation for accurate latency
                    if self.speech_end_ms is not None and self.session_start_time is not None:
                        current_offset = datetime.now() - self.session_start_time
                        self.ai_first_audio_ms = int(current_offset.total_seconds() * 1000)

                # Audio output: Streaming audio chunks from AI
                elif event_type == "response.audio.delta":
                    # Fallback: If audio.started wasn't received, mark timing on first delta
                    if (
                        self.ai_first_audio_ms is None
                        and self.speech_end_ms is not None
                        and self.session_start_time is not None
                    ):
                        current_offset = datetime.now() - self.session_start_time
                        self.ai_first_audio_ms = int(current_offset.total_seconds() * 1000)

                    audio_data = event.get("delta")
                    await browser_send(json.dumps({"type": "audio_delta", "audio": audio_data}))

                # Transcript: Interim text updates while AI is speaking
                elif event_type == "response.audio_transcript.delta":
                    delta = event.get("delta", "")
                    await self.transcription.update_interim(delta)
                    await browser_send(json.dumps({"type": "transcript_delta", "text": delta}))

                # Transcript: Final AI response text completed
                elif event_type == "response.audio_transcript.done":
                    transcript = event.get("transcript", "")
                    await self.transcription.finalize_current()

                    # Calculate response time using relative offsets from session start
                    response_time_ms = None
                    if self.speech_end_ms is not None and self.ai_first_audio_ms is not None:
                        response_time_ms = self.ai_first_audio_ms - self.speech_end_ms

                    log_msg = f"Agent: {transcript}"
                    if response_time_ms is not None and response_time_ms > 0:
                        log_msg += f" (response time: {response_time_ms}ms)"
                    logger.info(log_msg)

                    await browser_send(
                        json.dumps(
                            {
                                "type": "transcript_done",
                                "text": transcript,
                                "timestamp": datetime.now().isoformat(),
                                "response_time_ms": response_time_ms,
                                "toolsUsed": self.current_response_tools.copy(),
                            }
                        )
                    )

                    self.current_response_tools.clear()

                # Tool calls: Process function calls from AI response
                elif event_type == "response.done":
                    try:
                        for output in event.get("response", {}).get("output", []):
                            if output.get("type") == "function_call":
                                await self._handle_function_call(output)
                    except Exception as e:
                        logger.error(f"Error processing function calls: {e}")

                # VAD: User started speaking (voice activity detected)
                elif event_type == "input_audio_buffer.speech_started":
                    await browser_send(json.dumps({"type": "speech_started"}))

                # VAD: User stopped speaking (silence detected)
                elif event_type == "input_audio_buffer.speech_stopped":
                    # Store offset from session start for accurate response time calculation
                    audio_end_ms = event.get("audio_end_ms")
                    if audio_end_ms is not None:
                        self.speech_end_ms = audio_end_ms

                    self.ai_first_audio_ms = None
                    await browser_send(
                        json.dumps(
                            {"type": "speech_stopped", "timestamp": datetime.now().isoformat()}
                        )
                    )

                # Transcript: User speech-to-text completed
                elif event_type == "conversation.item.input_audio_transcription.completed":
                    transcript = event.get("transcript", "")
                    logger.info(f"User: {transcript}")
                    await browser_send(
                        json.dumps(
                            {
                                "type": "user_transcript",
                                "text": transcript,
                                "timestamp": datetime.now().isoformat(),
                            }
                        )
                    )

                # Rate limits: Monitor API usage and warn if approaching limits
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

                # Error handling: Process and forward errors to browser
                elif event_type == "error":
                    error_code = event.get("error", {}).get("code", "")
                    if error_code != "response_cancel_not_active":
                        logger.error(f"OpenAI error: {event}")
                        try:
                            await browser_send(
                                json.dumps({"type": "error", "error": event.get("error")})
                            )
                        except Exception as e:
                            logger.warning(f"Failed to send error to browser: {e}")

            except Exception as e:
                logger.error(f"Error processing OpenAI event {event_type}: {e}")

    async def disconnect(self) -> None:
        """Disconnect from OpenAI Realtime API"""
        if self.ws:
            await self.ws.close()
            self.ws = None
        await self.transcription.clear()

    async def _initialize_session(self) -> None:
        """Initialize session with backend settings"""
        backend = self.user_settings.get("backend", {})

        # Helper to extract value from schema structure
        def extract_value(setting, fallback):
            if isinstance(setting, dict):
                return setting.get("value", setting.get("default", fallback))
            return setting if setting is not None else fallback

        # Extract backend settings
        voice = extract_value(backend.get("voice"), "alloy")
        language = extract_value(backend.get("language"), "auto")
        transcription = backend.get("transcription", {})
        vad = backend.get("vad", {})
        response = backend.get("response", {})
        generation = backend.get("generation", {})
        audio = backend.get("audio", {})

        # Add language hint to instructions if not auto
        instructions = self.instructions
        if language != "auto":
            language_hints = {"vi": "Vietnamese", "en": "English", "ja": "Japanese"}
            lang_name = language_hints.get(language, language)
            instructions = f"{self.instructions}\n\nIMPORTANT: Always respond in {lang_name}."

        # Build turn_detection config based on VAD settings
        vad_enabled = extract_value(vad.get("enabled"), True)
        vad_type = extract_value(vad.get("type"), "server_vad")
        turn_detection: dict[str, Any] | None = None

        if vad_enabled and vad_type == "server_vad":
            turn_detection = {
                "type": "server_vad",
                "threshold": extract_value(vad.get("threshold"), 0.5),
                "prefix_padding_ms": extract_value(vad.get("prefix_padding_ms"), 300),
                "silence_duration_ms": extract_value(vad.get("silence_duration_ms"), 800),
            }
        elif vad_enabled and vad_type == "semantic_vad":
            turn_detection = {
                "type": "semantic_vad",
                "eagerness": extract_value(vad.get("semantic_eagerness"), "auto"),
                "create_response": extract_value(response.get("auto_response"), True),
                "interrupt_response": extract_value(vad.get("interrupt_response"), True),
            }

        # Build session config
        session_update = {
            "type": "session.update",
            "session": {
                "modalities": ["audio", "text"],
                "instructions": instructions,
                "voice": voice,
                "input_audio_format": extract_value(audio.get("input_format"), "pcm16"),
                "output_audio_format": extract_value(audio.get("output_format"), "pcm16"),
                "temperature": extract_value(generation.get("temperature"), 0.7),
                "max_response_output_tokens": extract_value(
                    generation.get("max_output_tokens"), 1024
                ),
            },
        }

        # Add transcription if enabled
        if extract_value(transcription.get("enabled"), True):
            session_update["session"]["input_audio_transcription"] = {
                "model": extract_value(transcription.get("model"), "whisper-1"),
            }

        # Add turn_detection if enabled
        if turn_detection:
            session_update["session"]["turn_detection"] = turn_detection

        # Add tools if available
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
        logger.info(f"Tool: {function_name}")

        # Track tool usage for current response
        if function_name and function_name not in self.current_response_tools:
            self.current_response_tools.append(function_name)

        initial_state: AgentState = {
            "tool_calls": [{"call_id": call_id, "name": function_name, "arguments": arguments}],
            "tool_results": [],
        }

        await self.graph.ainvoke(initial_state)
