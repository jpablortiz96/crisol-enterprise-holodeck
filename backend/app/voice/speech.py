import gc
import hashlib
import os
import re
import unicodedata
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from app.telemetry.events import emit_event


AUDIO_ROOT = Path(__file__).resolve().parents[2] / ".crisol_audio"
load_dotenv(AUDIO_ROOT.parents[1] / ".env")
MAX_SPEECH_TEXT_LENGTH = 450
DEFAULT_VOICE = "en-US-JennyNeural"
VOICE_STYLE_CONFIG = {
    "calm": ("AZURE_SPEECH_VOICE_CALM", "en-US-JennyNeural"),
    "urgent": ("AZURE_SPEECH_VOICE_URGENT", "en-US-AvaMultilingualNeural"),
    "analytical": ("AZURE_SPEECH_VOICE_ANALYTICAL", "en-US-DavisNeural"),
    "supportive": ("AZURE_SPEECH_VOICE_SUPPORTIVE", "en-US-SaraNeural"),
}
KNOWN_PERSONA_VOICE_CONFIG = {
    "VP Operations": ("AZURE_SPEECH_VOICE_VP", "en-US-AvaMultilingualNeural"),
    "Product Manager": ("AZURE_SPEECH_VOICE_PM", "en-US-JennyNeural"),
    "Database Lead": ("AZURE_SPEECH_VOICE_DB", "en-US-DavisNeural"),
    "Support Lead": ("AZURE_SPEECH_VOICE_SUPPORT", "en-US-SaraNeural"),
}


def is_speech_configured() -> bool:
    return bool(os.getenv("AZURE_SPEECH_KEY") and os.getenv("AZURE_SPEECH_REGION"))


def voice_for_persona(
    persona: str,
    voice_style: str | None = None,
    pressure_profile: str | None = None,
) -> str:
    known_voice = KNOWN_PERSONA_VOICE_CONFIG.get(persona)
    if known_voice:
        env_name, default_voice = known_voice
        return os.getenv(env_name) or default_voice
    normalized_style = (voice_style or "").strip().lower()
    if normalized_style in VOICE_STYLE_CONFIG:
        env_name, default_voice = VOICE_STYLE_CONFIG[normalized_style]
        return os.getenv(env_name) or default_voice
    if (pressure_profile or "").strip().lower() in {"high", "critical"}:
        env_name, default_voice = VOICE_STYLE_CONFIG["urgent"]
        return os.getenv(env_name) or default_voice
    return DEFAULT_VOICE


def sanitize_audio_filename(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    sanitized = re.sub(r"[^A-Za-z0-9_-]+", "-", normalized).strip("-_").lower()
    return sanitized[:80] or "audio"


def synthesize_npc_line(
    text: str,
    persona: str,
    session_id: str | None = None,
    event_id: str | None = None,
    voice_style: str | None = None,
    pressure_profile: str | None = None,
) -> dict[str, Any]:
    if not is_speech_configured():
        return _record_voice_result(_text_fallback(), session_id)

    voice_name = voice_for_persona(persona, voice_style, pressure_profile)
    safe_text = " ".join(text.split())[:MAX_SPEECH_TEXT_LENGTH]
    if not safe_text:
        return _record_voice_result(_azure_fallback(voice_name), session_id)

    safe_session_id = sanitize_audio_filename(session_id or "voice-preview")
    safe_event_id = sanitize_audio_filename(event_id or "event")
    safe_persona = sanitize_audio_filename(persona)
    digest_source = "|".join((safe_session_id, safe_event_id, persona, safe_text))
    digest = hashlib.sha256(digest_source.encode("utf-8")).hexdigest()[:12]
    filename = f"{safe_event_id}-{safe_persona}-{digest}.mp3"
    output_directory = AUDIO_ROOT / safe_session_id
    output_path = output_directory / filename
    audio_url = f"/audio/{safe_session_id}/{filename}"

    if output_path.is_file() and output_path.stat().st_size > 0:
        return _record_voice_result(_success_result(voice_name, audio_url), session_id)

    try:
        import azure.cognitiveservices.speech as speechsdk
    except ImportError:
        return _record_voice_result(_azure_fallback(voice_name), session_id)

    output_directory.mkdir(parents=True, exist_ok=True)

    result = None
    synthesizer = None
    audio_config = None
    try:
        speech_config = speechsdk.SpeechConfig(
            subscription=os.environ["AZURE_SPEECH_KEY"],
            region=os.environ["AZURE_SPEECH_REGION"],
        )
        speech_config.speech_synthesis_voice_name = voice_name
        output_format = getattr(
            speechsdk.SpeechSynthesisOutputFormat,
            "Audio24Khz48KBitRateMonoMp3",
            None,
        )
        if output_format is not None:
            speech_config.set_speech_synthesis_output_format(output_format)

        audio_config = speechsdk.audio.AudioOutputConfig(filename=str(output_path))
        synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=speech_config,
            audio_config=audio_config,
        )
        result = synthesizer.speak_text_async(safe_text).get()

        if (
            result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted
            and output_path.is_file()
            and output_path.stat().st_size > 0
        ):
            return _record_voice_result(_success_result(voice_name, audio_url), session_id)
    except Exception:
        pass
    finally:
        result = None
        synthesizer = None
        audio_config = None
        gc.collect()

    try:
        output_path.unlink(missing_ok=True)
    except OSError:
        pass
    return _record_voice_result(_azure_fallback(voice_name), session_id)


def configured_voices() -> dict[str, str]:
    voices = {
        persona: os.getenv(env_name) or default_voice
        for persona, (env_name, default_voice) in KNOWN_PERSONA_VOICE_CONFIG.items()
    }
    voices.update(
        {
            f"style:{style}": os.getenv(env_name) or default_voice
            for style, (env_name, default_voice) in VOICE_STYLE_CONFIG.items()
        }
    )
    return voices


def _success_result(voice_name: str, audio_url: str) -> dict[str, Any]:
    return {
        "enabled": True,
        "provider": "azure-speech",
        "voice_name": voice_name,
        "audio_url": audio_url,
        "format": "mp3",
        "message": "Azure Speech synthesis completed.",
    }


def _text_fallback() -> dict[str, Any]:
    return {
        "enabled": False,
        "provider": "text-only",
        "voice_name": None,
        "audio_url": None,
        "format": None,
        "message": "Speech is not configured; using text fallback.",
    }


def _azure_fallback(voice_name: str) -> dict[str, Any]:
    return {
        "enabled": False,
        "provider": "azure-speech-fallback",
        "voice_name": voice_name,
        "audio_url": None,
        "format": None,
        "message": "Azure Speech synthesis failed; using text fallback.",
    }


def _record_voice_result(
    result: dict[str, Any],
    session_id: str | None,
) -> dict[str, Any]:
    emit_event(
        "voice_synthesized" if result["provider"] == "azure-speech" else "voice_fallback",
        {
            "session_id": session_id,
            "provider": result["provider"],
            "voice_enabled": result["enabled"],
            "status": "completed" if result["enabled"] else "fallback",
        },
    )
    return result
