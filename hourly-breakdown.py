import sqlite3
from datetime import datetime
from zoneinfo import ZoneInfo  # Using tzdata installed
import matplotlib.pyplot as plt

# --- CONFIG ---
anki_db_path = r"C:\Users\Kopecky_J\AppData\Roaming\Anki2\User 1\collection.anki2"

# Your local timezone
local_tz = ZoneInfo("Europe/Berlin")

# Date range
start_date = datetime(2020, 11, 1, tzinfo=local_tz)
end_date = datetime(2026, 12, 31, 23, 59, 59, tzinfo=local_tz)
# --- END CONFIG ---

# Convert start/end dates to UTC timestamps (seconds)
start_ts = int(start_date.timestamp())
end_ts = int(end_date.timestamp())

# Connect to SQLite
conn = sqlite3.connect(anki_db_path)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# Query revlog using 'id' (real timestamp)
query = """
SELECT id
FROM revlog
WHERE id/1000 BETWEEN ? AND ?
"""
cur.execute(query, (start_ts, end_ts))
rows = cur.fetchall()
conn.close()

# Initialize hourly counts
hourly_counts = {f"{h:02}": 0 for h in range(24)}

# Count reviews per hour using historical local time
for row in rows:
    ts = row["id"] / 1000  # milliseconds → seconds
    dt = datetime.fromtimestamp(ts, tz=local_tz)
    hour = f"{dt.hour:02}"
    hourly_counts[hour] += 1

# --- Print hourly breakdown ---
print(f"Reviews from {start_date} to {end_date}")
print("Hour | Reviews")
for h in range(24):
    hour_str = f"{h:02}"
    print(f"{hour_str}   | {hourly_counts[hour_str]}")

# --- Plotting ---
hours = list(hourly_counts.keys())
counts = list(hourly_counts.values())

plt.figure(figsize=(12, 6))
plt.bar(hours, counts, color="skyblue")
plt.title(f"Anki Reviews by Hour ({start_date.date()} to {end_date.date()})", fontsize=14)
plt.xlabel("Hour of Day", fontsize=12)
plt.ylabel("Number of Reviews", fontsize=12)
plt.xticks(hours)  # show all hours
plt.grid(axis="y", linestyle="--", alpha=0.7)
plt.tight_layout()
plt.show()