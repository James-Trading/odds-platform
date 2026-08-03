from datetime import datetime

LOG_FILE = "logs/activity_log.txt"

def log_activity(category, message):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] {message}\n")