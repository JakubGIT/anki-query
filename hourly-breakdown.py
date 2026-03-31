import sqlite3
from datetime import datetime

# --- CONFIG ---
anki_db_path = r"C:\Users\Kopecky_J\AppData\Roaming\Anki2\User 1\collection.anki2"
# --- END CONFIG ---

# Connect to SQLite
conn = sqlite3.connect(anki_db_path)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# Query revlog using 'id' as timestamp
cur.execute("SELECT id FROM revlog")
rows = cur.fetchall()

# Create empty dict for all hours
hourly_counts = {f"{h:02}": 0 for h in range(24)}

for row in rows:
    timestamp = row["id"] / 1000  # Convert milliseconds to seconds
    dt = datetime.fromtimestamp(timestamp)  # local time
    hour = dt.strftime("%H")
    hourly_counts[hour] += 1

# Print hourly breakdown
print("Hour | Reviews")
for h in range(24):
    hour_str = f"{h:02}"
    print(f"{hour_str}   | {hourly_counts[hour_str]}")

conn.close()