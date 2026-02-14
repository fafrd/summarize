const SERVER = process.env.NEXT_PUBLIC_SERVER_URL;

if (!SERVER) {
  console.warn("NEXT_PUBLIC_SERVER_URL not set, API calls will fail");
}

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
