"use client";

import { useState } from "react";
import { addVideo } from "@/utils/api";

export default function VideoForm({ onVideoAdded }) {
  const [url, setUrl] = useState("");
  const [message, setMessage] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage("");

    try {
      await addVideo(url);
      setMessage("Video added successfully.");
      setUrl("");
      if (onVideoAdded) {
        onVideoAdded();
      }
    } catch (error) {
      setMessage(error.message || "Failed to add video.");
    }
  };

  return (
    <div>
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
    </div>
  );
}
