import sqlite3
from datetime import datetime
from zoneinfo import ZoneInfo  # Using tzdata installed
import matplotlib.pyplot as plt
from collections import Counter

# --- CONFIG ---
anki_db_path = r"C:\Users\Kopecky_J\AppData\Roaming\Anki2\User 1\collection.anki2"

# Your local timezone
local_tz = ZoneInfo("Europe/Berlin")

# Date range
start_date = datetime(2020, 11, 1, tzinfo=local_tz)
end_date = datetime(2026, 12, 31, 23, 59, 59, tzinfo=local_tz)

# Number of top days to display (change this value as needed)
top_n_days = 40
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

# Initialize daily counts
daily_counts = Counter()

# Count reviews per day using historical local time
for row in rows:
    ts = row["id"] / 1000  # milliseconds → seconds
    dt = datetime.fromtimestamp(ts, tz=local_tz)
    day = dt.date()  # Extract just the date (year-month-day)
    daily_counts[day] += 1

# --- Get the top N days with the most reviews ---
top_days = daily_counts.most_common(top_n_days)

# --- Print top N days ---
print(f"Top {top_n_days} Days with Most Reviews ({start_date.date()} to {end_date.date()})")
print("Date         | Reviews")
for day, count in top_days:
    print(f"{day} | {count}")

# --- Plotting ---
days = [str(day) for day, count in top_days]
counts = [count for day, count in top_days]

plt.figure(figsize=(12, 6))
plt.bar(days, counts, color="lightgreen")
plt.title(f"Top {top_n_days} Days with Most Anki Reviews ({start_date.date()} to {end_date.date()})", fontsize=14)
plt.xlabel("Date", fontsize=12)
plt.ylabel("Number of Reviews", fontsize=12)
plt.xticks(rotation=45, ha="right")  # Rotate the dates for better readability
plt.grid(axis="y", linestyle="--", alpha=0.7)
plt.tight_layout()
plt.show()