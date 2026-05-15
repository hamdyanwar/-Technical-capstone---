import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), "medical_devices.db")
print(f"Opening DB at: {db_path}")

conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Show current devices
cur.execute("SELECT id, name, location FROM devices")
rows = cur.fetchall()
print("Current devices:")
for r in rows:
    print(f"  {r}")

# 1. Delete device with name containing 568
cur.execute("DELETE FROM devices WHERE name LIKE '%568%'")
print(f"\nDeleted {cur.rowcount} device(s) matching '568'")

# 2. Rename device with smallest id to 'menrey' and change room to 102
cur.execute("SELECT id FROM devices ORDER BY id ASC LIMIT 1")
first = cur.fetchone()
if first:
    cur.execute("UPDATE devices SET name='menrey', location='Room 102' WHERE id=?", (first[0],))
    print(f"Renamed device id={first[0]} to 'menrey', Room 102")

# 3. Change all remaining Room 101 devices to Room 102
cur.execute("UPDATE devices SET location='Room 102' WHERE location='Room 101'")
print(f"Updated {cur.rowcount} device(s) from Room 101 to Room 102")

conn.commit()

# Show updated devices
cur.execute("SELECT id, name, location FROM devices")
rows = cur.fetchall()
print("\nUpdated devices:")
for r in rows:
    print(f"  {r}")

conn.close()
print("\nDone!")
