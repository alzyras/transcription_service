## transcription_service (Whisper + FastAPI)

## Installation

To create and install virtual environment:

```bash
uv sync
```

## Running the service

To run the service:
```bash
python -m uvicorn transcription_service.transcribe:app --reload
```

or

```bash
chmod +x run_api.sh
./run_api.sh
```

This command does the same. The service runs by default on http://127.0.0.1:8000.


## Using the API

By sending a mp3 file:
```python
def transcribe_audio(file_path, words_per_sentence=5):
    """Transcribe audio using an API to generate SRT subtitles."""
    url = "http://127.0.0.1:8000/transcribe/"
    with open(file_path, "rb") as f:
        files = {"file": (file_path, f, "audio/mpeg")}
        data = {"words_per_sentence": words_per_sentence}
        response = requests.post(url, files=files, data=data)
    
    # Return the SRT content in memory
    if response.status_code == 200:
        return response.content.decode()  # Ensure we return a string
    else:
        raise Exception(f"Failed to fetch subtitles: {response.text}")
```
By sending an AudioSegment:
```python
def send_audiosegment_to_transcriber(audio_segment: AudioSegment, words_per_sentence: int = 5):
    """Send an AudioSegment object to the transcription API and get subtitles."""
    audio_bytes = BytesIO()
    audio_segment.export(audio_bytes, format="mp3")  # Export to MP3 in-memory
    audio_bytes.seek(0)

    files = {"file": ("audio.mp3", audio_bytes, "audio/mpeg")}
    data = {"words_per_sentence": str(words_per_sentence)}

    response = requests.post(
        FASTAPI_URL,
        files=files,
        data=data
    )

    if response.status_code == 200:
        with open("output.srt", "wb") as srt_file:
            srt_file.write(response.content)
        print("Transcription saved as output.srt")
    else:
        print("Error:", response.text)
```
