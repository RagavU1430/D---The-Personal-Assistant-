from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.config import settings

router = APIRouter(tags=["voice"])


class SpeakRequest(BaseModel):
    text: str = Field(..., min_length=1)
    rate: float = Field(default=1.0, ge=0.5, le=2.0)
    pitch: float = Field(default=1.0, ge=0.5, le=1.5)


class VoiceStatusResponse(BaseModel):
    enabled: bool
    stt_supported: bool
    tts_supported: bool
    active_profile: str


@router.get("/voice/status", response_model=VoiceStatusResponse)
async def get_voice_status() -> VoiceStatusResponse:
    return VoiceStatusResponse(
        enabled=settings.enable_voice,
        stt_supported=True,
        tts_supported=True,
        active_profile="D - Futuristic Assistant (JARVIS mode)",
    )


@router.post("/voice/speak")
async def process_speech(request: SpeakRequest) -> dict[str, object]:
    return {
        "status": "ready",
        "text": request.text,
        "rate": request.rate,
        "pitch": request.pitch,
        "engine": "web_speech_synthesis",
    }
