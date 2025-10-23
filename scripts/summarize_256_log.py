import json, sys, collections
from pathlib import Path

log = Path("logs/256bit_breakthrough_log.md")
if not log.exists():
    print("No log file found.", file=sys.stderr)
    sys.exit(1)

meta = None
hits = 0
total = 0
theta_counts = collections.Counter()
for line in open(log):
    try:
        r = json.loads(line)
    except Exception:
        continue
    if r.get("meta") == "RUN":
        meta = r
        continue
    total += 1
    if r.get("status") == "factored":
        hits += 1
    tg = r.get("theta_gate")
    if tg is not None:
        theta_counts[str(bool(tg))] += 1

print(f"factored={hits} / total={total}  hit_rate={hits/(total or 1):.2%}")
if meta:
    print(f"backend={meta.get('backend')} version={meta.get('version')} B1s={meta.get('schedule_B1')}")
if theta_counts:
    print("theta_gate counts:", dict(theta_counts))
