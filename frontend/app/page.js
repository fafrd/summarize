"use client";

import { useState } from "react";

export default function Home() {
  const [url, setUrl] = useState("");
  const [message, setMessage] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage("");

    const response = await fetch("/api/add-video", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url }),
    });

    if (response.ok) {
      setMessage("Video added successfully.");
      setUrl("");
    } else {
      setMessage("Failed to add video.");
    }
  };

  const dummyData = [
    { name: "City Council Meeting 1", status: "done" },
    { name: "City Council Meeting 2", status: "transcribing" },
    { name: "City Council Meeting 3", status: "downloading" },
  ];

  return (
    <div id="container">
      <main>
        <h1>Summarize</h1>
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
        {message && <p>{message}</p>}

        <div className="video-list">
          <div className="video-header">
            <span>Name</span>
            <span>Status</span>
          </div>
          {dummyData.map((video, index) => (
            <div className="video-row" key={index}>
              <span>{video.name}</span>
              <span>{video.status}</span>
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}
