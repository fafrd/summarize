# Summarize

summarize.py will download a youtube video, transcribe it using whisper.cpp, then summarize it using AI.

## Developing

First set up the backend:

    cd api
    poetry install
    poetry run python app.py

    git clone https://github.com/ggerganov/whisper.cpp.git
    cd whisper.cpp
    bash ./models/download-ggml-model.sh large-v3-turbo
    cmake -B build
    cmake --build build --config Release

Then set up the frontend:

    cd ../../frontend
    npm run dev