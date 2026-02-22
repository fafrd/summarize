# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

YouTube video summarization application that downloads city council meeting videos, transcribes them using whisper.cpp, and generates AI summaries. Consists of a Python Flask backend with background daemon processing and a Next.js frontend.

## Environment Variables

### Required
- `OPENROUTER_API_KEY`: API key for OpenRouter LLM service (required for summarization)

### Optional - Backend Configuration
- `API_PORT`: Port for Flask server (default: `3669`)
- `API_HOST`: Host for Flask server (default: `0.0.0.0`)
- `DATABASE_PATH`: Path to SQLite database file (default: `summarize.db`)
- `TEMP_DIR`: Directory for temporary files (default: `temp`)
- `POLLING_INTERVAL`: Seconds between daemon polling cycles (default: `5`)

### Optional - Audio Processing
- `AUDIO_SAMPLE_RATE`: Sample rate for WAV conversion (default: `16000`)
- `MP3_QUALITY`: Quality setting for MP3 download (default: `192`)

### Optional - Whisper Configuration
- `WHISPER_BASE_DIR`: Base directory for whisper.cpp (default: `whisper.cpp`)
- `WHISPER_ENTROPY_THRESHOLD`: Entropy threshold for whisper (default: `2.8`)
- `WHISPER_BEAM_SIZE`: Beam size for whisper (default: `5`)
- `WHISPER_MAX_CONTEXT`: Max context for whisper (default: `64`)

### Optional - LLM Configuration
- `LLM_BASE_URL`: Base URL for LLM API (default: `https://openrouter.ai/api/v1`)
- `LLM_MODEL`: Model to use for summarization (default: `openai/gpt-4o-mini`)
- `LLM_TEMPERATURE`: Temperature for LLM generation (default: `0.7`)
- `LLM_MAX_TOKENS`: Max tokens for LLM response (default: `16384`)

### Optional - Frontend
- `NEXT_PUBLIC_BACKEND_PORT`: Backend port number (default: `3669`). Frontend automatically uses current browser hostname with this port.
- `NEXT_PUBLIC_POLL_INTERVAL`: Milliseconds between frontend polling (default: `1000`)

**Note:** Copy `.env.example` to `.env` and fill in required values before running.

## Development Commands

### Backend (api/)
```bash
cd api
cp ../.env.example ../.env  # Copy and edit with your API key
uv sync                      # Install dependencies
source .venv/bin/activate    # Activate virtual environment
uv run python app.py         # Start API server and daemon
```

### Frontend (frontend/)
```bash
cd frontend
npm i                # Install dependencies
npm run dev -- -p 4000    # Start dev server on port 4000 (automatically connects to backend on same hostname)
npm run build        # Build for production
npm run lint         # Run linter
```

### Whisper.cpp Setup (one-time)
```bash
cd api
git clone https://github.com/ggerganov/whisper.cpp.git
cd whisper.cpp
bash ./models/download-ggml-model.sh large-v3-turbo
cmake -B build
cmake --build build --config Release
```

## Architecture

### Backend Components

- **app.py**: Main entry point running Flask API server and background daemon in separate threads
- **config.py**: Centralized configuration management with environment variable validation
- **helpers.py**: Shared utility functions (entry creation, filename sanitization, path helpers)
- **server.py**: Flask API with `/entries` endpoint (GET/POST) for video management
- **daemon.py**: Background processor that polls database for unprocessed videos
- **model.py**: Peewee ORM model for SQLite database (`entry` table)
- **downloader.py**: YouTube audio download using yt-dlp, converts to MP3 then WAV
- **transcriber.py**: Wrapper around whisper.cpp for audio transcription
- **summarizer.py**: LLM integration for transcript summarization

### Processing Pipeline

Videos flow through these states in `entry.status`:
1. `not_started` → `downloading` → `converting` → `transcribing` → `summarizing` → `done`
2. Any step can fail and set status to `error`
3. Daemon resumes interrupted jobs on restart using file existence checks

### File Storage

All temporary files stored in `api/temp/`:
- `{entry_id}_{sanitized_name}.mp3` - Downloaded audio
- `{entry_id}_{sanitized_name}.wav` - Converted 16kHz WAV for whisper
- `{entry_id}_{sanitized_name}.wav.txt` - Raw transcription output

### Database Schema

SQLite table `entry`:
- `id` (primary key)
- `name` (video title, initially URL then updated to actual title)
- `status` (processing state)
- `url` (YouTube URL, unique)
- `transcription` (cleaned transcript text)
- `summary` (AI-generated summary)
- `insertion_date` (datetime when added)

### Frontend Features

- Submit YouTube URLs (single videos or playlists)
- Real-time status updates via polling
- Sortable columns (Name, Status, Added At)
- Search filtering
- Multi-select summaries with bulk copy to clipboard
- Markdown rendering of summaries

## Customization

- Edit summarization prompt in `api/summarizer.py`
- Change LLM model via `LLM_MODEL` environment variable
- Adjust whisper parameters via environment variables (see Environment Variables section)
- Modify frontend polling interval via `NEXT_PUBLIC_POLL_INTERVAL`

## Important Implementation Details

### Resume Logic
The daemon intelligently resumes interrupted processing by checking:
1. Database transcription field → resume at "summarizing"
2. Existing `.wav.txt` file → resume at "summarizing" 
3. Current status preservation for active states
4. File existence fallbacks for determining restart point

### Error Handling
- Failed videos get `error` status and are skipped
- Re-adding a video with `error` status resets it to `not_started`
- Transcriber checks for existing transcript files to avoid re-work

### Logging
- Application uses structlog for structured logging
- Werkzeug HTTP request logs are disabled via `logging.getLogger('werkzeug').disabled = True`
- Key events logged: video processing start/complete, errors, daemon status