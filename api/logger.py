from datetime import datetime, timezone

def log(message):
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%Sz")
    print(f"[{timestamp}] {message}")
