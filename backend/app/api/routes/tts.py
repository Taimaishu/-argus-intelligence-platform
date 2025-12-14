"""Text-to-Speech API routes."""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from gtts import gTTS
from pydub import AudioSegment
from pydub.effects import speedup
import io
from ...utils.logger import logger

router = APIRouter(tags=["tts"])


class TTSRequest(BaseModel):
    """Request model for TTS."""
    text: str
    lang: str = "en"
    speed: float = Field(default=1.0, ge=0.5, le=2.5, description="Playback speed multiplier (0.5x to 2.5x)")


@router.post("/tts/speak")
async def text_to_speech(request: TTSRequest):
    """
    Convert text to speech and return audio stream with adjustable speed.

    Args:
        text: Text to convert to speech
        lang: Language code (default: 'en')
        speed: Playback speed multiplier (0.5x to 2.5x, default: 1.0)

    Returns:
        Audio file as MP3 stream
    """
    try:
        if not request.text or len(request.text.strip()) == 0:
            raise HTTPException(status_code=400, detail="Text cannot be empty")

        if len(request.text) > 5000:
            raise HTTPException(status_code=400, detail="Text too long (max 5000 characters)")

        logger.info(f"Generating TTS for {len(request.text)} characters at {request.speed}x speed")

        # Generate speech using gTTS
        tts = gTTS(text=request.text, lang=request.lang, slow=False)

        # Save to in-memory buffer
        temp_buffer = io.BytesIO()
        tts.write_to_fp(temp_buffer)
        temp_buffer.seek(0)

        # Apply speed adjustment if needed
        if abs(request.speed - 1.0) > 0.01:  # Only process if speed is different from 1.0
            logger.info(f"Applying {request.speed}x speed adjustment")
            audio = AudioSegment.from_mp3(temp_buffer)

            # Apply speed change
            if request.speed > 1.0:
                # Speed up
                audio = speedup(audio, playback_speed=request.speed)
            else:
                # Slow down by changing frame rate
                audio = audio._spawn(audio.raw_data, overrides={
                    "frame_rate": int(audio.frame_rate * request.speed)
                })
                audio = audio.set_frame_rate(44100)  # Normalize to standard frame rate

            # Export to buffer
            audio_buffer = io.BytesIO()
            audio.export(audio_buffer, format="mp3", bitrate="128k")
            audio_buffer.seek(0)
        else:
            # No speed adjustment needed
            audio_buffer = temp_buffer

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
