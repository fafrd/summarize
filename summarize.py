#!python

import openai
import os
import subprocess
import shutil
import argparse
import sys

prompt = "The following is a raw unlabeled meeting transcript. Create a summary that extracts \
the points discussed, positions taken by individuals, and main takeaways/action items.\
\nTranscript:"

def summarize_text(text, client):
    try:
        response = client.chat.completions.create(
            model="gpt-4-1106-preview",
            max_tokens=4096,
            temperature=1.0,
            top_p=0.5,
            messages=[
                {
                    "role": "user",
                    "content": prompt + f"\n\n{text}\n\nComprehensive summary:"
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

# Create argument parser
parser = argparse.ArgumentParser(description='Process YouTube video for transcript summarization.')
parser.add_argument('video_directory', help='Directory to store video and audio files')
parser.add_argument('youtube_link', help='YouTube link to download audio from')

# Parse arguments
args = parser.parse_args()

base_directory = os.getcwd()
video_directory = os.path.join(base_directory, args.video_directory)
youtube_link = args.youtube_link

# Navigate to the directory
os.makedirs(video_directory, exist_ok=True)
os.chdir(video_directory)

# Check if there is any .vtt file before downloading with youtube-dl
vtt_files = [f for f in os.listdir() if f.endswith(".vtt")]
if not vtt_files:
    print("Downloading subtitles from YouTube...")
    subprocess.run(["youtube-dl", "--skip-download", "--write-auto-sub", youtube_link])
    vtt_files = [f for f in os.listdir() if f.endswith(".vtt")]

if not vtt_files:
    print("No subtitles found. Exiting...")
    sys.exit(1)

with open(vtt_files[0], 'r') as file:
    for i in range(7):
        line = file.readline()
transcript_path = os.path.join(base_directory, sys.argv[1], "transcript.txt")
with open(transcript_path, 'w') as output_file:
    output_file.write(line.strip())

print("Summarizing transcript...")
gpt_summarize_path = os.path.join(base_directory, "gpt-summarize/gpt-summarize")
with open(transcript_path, "r") as transcript_file:
    transcript = transcript_file.read()

response = summarize_text(transcript, client)
summarized_text = response.choices[0].message.content
summarized_path = os.path.join(video_directory, "summary.txt")
print(f"Prompt tokens used: {response.usage.prompt_tokens}. Completion tokens used: {response.usage.completion_tokens}")

if summarized_text:
    with open(summarized_path, "w") as f:
        f.write(summarized_text)
    print(f"Summarized to {summarized_path}")
else:
    print("Failed to summarize the transcript.")
