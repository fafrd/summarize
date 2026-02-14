import { useState, useEffect } from "react";
import { fetchEntries } from "@/utils/api";

const POLL_INTERVAL = parseInt(process.env.NEXT_PUBLIC_POLL_INTERVAL) || 1000;

export function useVideos() {
  const [entries, setEntries] = useState([]);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadEntries = async () => {
      try {
        const data = await fetchEntries();
        setEntries(data);
        setError(null);
      } catch (err) {
        setError(err.message);
      } finally {
        setIsLoading(false);
      }
    };

    loadEntries();
    const interval = setInterval(loadEntries, POLL_INTERVAL);
    return () => clearInterval(interval);
  }, []);

  return { entries, error, isLoading, refetch: () => fetchEntries().then(setEntries) };
}
