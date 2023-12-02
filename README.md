# summarize

summarize.py will download a youtube video, transcribe it using [whisper.cpp](https://github.com/ggerganov/whisper.cpp), then summarize it using ChatGPT.

The summary is written to \[your_video_directory\]/summary.txt

This script is idempotent: if the youtube download succeeds, but the transcription fails, the next run will not re-download the youtube video. (However, summary will always be regenerated even if summary.txt already exists)

## setup

1. clone this repo. cd into it
2. git clone https://github.com/ggerganov/whisper.cpp.git
3. cd whisper.cpp, `bash ./models/download-ggml-model.sh large` then `make`
4. Customize the prompt in `summarize.py`:
```python
prompt = "You help read a raw unlabeled transcript that is a conversation between multiple people \
working together and create a coherent, concise, and easy to understand summary that extracts \
the main takeaways of the conversation.\
\nTranscript:"
```
5. Set your openai key: set `export OPENAI_API_KEY=sk-yourkeywhatever` in your shell

Run it: 
```bash
./summarize.py video_directory youtube_link
```