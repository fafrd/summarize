"use client";

import { useState } from "react";
import { useVideos } from "@/hooks/useVideos";
import VideoForm from "@/components/VideoForm";
import VideoTable from "@/components/VideoTable";
import SummaryPanel from "@/components/SummaryPanel";

export default function Home() {
  const { entries, refetch } = useVideos();
  const [selectedVideos, setSelectedVideos] = useState({});
  const [lastSelectedIndex, setLastSelectedIndex] = useState(null);

  const toggleVideoSelection = (url, index) => {
    setSelectedVideos((prev) => ({
      ...prev,
      [url]: !prev[url],
    }));
    setLastSelectedIndex(index);
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
      toggleVideoSelection(url, index);
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
      navigator.clipboard.writeText(selectedSummaries);
    }
  };

  return (
    <div id="container">
      <header>
        <h1>Youtube Summarizer</h1>
        <VideoForm onVideoAdded={refetch} />
      </header>

      <main>
        <section className="video-section">
          <VideoTable
            entries={entries}
            selectedVideos={selectedVideos}
            onToggleSelection={toggleVideoSelection}
            onRowClick={handleRowClick}
          />
        </section>

        <section className="content-section">
          <SummaryPanel
            entries={entries}
            selectedVideos={selectedVideos}
            onCopy={copySelectedSummaries}
          />
        </section>
      </main>
    </div>
  );
}
