"use client";

import ReactMarkdown from "react-markdown";

export default function SummaryPanel({ entries, selectedVideos, onCopy }) {
  const selectedCount = entries.filter(
    (video) => selectedVideos[video.url] && video.summary
  ).length;

  const selectedSummaries = entries.filter(
    (video) => selectedVideos[video.url] && video.summary
  );

  return (
    <div>
      {selectedCount > 0 && (
        <button className="copy-all" onClick={onCopy}>
          Copy {selectedCount} Selected Summaries
        </button>
      )}

      <div>
        {selectedCount > 0 ? (
          selectedSummaries.map((video, index) => (
            <article key={index}>
              <h2>
                <a href={video.url} target="_blank">
                  {video.name}
                </a>
              </h2>
              <ReactMarkdown>{video.summary}</ReactMarkdown>
            </article>
          ))
        ) : (
          <p className="placeholder-text">
            Select videos to view summaries.
          </p>
        )}
      </div>
    </div>
  );
}
