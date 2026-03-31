import sqlite3
from datetime import datetime
from zoneinfo import ZoneInfo  # Python 3.9+

# --- CONFIG ---
anki_db_path = r"C:\Users\Kopecky_J\AppData\Roaming\Anki2\User 1\collection.anki2"

# Time zone of your Anki reviews (replace with your actual zone)
local_tz = ZoneInfo("Europe/Berlin")  

# Date range options
# Option 1: last year
# start_date = datetime(datetime.now().year - 1, 1, 1, tzinfo=local_tz)
# end_date = datetime(datetime.now().year - 1, 12, 31, 23, 59, 59, tzinfo=local_tz)

# Option 2: specific year
# start_date = datetime(2023, 1, 1, tzinfo=local_tz)
# end_date = datetime(2023, 12, 31, 23, 59, 59, tzinfo=local_tz)

# Option 3: custom range, e.g., Jan 2024 to Mar 2024
start_date = datetime(2021, 1, 1, tzinfo=local_tz)
end_date = datetime(2027, 3, 31, 23, 59, 59, tzinfo=local_tz)
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

# Initialize hourly counts
hourly_counts = {f"{h:02}": 0 for h in range(24)}

for row in rows:
    ts = row["id"] / 1000  # convert milliseconds to seconds
    dt = datetime.fromtimestamp(ts, tz=local_tz)  # historical local time with DST
    hour = f"{dt.hour:02}"
    hourly_counts[hour] += 1

# Print results
print(f"Reviews from {start_date} to {end_date}")
print("Hour | Reviews")
for h in range(24):
    hour_str = f"{h:02}"
    print(f"{hour_str}   | {hourly_counts[hour_str]}")

conn.close()