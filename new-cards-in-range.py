import sqlite3
from collections import defaultdict
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# --- CONFIG ---
anki_db_path = r"C:\Users\Kopecky_J\AppData\Roaming\Anki2\User 1\collection.anki2"

local_tz = ZoneInfo("Europe/Berlin")

start_date = datetime(2025, 9, 1, tzinfo=local_tz)
end_date = datetime(2026, 12, 31, 23, 59, 59, tzinfo=local_tz)
# --- END CONFIG ---

# Get actual date range from database to clip bounds
conn = sqlite3.connect(anki_db_path)
cur = conn.cursor()
cur.execute("SELECT MIN(id), MAX(id) FROM revlog")
min_id, max_id = cur.fetchone()
conn.close()

first_ts = min_id // 1000
last_ts = max_id // 1000

first_review_date = datetime.fromtimestamp(first_ts, tz=local_tz).date()
last_review_date = datetime.fromtimestamp(last_ts, tz=local_tz).date()
today = datetime.now(tz=local_tz).date()

start_date = datetime.combine(max(start_date.date(), first_review_date), datetime.min.time(), tzinfo=local_tz)
end_date = datetime.combine(min(end_date.date(), min(last_review_date, today)), datetime.max.time(), tzinfo=local_tz)

start_ts = int(start_date.timestamp())
end_ts = int(end_date.timestamp())

conn = sqlite3.connect(anki_db_path)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

query = """
SELECT id, cid, ease
FROM revlog
WHERE id/1000 BETWEEN ? AND ?
AND type = 0
"""
cur.execute(query, (start_ts, end_ts))
rows = cur.fetchall()
conn.close()

card_steps = defaultdict(list)
for row in rows:
    cid = row["cid"]
    ts = row["id"]
    ease = row["ease"]
    dt = datetime.fromtimestamp(ts / 1000, tz=local_tz)
    date_key = (cid, dt.date())
    card_steps[date_key].append(ease)

total = 0
for (cid, date), eases in card_steps.items():
    count_3 = eases.count(3)
    has_4 = 4 in eases
    if count_3 >= 2 or has_4:
        total += 1

range_days = (end_date.date() - start_date.date()).days + 1

avg_per_day = total / range_days if range_days > 0 else 0

print("New Cards Statistics")
print(f"Range: {start_date.date()} to {end_date.date()} ({range_days} days)")
print(f"Sum: {total}")
print(f"Average per day: {avg_per_day:.1f}")

if range_days < 7:
    print(f"Average per week: {avg_per_day * 7:.1f} (extrapolated)")
    print(f"Average per month: {avg_per_day * 30.44:.1f} (extrapolated)")
elif range_days < 30:
    avg_per_week = total / (range_days / 7)
    print(f"Average per week: {avg_per_week:.1f}")
    print(f"Average per month: {avg_per_day * 30.44:.1f} (extrapolated)")
else:
    avg_per_week = total / (range_days / 7)
    avg_per_month = total / (range_days / 30.44)
    print(f"Average per week: {avg_per_week:.1f}")
    print(f"Average per month: {avg_per_month:.1f}")