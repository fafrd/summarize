# Summarize

summarize.py will download a youtube video, transcribe it using whisper.cpp, then summarize it using AI.

## Setup

First build whisper.cpp and authenticate with Google Cloud:

    # Install the Google Cloud CLI
    curl https://sdk.cloud.google.com | bash
    exec -l $SHELL
    gcloud init
    gcloud auth application-default login

    cd api

    # Install whisper.cpp to this directory
    git clone https://github.com/ggerganov/whisper.cpp.git
    cd whisper.cpp
    bash ./models/download-ggml-model.sh large-v3-turbo
    cmake -B build
    cmake --build build --config Release

Start the backend in `api/`:

    cd api
    uv sync
    source .venv/bin/activate
    uv run python app.py

In another terminal, start the frontend in `frontend/`:

    cd frontend
    npm i
    NEXT_PUBLIC_SERVER_URL=http://localhost:3669 npm run dev

You can the edit the prompt in `api/summarizer.py`.
