// Use the backend port from env, default to 3669
const BACKEND_PORT = process.env.NEXT_PUBLIC_BACKEND_PORT || '3669';

// Dynamically construct the server URL based on current browser location
// This allows the app to work on localhost, LAN IPs, domains, etc.
const getServerUrl = () => {
  if (typeof window !== 'undefined') {
    // In the browser: use current hostname with backend port
    return `${window.location.protocol}//${window.location.hostname}:${BACKEND_PORT}`;
  }
  // During SSR: fallback to env variable or localhost
  return process.env.NEXT_PUBLIC_SERVER_URL || `http://localhost:${BACKEND_PORT}`;
};

const SERVER = getServerUrl();

export async function fetchEntries() {
  const response = await fetch(`${SERVER}/entries`);
  if (!response.ok) {
    throw new Error(`Failed to fetch entries: ${response.status}`);
  }
  return response.json();
}

export async function addVideo(url) {
  const response = await fetch(`${SERVER}/entries`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url }),
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || "Failed to add video");
  }
  return data;
}
