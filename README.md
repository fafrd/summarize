# summarize

summarize.py will download the auto-generated subtitles for a youtube video and summarize them using ChatGPT.

This script takes on a summary-of-summaries method, which I find works well. It will ask the AI to make 3 different summaries from slightly different prompts, then re-prompt the AI to create a final summary from the intermediate ones.

The script uses ChatGPT's new 128k context model. This should support up to about 100,000 words, which is maybe 10 hours of discussion. At $0.01 per 1k tokens times 4 summarizations, summarizing a transcript costs roughly 40 cents per hour.

### example

I've been using this to summarize my local city council meetings. For example, given this [2 hour 45 minute council meeting](https://www.youtube.com/watch?v=a8uXZQ8XDrY), the following summary is produced:

> <ul><li>The Mercer Island City Council is actively working on updating the comprehensive plan to comply with House Bill 1220, focusing on housing needs across different income levels and addressing potential racially disparate impacts.
> </li><li>The council administered Oaths of Office to newly elected members Dave Rosenbom, Wendy Wer, Craig Reynolds, and Jake Jacobson, followed by the election of council member Nce as mayor and Dave Rosenbom as Deputy Mayor.
> </li><li>A brief recess was taken for pictures and seating arrangements after the elections.
> </li><li>City manager Jesse Bond updated on various city projects, including City Hall transitions, community center maintenance, and the Island Crestway project, and celebrated the success of the Illuminate MI event.
> </li><li>The Racially Disparate Impacts (RDI) evaluation and Land Capacity Analysis (LCA) supplement were presented, revealing a shortfall of 143 units for housing below 120% AMI and suggesting policy amendments to mitigate racially disparate impacts and displacement risks.
> </li><li>Three options to address the housing capacity shortfall were proposed:
> <ol>
>   <li>Increasing height in the town center by one story.</li>
>   <li>Allowing multifamily residential uses in the commercial office (CO) zone.</li>
>   <li>Increasing maximum density in the MF3 zone.</li>
> </ol>
> </li><li>The council members shared individual reports, expressing the need for further information and discussion on the proposed options, particularly focusing on infrastructure and displacement concerns in areas like Shorewood.
> </li><li>Councilmember Reynolds highlighted the potential of ADUs in single-family zones, while Councilmember Andall called for additional analysis on the Planned Business Zone (PBZ) as a possible solution.
> </li><li>Councilmember Jacobson showed hesitance towards rezoning in the Shorewood area, whereas Councilmember Wer favored Option B and the inclusion of PBZ in the analysis.
> </li><li>Deputy Mayor Rosenbom emphasized the significance of transit access in affordable housing planning, and Mayor Nce proposed a limited incremental scaling approach in the CO zone to maintain flexibility and minimize displacement.
> </li><li>The council agreed to further discuss the options at the next meeting on January 16, 2023, with staff working to provide more insights on the PBZ.
> </li><li>The Housing Work Group will reconvene to draft the housing element of the comprehensive plan, with public outreach, surveys, and an open house planned to gather community input before the Planning Commission's public hearing.
> </li><li>The council will enter an executive session to discuss pending or potential litigation, with no action expected to follow.
> </li><li>Overall, the council recognized the complexity of planning for affordable housing and the necessity for ongoing advocacy and collaboration with state and county entities.</li></ul>

(Note the misspelled names- this is due to automatic transcription)

## setup

1. Install youtube-dl from [their github](https://github.com/ytdl-org/youtube-dl), or with `brew install youtube-dl`
2. clone this repo. cd into it
3. Customize the prompt in `summarize.py`:
```python
prompt = "The following is a raw unlabeled meeting transcript. Create a summary that extracts \
the points discussed, positions taken by individuals, and main takeaways/action items.\
\nTranscript:"
```
4. Set your openai key: set `export OPENAI_API_KEY=sk-yourkeywhatever` in your shell

Run it: 
```bash
./summarize.py video_directory youtube_link
```

## notes

- The raw transcript is saved to `[your_video_directory]/transcript.txt`
- The summaries are saved to `[your_video_directory]/summaries.html`
