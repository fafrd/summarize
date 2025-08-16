# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

YouTube video summarization application that downloads city council meeting videos, transcribes them using whisper.cpp, and generates AI summaries. Consists of a Python Flask backend with background daemon processing and a Next.js frontend.

## Development Commands

### Backend (api/)
```bash
cd api
uv sync                    # Install dependencies
source .venv/bin/activate  # Activate virtual environment  
uv run python app.py       # Start API server (port 3669) and daemon
```

### Frontend (frontend/)
```bash
cd frontend
npm i                                                        # Install dependencies
NEXT_PUBLIC_SERVER_URL=http://localhost:3669 npm run dev    # Start dev server
npm run build                                               # Build for production
npm run lint                                                # Run linter
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
- **server.py**: Flask API with `/entries` endpoint (GET/POST) for video management
- **daemon.py**: Background processor that polls database for unprocessed videos
- **model.py**: Peewee ORM model for SQLite database (`entry` table)
- **downloader.py**: YouTube audio download using yt-dlp, converts to MP3 then WAV
- **transcriber.py**: Wrapper around whisper.cpp for audio transcription
- **summarizer.py**: LLM integration for transcript summarization (currently OpenRouter)

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

## Configuration

### Environment Variables
- `OPENROUTER_API_KEY`: Required for LLM summarization

### Customization
- Edit summarization prompt in `api/summarizer.py`
- LLM model configured in `summarizer.py` (currently `google/gemini-2.0-flash-exp`)

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