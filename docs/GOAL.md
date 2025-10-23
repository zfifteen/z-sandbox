oh yeah — time to send it. here’s the exact, no-nonsense launch sequence from repo root:

### 1) install and verify GMP-ECM (fast path)

```bash
# macOS / Apple Silicon
brew install gmp-ecm

# make sure your PATH has Homebrew’s bin (Apple Silicon):
echo 'export PATH="/opt/homebrew/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# verify the binary works
ecm -v
python3 - <<'PY'
from ecm_backend import backend_info
print(backend_info())  # should say {'backend': 'gmp-ecm', 'version': ...}
PY
```

### 2) quick smoke (single target, checkpoints + deterministic curves)

```bash
ECM_SIGMA=1 ECM_CKDIR=ckpts \
python3 python/scaling_test.py \
  --single $(jq -r '.targets[0].N' python/targets_filtered.json) \
  --timeout-per-stage 60 \
  --checkpoint-dir ckpts \
  --use-sigma

# sanity peek
head -3 logs/256bit_breakthrough_log.md
```

### 3) full parallel batch (100 targets, 4 workers, 20 min/stage)

```bash
J=4 TIMEOUT=1200 COUNT=100 ECM_CKDIR=ckpts ECM_SIGMA=0 \
./scripts/run_full_batch.sh
```

### 4) monitor like a hawk

```bash
# live tail
tail -f logs/256bit_breakthrough_log.md

# periodic summary
watch -n 30 'python3 scripts/summarize_256_log.py'
```

### 5) resume anytime

All tiers auto-checkpoint per target/B1. If you stop or crash, just rerun the same command — it resumes from the saved state.

---

If the summarizer shows zero hits at the end of the 100, bump `width_factor` to **0.226** and rerun the same batch. Otherwise… let’s go get that first crack. 🚀
