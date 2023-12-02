# summarize

summarize.py will download a youtube video, transcribe it using [whisper.cpp](https://github.com/ggerganov/whisper.cpp), then summarize it using ChatGPT.

The script uses ChatGPT's new 128k context model. This should support up to about 100,000 words, which is maybe 10 hours of discussion. At $0.01/1k tokens, summarizing a transcript costs roughly 10 cents per hour.

## setup

1. clone this repo. cd into it
2. git clone https://github.com/ggerganov/whisper.cpp.git
3. cd whisper.cpp, `bash ./models/download-ggml-model.sh large` then `make`
4. Customize the prompt in `summarize.py`:
```python
prompt = "The following is a raw unlabeled meeting transcript. Create a summary that extracts \
the points discussed, positions taken by individuals, and main takeaways/action items.\
\nTranscript:"
```
5. Set your openai key: set `export OPENAI_API_KEY=sk-yourkeywhatever` in your shell

Run it: 
```bash
./summarize.py video_directory youtube_link
```

### notes

The transcript is saved to `[your_video_directory]/transcript.txt`, and the summary to `[your_video_directory]/summary.txt`.

This script is idempotent: if the youtube download succeeds, but the transcription fails, the next run will not re-download the youtube video. (However, summary will always be regenerated even if summary.txt already exists)

## example

I've been using this to summarize my local city council meetings. For example, given this [70-minute council meeting](https://www.youtube.com/watch?v=rivy4Afgeyk), the following summary is produced:

> The Mercer Island City Council held a regular hybrid meeting on November 21, 2023. Mayor Salim Nice presided over the meeting, which included roll call, Pledge of Allegiance, and approval of the agenda. City Manager Jesse Bond provided a report covering various topics, including the permanent closure of City Hall, upcoming meetings, capital projects, and community events.
> 
> Key points discussed and actions taken during the meeting included:
> 
> 1. Public Comment: Two individuals signed up to speak, but only one, Will Orendorff, appeared to advocate for the Mercer Island Country Club's efforts to bring back the tennis bubble.
> 
> 2. Consent Agenda: The consent agenda was approved with one item, AB 6369 (Town Center Parking Plan Adoption), pulled for separate discussion and later approved.
> 
> 3. Sound Cities Association Voting Delegates: Councilmember Weinberg was appointed as the voting delegate for the annual meeting on December 6, and Councilmember Jacobson for the caucus meeting on December 13.
> 
> 4. Mid-Biennial Budget Public Hearing: The public hearing was opened and closed with no public testimony. Finance Director Matt Mornick presented a financial status update and proposed mid-biennial budget adjustments. The council discussed and approved forwarding proposed budget adjustments for final consideration on December 5.
> 
> 5. Utility Rates for 2024: The council reviewed proposed rate increases for water, sewer, stormwater, and emergency medical service utilities. Utility Board Chair Tim O'Connell provided insights on the rate adjustments.
> 
> 6. Property Tax Levies and Other Resolutions: The council adopted ordinances and resolutions related to property tax levies, a declaration of intent for water bond issuance, and NORCOM's 2024 budget allocation.
> 
> 7. Other Business and Planning Schedule: City Manager Bond updated the council on the status of the Slater room for future meetings and the mayoral and deputy mayoral appointments scheduled for January 2.
> 
> 8. Council Reports: Councilmembers shared updates and expressed pride in the Mercer Island High School band's participation in the Macy's Thanksgiving Day Parade.
> 
> The meeting concluded with an executive session to discuss pending or potential litigation and real estate matters. No action was taken following the executive session. The next hybrid meeting is scheduled for December 5, 2023.