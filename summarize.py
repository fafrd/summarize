#!python

import openai
import os
import subprocess
import shutil
import sys

prompt = "The following is a raw unlabeled meeting transcript. Create a summary that extracts \
the points discussed, positions taken by individuals, and main takeaways/actions items.\
\nTranscript:"

def summarize_text(text, client):
    try:
        response = client.chat.completions.create(
            model="gpt-4-1106-preview",
            max_tokens=4096,
            temperature=0.2,
            top_p=0.5,
            messages=[
                {
                    "role": "user",
                    "content": prompt + f"\n\n{text}"
                }
            ]
        )
        return response
    except Exception as e:
        print(f"Error during summarization: {e}")
        return None

# Initialize OpenAI client
client = openai.OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY")
)

# Check number of arguments
if len(sys.argv) != 3:
    print("Usage: script_name.py [video_directory] [youtube_link]")
    sys.exit(1)

base_directory = os.getcwd()
if not os.path.exists(base_directory):
    print("Base directory doesn't exist")
    sys.exit(1)

video_directory = os.path.join(base_directory, sys.argv[1])
youtube_link = sys.argv[2]

# Navigate to the council directory
os.makedirs(video_directory, exist_ok=True)
os.chdir(video_directory)

# Check if there is any .m4a file before downloading with youtube-dl
m4a_files = [f for f in os.listdir() if f.endswith(".m4a")]
if not m4a_files:
    print("Downloading audio from YouTube...")
    subprocess.run(["youtube-dl", "-x", youtube_link])
    m4a_files = [f for f in os.listdir() if f.endswith(".m4a")]

# Convert audio using ffmpeg if audio.wav doesn't exist
if "audio.wav" not in os.listdir():
    print("Converting audio to 16kHz...")
    input_audio = m4a_files[0]
    subprocess.run(["ffmpeg", "-i", input_audio, "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le", "audio.wav"])

audio_path = os.path.join(video_directory, "audio.wav")
transcript_path = os.path.join(base_directory, sys.argv[1], "transcript.txt")
summarized_path = os.path.join(video_directory, "summary.txt")
whisper_path = os.path.join(base_directory, "whisper.cpp/main")
whisper_model_path = os.path.join(base_directory, "whisper.cpp/models/ggml-large.bin")

# Transcribe audio only if transcript file doesn't exist
if not os.path.exists(transcript_path) or os.path.getsize(transcript_path) == 0:
    print("Transcribing audio...")
    transcription_cmd = [
        whisper_path,
        "-m", whisper_model_path,
        "-f", audio_path
    ]
    with open(transcript_path, "w") as f:
        result = subprocess.run(transcription_cmd, stdout=f, text=True)
        if result.returncode != 0:
            print(f"Whisper command failed with return code: {result.returncode}")
            sys.exit(1)

cleanup_script_path = os.path.join(base_directory, "cleanup.sh")
gpt_summarize_path = os.path.join(base_directory, "gpt-summarize/gpt-summarize")

print("Cleaning up transcript...")
temp_path = transcript_path + ".tmp"
with open(temp_path, 'w') as f:
    result = subprocess.run([cleanup_script_path, transcript_path], stdout=f)
# If command was successful, replace the original with the cleaned file
if result.returncode == 0:
    shutil.move(temp_path, transcript_path)
else:
    # Optional: remove temporary file if command failed
    os.remove(temp_path)

print("Summarizing transcript...")
with open(transcript_path, "r") as transcript_file:
    transcript = transcript_file.read()

response = summarize_text(transcript, client)
summarized_text = response.choices[0].message.content
print(f"Prompt tokens used: {response.usage.prompt_tokens}. Completion tokens used: {response.usage.completion_tokens}")

if summarized_text:
    with open(summarized_path, "w") as f:
        f.write(summarized_text)
    print(f"Summarized to {summarized_path}")
else:
    print("Failed to summarize the transcript.")
