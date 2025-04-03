## transcription_service

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
