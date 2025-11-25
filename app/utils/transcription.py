import asyncio
from collections import deque


class TranscriptionBuffer:
    def __init__(self, max_history: int = 100):
        self.current_transcript = ""
        self.final_transcripts: deque[str] = deque(maxlen=max_history)
        self._lock = asyncio.Lock()

    async def update_interim(self, text: str) -> None:
        """Update the current interim transcript"""
        async with self._lock:
            self.current_transcript = text

    async def finalize_current(self) -> str:
        """Finalize the current transcript and return it"""
        async with self._lock:
            if self.current_transcript:
                final = self.current_transcript.strip()
                if final:  # Only add non-empty transcripts
                    self.final_transcripts.append(final)
                self.current_transcript = ""
                return final
            return ""

    async def clear(self) -> None:
        """Clear all transcripts"""
        async with self._lock:
            self.current_transcript = ""
            self.final_transcripts.clear()
