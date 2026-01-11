from collections import deque


class TranscriptionBuffer:
    def __init__(self, max_history: int = 100):
        self.current_transcript = ""
        self.final_transcripts: deque[str] = deque(maxlen=max_history)

    async def update_interim(self, text: str) -> None:
        """Update the current interim transcript"""
        self.current_transcript = text

    async def finalize_current(self) -> str:
        """Finalize the current transcript and return it"""
        if self.current_transcript:
            final = self.current_transcript.strip()
            if final:
                self.final_transcripts.append(final)
            self.current_transcript = ""
            return final
        return ""

    async def clear(self) -> None:
        """Clear all transcripts"""
        self.current_transcript = ""
        self.final_transcripts.clear()
