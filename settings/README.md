# Simulation Settings

Each folder here should be self-contained: local harness or runner, setting
specific agents/prompts, configs, code, notes, artifacts, and writeups.

Keep only shared credentials and local process logs at the workspace root.

## Active Settings

- `crosslingual_debate/` - original WVS/debate-loop setting.
- `negotiation_arena_crosslingual/` - B5 mixed-motive negotiation.
- `cw_por_crosslingual/` - B6 adversarial persuasion.
- `camel_crosslingual/` - B2 cooperative dyadic tasks.
- `spygame_crosslingual/` - B4 hidden-role group game.
- `govsim_crosslingual/` - B1 cooperative resource management.
- `sotopia_crosslingual/` - B3 cooperative social scenarios.
- `_benchmark_common/` - shared helper and protocol for benchmark settings.
- `_template/` - minimal scaffold for a new setting.

Benchmark read-first index: `settings/benchmark_status.md`.

Benchmark settings support:

```bash
./harness.sh status
./harness.sh check
./harness.sh once
./harness.sh loop --sleep 900
./harness.sh error "quota or token issue"
./harness.sh note "open question or decision"
```
