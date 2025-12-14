"""Text-to-Speech API routes."""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from gtts import gTTS
import io
from ...utils.logger import logger

router = APIRouter(tags=["tts"])


class TTSRequest(BaseModel):
    """Request model for TTS."""
    text: str
    lang: str = "en"
    slow: bool = False


@router.post("/tts/speak")
async def text_to_speech(request: TTSRequest):
    """
    Convert text to speech and return audio stream.

    Args:
        text: Text to convert to speech
        lang: Language code (default: 'en')
        slow: Whether to speak slowly (default: False)

    Returns:
        Audio file as MP3 stream
    """
    try:
        if not request.text or len(request.text.strip()) == 0:
            raise HTTPException(status_code=400, detail="Text cannot be empty")

        if len(request.text) > 5000:
            raise HTTPException(status_code=400, detail="Text too long (max 5000 characters)")

        logger.info(f"Generating TTS for {len(request.text)} characters")

        # Generate speech using gTTS
        tts = gTTS(text=request.text, lang=request.lang, slow=request.slow)

        # Save to in-memory buffer
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)

        logger.info("TTS audio generated successfully")

        # Return as streaming response
        return StreamingResponse(
            audio_buffer,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "inline",
                "Cache-Control": "no-cache"
            }
        )

    except Exception as e:
        logger.error(f"TTS generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"TTS generation failed: {str(e)}")
