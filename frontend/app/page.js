"use client";

import { useState, useEffect } from "react";

export default function Home() {
  const [url, setUrl] = useState("");
  const [message, setMessage] = useState("");
  const [entries, setEntries] = useState([]);

  const SERVER = "http://127.0.0.1:3669";

  useEffect(() => {
    fetchEntries();
    const interval = setInterval(fetchEntries, 10_000);
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

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text).then(() => {
      setMessage("Transcript copied to clipboard.");
    });
  };

  return (
    <div id="container">
      <main>
        <h1>Youtube Transcriber</h1>
        <form onSubmit={handleSubmit}>
          <input
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="Enter YouTube URL"
            required
          />
          <button type="submit">Go</button>
        </form>
        {message && <p id="message">{message}</p>}

        <div className="video-list">
          <div className="video-header">
            <span>Name</span>
            <span>Status</span>
            <span></span>
          </div>
          {entries.map((video, index) => (
            <div className="video-row" key={index}>
              <span>
                <a href={video.url} target="_blank">
                  {video.name}
                </a>
              </span>
              <span>{video.status}</span>
              {video.transcription && (
                <button
                  className="copy-button"
                  onClick={() => copyToClipboard(video.transcription)}
                >
                  Copy Transcript
                </button>
              )}
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}
