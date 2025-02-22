# Summarize

summarize.py will download a youtube video, transcribe it using whisper.cpp, then summarize it using AI.

## Developing

First set up the backend:

    cd api
    uv sync
    source .venv/bin/activate

    git clone https://github.com/ggerganov/whisper.cpp.git
    cd whisper.cpp
    bash ./models/download-ggml-model.sh large-v3-turbo
    cmake -B build
    cmake --build build --config Release

    cd ..
    uv run python app.py

Then set up the frontend:

    cd ../../frontend
    npm i
    npm run dev
    # or
    npm run build && npm run start
