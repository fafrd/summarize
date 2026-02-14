"use client";

import { useState } from "react";

export default function VideoTable({ entries, selectedVideos, onToggleSelection, onRowClick }) {
  const [sortField, setSortField] = useState("insertion_date");
  const [sortDirection, setSortDirection] = useState("desc");
  const [searchTerm, setSearchTerm] = useState("");

  const handleSort = (field) => {
    const newDirection = sortField === field && sortDirection === "asc" ? "desc" : "asc";
    setSortField(field);
    setSortDirection(newDirection);
  };

  const filteredEntries = entries.filter(video =>
    video.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    video.status.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const sortedEntries = [...filteredEntries].sort((a, b) => {
    let aVal = a[sortField];
    let bVal = b[sortField];

    if (sortField === "insertion_date") {
      aVal = new Date(aVal);
      bVal = new Date(bVal);
    }

    if (sortDirection === "asc") {
      return aVal < bVal ? -1 : aVal > bVal ? 1 : 0;
    } else {
      return aVal > bVal ? -1 : aVal < bVal ? 1 : 0;
    }
  });

  return (
    <div>
      <input
        type="text"
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        placeholder="Search videos..."
        style={{
          width: "100%",
          padding: "8px",
          marginBottom: "16px",
          border: "1px solid #ccc",
          borderRadius: "4px"
        }}
      />
      <div className="video-list">
        <div className="video-header">
          <span
            onClick={() => handleSort("name")}
            style={{ cursor: "pointer" }}
          >
            Name {sortField === "name" ? (sortDirection === "asc" ? "↑" : "↓") : ""}
          </span>
          <span
            onClick={() => handleSort("status")}
            style={{ cursor: "pointer" }}
          >
            Status {sortField === "status" ? (sortDirection === "asc" ? "↑" : "↓") : ""}
          </span>
          <span
            onClick={() => handleSort("insertion_date")}
            style={{ cursor: "pointer" }}
          >
            Added At {sortField === "insertion_date" ? (sortDirection === "asc" ? "↑" : "↓") : ""}
          </span>
        </div>
        {sortedEntries.map((video, index) => (
          <div
            className={`video-row ${
              !video.summary ? "video-row-disabled" : ""
            }`}
            key={index}
            onClick={(e) => onRowClick(index, video.url, e)}
          >
            <span className="video-name">
              <input
                className="checkbox"
                type="checkbox"
                checked={selectedVideos[video.url] || false}
                onChange={(e) => {
                  e.stopPropagation();
                  onToggleSelection(video.url, index);
                }}
                disabled={!video.summary}
              />
              {video.name}
            </span>
            <span>{video.status}</span>
            <span>{new Date(video.insertion_date).toLocaleDateString()}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
