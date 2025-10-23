import json, sys
hits = 0; total = 0
for line in open("logs/256bit_breakthrough_log.md"):
    try:
        r = json.loads(line); total += 1
        if r.get("status") == "factored": hits += 1
    except: pass
print(f"factored={hits} / total={total}  hit_rate={hits/(total or 1):.2%}")