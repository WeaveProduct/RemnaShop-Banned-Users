import csv, json, sys

with open("telegram_ids.csv", encoding="utf-8") as f:
    rows = [r["telegram_id"] for r in csv.DictReader(f)]

errors = []
if not rows:
    errors.append("empty list")
if any(not r.isdigit() for r in rows):
    errors.append("non-numeric entries")
if len(set(rows)) != len(rows):
    errors.append(f"duplicates: {len(rows) - len(set(rows))}")
if rows != sorted(rows, key=int):
    errors.append("not sorted ascending")
if any(len(r) < 6 or len(r) > 11 for r in rows):
    errors.append("id length out of 6..11 range")

with open("telegram_ids.txt", encoding="utf-8") as f:
    txt = [line.split("#", 1)[0].strip() for line in f if line.strip()]
if rows != txt:
    errors.append("telegram_ids.txt out of sync")

with open("banned_users.csv", encoding="utf-8-sig") as f:
    detailed = list(csv.DictReader(f))
if [r["telegram_id"] for r in detailed] != rows:
    errors.append("banned_users.csv out of sync")

payload = json.load(open("data/banned_users.json", encoding="utf-8"))
if len(payload["users"]) != len(rows):
    errors.append("json out of sync")
if any(not r["category"] for r in detailed):
    errors.append("empty category")

print(f"checked {len(rows)} ids, {len(payload['users'])} json records")
if errors:
    sys.exit("FAILED: " + "; ".join(errors))
print("OK")
