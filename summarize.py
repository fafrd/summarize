#!python

import openai
import os
import subprocess
import sys
import argparse

prompts = [
    # Baseline prompt. Results in thorough, neutral analysis with no investigative slant. Sometimes generic and will focus more on procedural details instead of substance.
    "The following is a raw, unlabeled meeting transcript. Create a past-tense bullet-point summary that extracts the points discussed, positions taken by individuals, and main takeaways/action items.\nTranscript:",

    # Investigative Journalist prompt. Takes a more investigative tone. Does not focus on procedural details and can sometimes gloss over points that do not work towards a narrative.
    "Background:\nYour name is Thomas Weisman, investigative journalist.\nAny provided dialogue was done via automatic transcription and is subject to errors.\n\n[Scene: 7pm, downtown Seattle. Raining. Miserable.]\nBANG BANG BANG.\n[Thomas looked up from his desk]\n\"Good thing you\'re still here, Thomas. We just got this in. The dialogue from another Mercer Island city council meeting.\"\n[\"Oh great\", thought Thomas. Another dull city council meeting to look over...]\n\"I need to you create another bullet-point summary for us. I think they\'re trying to slip something past us again, so make sure to be careful.\"\n[Thomas opened his laptop and began.]\nTranscript:",

    # Data Analyst prompt. Similar to previous, but more analytical and less investigative. Better at finding specific positions taken by speakers.
    "Background:\nYou are Alex Haberman, a skilled political analyst and part-time investigative assistant, known for your keen eye for detail and ability to distill complex information into clear insights. You work closely with renowned investigative journalist Thomas Weisman, who has a knack for uncovering the hidden truths in mundane data.\nAny provided dialogue was done via automatic transcription and is subject to errors.\n\nThomas has just handed you the transcript from the latest Mercer Island City Council meeting. \"I have a hunch there\'s more to this meeting than meets the eye,\" he says. \"We need to unravel the details. Can you create a bullet-point summary that digs deep into the points discussed, the positions taken by individuals, and the main takeaways or action items? Look out for anything that seems out of the ordinary or particularly significant.\"",
]

def request_completion(client, input):
    return client.chat.completions.create(
        model="gpt-4-1106-preview",
        #model="gpt-3.5-turbo-1106",
        max_tokens=4096,
        temperature=1.0,
        top_p=0.5,
        messages=[
            {
                "role": "user",
                "content": input
            }
        ]
    )


def download_subtitles(youtube_link):
    print("Downloading subtitles from YouTube...")
    subprocess.run(["youtube-dl", "--skip-download", "--write-auto-sub", youtube_link])

    # re-check
    vtt_files = [f for f in os.listdir() if f.endswith(".vtt")]
    if not vtt_files:
        print("No subtitles found. Exiting...")
        sys.exit(1)

    with open(vtt_files[0], 'r') as file:
        for _ in range(7):
            line = file.readline()
    transcript_path = "transcript.txt"
    with open(transcript_path, 'w') as output_file:
        output_file.write(line.strip())


def summarize_transcript(client):
    transcript_path = "transcript.txt"
    with open(transcript_path, "r") as transcript_file:
        transcript = transcript_file.read()

    # Generate intermediate summaries
    summaries = []
    for prompt in prompts:
        print("Summarizing transcript...")
        response = request_completion(client, prompt + f"\n\n{transcript}\n\nBullet-point summary:")
        summarized_text = response.choices[0].message.content
        print(f"Prompt tokens used: {response.usage.prompt_tokens}. Completion tokens used: {response.usage.completion_tokens}")

        summaries.append(summarized_text)

    html_output_path = "summaries.html"
    with open(html_output_path, "w") as html_file:
        html_file.write("<html><head><style>body { max-width: 900px; margin: 1em auto; background: #ffe0c6; color: black; font-family: serif; font-size: 1.3em; line-height: 1.5; } section { margin-bottom: 2em; } p { margin: 0.5em 0; } strong { font-weight: bold; }</style></head><body>\n")

        for prompt, summarized_text in zip(prompts, summaries):
            summarized_text = '<ul><li>' + summarized_text.replace('- ', '</li><li>') + '</li></ul>'
            summarized_text = summarized_text.replace('<li></li>', '')  # Remove empty list items

            if summarized_text:
                html_file.write("<section>\n")
                html_file.write(f"<p><strong>Prompt:</strong> {prompt}</p>\n")
                html_file.write(f"<p><strong>Summary:</strong><br>{summarized_text}</p>\n")
                html_file.write("</section>\n")
            else:
                print("Failed to summarize the transcript.")

        # Generate final summary
        print("Generating final summary...")
        message = "The following are summaries created by different analysts based on the same transcript. Each summary offers a unique perspective: the first is a baseline summary, the second is from an investigative journalist, and the third is from a political analyst. Please review these summaries and the original transcript. Then, create a final, comprehensive bullet-point summary. This summary should integrate the varying insights, emphasizing key policy discussions, individual council members' perspectives, and significant action plans. The final summary should offer both a broad overview and detailed analysis, suitable for a well-informed audience interested in municipal governance and policy nuances.\n\nTranscript:\n{transcript}\n\n"

        i = 1
        for summarized_text in summaries:
            message += f"Summary {i}:\n{summarized_text}\n\n"

        response = request_completion(client, message + "Final bullet-point summary:")
        summarized_text = response.choices[0].message.content
        print(f"Prompt tokens used: {response.usage.prompt_tokens}. Completion tokens used: {response.usage.completion_tokens}")

        summarized_text = '<ul><li>' + summarized_text.replace('- ', '</li><li>') + '</li></ul>'
        summarized_text = summarized_text.replace('<li></li>', '')  # Remove empty list items

        html_file.write("<section>\n")
        html_file.write(f"<p><strong>Final summary:</strong><br>{summarized_text}</p>\n")
        html_file.write("</section>\n")

        html_file.write("</body></html>")
        print(f"Summarized to {html_output_path}")


if not os.environ.get("OPENAI_API_KEY"):
    print("Please set OPENAI_API_KEY environment variable.")
    sys.exit(1)

# Initialize OpenAI client
client = openai.OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY")
)

# Create argument parser
parser = argparse.ArgumentParser(description='Process YouTube video for transcript summarization.')
parser.add_argument('video_directory', help='Directory to store video and audio files')
parser.add_argument('youtube_link', help='YouTube link to download audio from')
parser.add_argument('-d', '--download', action='store_true', help='Download subtitles only')
parser.add_argument('-s', '--summarize', action='store_true', help='Summarize preexisting transcript')

# Parse arguments
args = parser.parse_args()

if not args.download and not args.summarize:
    args.download = True
    args.summarize = True

video_directory = os.path.join(os.getcwd(), args.video_directory)
youtube_link = args.youtube_link

# Navigate to the directory
os.makedirs(video_directory, exist_ok=True)
os.chdir(video_directory)

# Check if there is a 'transcript.txt' file
if os.path.exists("transcript.txt"):
    if args.download:
        print("Subtitles already present. Skipping download.")
else:
    if args.download:
        download_subtitles(youtube_link)
    else:
        print("No subtitles found. Download with -d")
        sys.exit(1)

if args.summarize:
    summarize_transcript(client)
