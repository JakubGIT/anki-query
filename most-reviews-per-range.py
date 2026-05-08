import sqlite3
from datetime import datetime, timedelta
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

# Grouping: "day", "week", or "month"
grouping = "month"

# Number of top periods to display (change this value as needed)
top_n_periods = 40
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

# Initialize period counts
period_counts = Counter()

def get_period_key(dt, grouping_type):
    """Get the period key based on grouping type."""
    if grouping_type == "day":
        return dt.date()
    elif grouping_type == "week":
        # Return the Monday of the week
        return (dt.date() - timedelta(days=dt.weekday()))
    elif grouping_type == "month":
        # Return the first day of the month
        return dt.date().replace(day=1)
    else:
        raise ValueError(f"Unknown grouping type: {grouping_type}")

# Count reviews per period using historical local time
for row in rows:
    ts = row["id"] / 1000  # milliseconds → seconds
    dt = datetime.fromtimestamp(ts, tz=local_tz)
    period = get_period_key(dt, grouping)
    period_counts[period] += 1

# --- Get the top N periods with the most reviews ---
top_periods = period_counts.most_common(top_n_periods)

# --- Print top N periods ---
grouping_label = {"day": "Days", "week": "Weeks", "month": "Months"}[grouping]
print(f"Top {top_n_periods} {grouping_label} with Most Reviews ({start_date.date()} to {end_date.date()})")
print("Period       | Reviews")
for period, count in top_periods:
    print(f"{period} | {count}")

# --- Plotting ---
periods = [str(period) for period, count in top_periods]
counts = [count for period, count in top_periods]

plt.figure(figsize=(12, 6))
plt.bar(periods, counts, color="lightgreen")
plt.title(f"Top {top_n_periods} {grouping_label} with Most Anki Reviews ({start_date.date()} to {end_date.date()})", fontsize=14)
plt.xlabel(grouping_label.rstrip('s'), fontsize=12)
plt.ylabel("Number of Reviews", fontsize=12)
plt.xticks(rotation=45, ha="right")  # Rotate the periods for better readability
plt.grid(axis="y", linestyle="--", alpha=0.7)
plt.tight_layout()
plt.show()