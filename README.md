# summarize

summarize.py will download a youtube video, transcribe it using [whisper.cpp](https://github.com/ggerganov/whisper.cpp), then summarize it using ChatGPT.

## Untested setup instructions

1. clone this repo. cd into it
2. cd into gpt-summarize, run `go get` then `go build`
3. git clone https://github.com/ggerganov/whisper.cpp.git
4. cd whisper.cpp, `bash ./models/download-ggml-model.sh large` then `make`
5. Change the prompt in `summarize.py` to something that fits your project:
```python
llm_prompt = """
You help read a raw unlabeled transcript that is a conversation between multiple people \
working together and create a coherent, concise, and easy to understand summary that extracts \
the main takeaways of the conversation.
"""
```
6. Set your openai key: set `export OPENAI_API_KEY=sk-yourkeywhatever` in your shell

Run it: 
```bash
./summarize.py videos/summary-090123 YOUTUBE_LINK
```