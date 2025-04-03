import os
import tempfile
from io import BytesIO
from typing import AsyncGenerator

import transcription_service

import whisper
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import StreamingResponse

app = FastAPI()

CACHE_DIR = "whisper_cache"
os.makedirs(CACHE_DIR, exist_ok=True)
os.environ["WHISPER_CACHE_DIR"] = CACHE_DIR

MODEL_SIZE = os.environ.get("WHISPER_MODEL_SIZE", "small")
model = whisper.load_model(MODEL_SIZE, download_root=CACHE_DIR)

def split_text(text: str, n: int) -> list[str]:
    """Splits text into chunks of n words."""
    words = text.split()
    return [" ".join(words[i : i + n]) for i in range(0, len(words), n)]

def format_time(seconds: float) -> str:
    """Formats time in SRT format (HH:MM:SS,mmm)."""
    milliseconds = int((seconds % 1) * 1000)
    total_seconds = int(seconds)
    minutes, seconds = divmod(total_seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"

@app.post("/transcribe/")
async def transcribe(
    file: UploadFile = File(...), words_per_sentence: int = Form(...)
) -> StreamingResponse:
    """Transcribes an uploaded audio file and returns subtitles in SRT format."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
        audio_path = tmp.name
        tmp.write(await file.read())

    try:
        result = model.transcribe(audio_path)
        srt_content = BytesIO()
        index = 1

        for segment in result.get("segments", []):
            start, end, text = segment["start"], segment["end"], segment["text"]
            text_chunks = split_text(text, words_per_sentence)
            total_words = len(text.split())
            duration_per_word = (end - start) / max(total_words, 1)

            for chunk in text_chunks:
                chunk_words = len(chunk.split())
                chunk_end = start + chunk_words * duration_per_word
                srt_content.write(f"{index}\n".encode())
                srt_content.write(
                    f"{format_time(start)} --> {format_time(chunk_end)}\n".encode()
                )
                srt_content.write(f"{chunk}\n\n".encode())
                start = chunk_end
                index += 1

        srt_content.seek(0)
        return StreamingResponse(
            srt_content,
            media_type="text/plain",
            headers={"Content-Disposition": f"attachment; filename={file.filename}.srt"},
        )
    finally:
        os.remove(audio_path)