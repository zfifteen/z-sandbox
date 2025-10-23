import json
from pathlib import Path

def load_256bit_targets(count: int):
    """
    Load up to 'count' targets from targets_filtered.json
    """
    ts = Path("python/targets_filtered.json")
    data = json.loads(ts.read_text())
    targets = [int(x['N']) for x in data["targets"][:count]]
    return targets