"use client";

import { useState, useEffect } from "react";
import ReactMarkdown from "react-markdown";

export default function Home() {
  const [url, setUrl] = useState("");
  const [message, setMessage] = useState("");
  const [entries, setEntries] = useState([]);
  const [selectedVideos, setSelectedVideos] = useState({});
  const [lastSelectedIndex, setLastSelectedIndex] = useState(null);

  const SERVER = process.env.NEXT_PUBLIC_SERVER_URL;

  useEffect(() => {
    fetchEntries();
    const interval = setInterval(fetchEntries, 1_000);
    return () => clearInterval(interval);
  }, []);

  const fetchEntries = async () => {
    const response = await fetch(SERVER + "/entries");
    if (response.ok) {
      const data = await response.json();
      setEntries(data);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage("");

    const response = await fetch(SERVER + "/entries", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        url: url,
      }),
    });

    const data = await response.json();

    if (response.ok) {
      setMessage("Video added successfully.");
      setUrl("");
      fetchEntries(); // Refresh the list after adding
    } else {
      setMessage(data.error || "Failed to add video.");
    }
  };

  const toggleVideoSelection = (url) => {
    setSelectedVideos((prev) => ({
      ...prev,
      [url]: !prev[url],
    }));
  };

  const handleRowClick = (index, url, event) => {
    if (!entries[index].summary) return;

    if (event.shiftKey && lastSelectedIndex !== null) {
      // Determine range (start and end indices)
      const start = Math.min(lastSelectedIndex, index);
      const end = Math.max(lastSelectedIndex, index);

      // Create new selection state
      const newSelections = { ...selectedVideos };

      // Set all items in range to true (selected)
      for (let i = start; i <= end; i++) {
        if (entries[i].summary) {
          newSelections[entries[i].url] = true;
        }
      }

      setSelectedVideos(newSelections);
    } else {
      // Normal toggle for single item
      toggleVideoSelection(url);
      setLastSelectedIndex(index);
    }
  };

  const copySelectedSummaries = () => {
    const selectedSummaries = entries
      .filter((video) => selectedVideos[video.url] && video.summary)
      .map((video) => {
        return `## ${video.name}\n\n${video.summary}\n\n---\n\n`;
      })
      .join("");

    if (selectedSummaries) {
      navigator.clipboard.writeText(selectedSummaries).then(() => {
        setMessage("All selected summaries copied to clipboard.");
      });
    } else {
      setMessage("No summaries selected to copy.");
    }
  };

  const selectedCount = entries.filter(
    (video) => selectedVideos[video.url] && video.summary
  ).length;

  return (
    <div id="container">
      <header>
        <h1>Youtube Summarizer</h1>
        <form onSubmit={handleSubmit}>
          <input
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="Enter YouTube URL"
            required
          />
          <button type="submit">Submit</button>
        </form>
        {message && <p id="message">{message}</p>}
      </header>

      <main>
        <section className="video-section">
          <div className="video-list">
            <div className="video-header">
              <span>Name</span>
              <span>Status</span>
            </div>
            {entries.map((video, index) => (
              <div
                className={`video-row ${
                  !video.summary ? "video-row-disabled" : ""
                }`}
                key={index}
                onClick={(e) => handleRowClick(index, video.url, e)}
              >
                <span className="video-name">
                  <input
                    className="checkbox"
                    type="checkbox"
                    checked={selectedVideos[video.url] || false}
                    onChange={(e) => {
                      e.stopPropagation();
                      toggleVideoSelection(video.url);
                      setLastSelectedIndex(index);
                    }}
                    disabled={!video.summary}
                  />
                  {video.name}
                </span>
                <span>{video.status}</span>
              </div>
            ))}
          </div>
        </section>

        <section className="content-section">
          {selectedCount > 0 && (
            <button className="copy-all" onClick={copySelectedSummaries}>
              Copy {selectedCount} Selected Summaries
            </button>
          )}

          <div>
            {selectedCount > 0 ? (
              entries
                .filter((video) => selectedVideos[video.url] && video.summary)
                .map((video, index) => (
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
        </section>
      </main>
    </div>
  );
}
