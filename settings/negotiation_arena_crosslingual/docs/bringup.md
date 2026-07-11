# NegotiationArena Bring-Up

This setting does not clone or vendor upstream code automatically. To unblock
local bring-up, provide an existing NegotiationArena checkout by one of these
paths:

- `external/NegotiationArena`
- `vendor/NegotiationArena`
- `third_party/NegotiationArena`
- `NEGOTIATION_ARENA_REPO=/absolute/path/to/NegotiationArena`

Then run:

```bash
python3 scripts/bringup_check.py --write-event
```

The bring-up gate requires evidence on disk before `goals.md` can mark
`Bring up NegotiationArena locally` complete:

- `artifacts/results/bringup_check.json` has `status: "OK"`.
- The selected checkout has README and license metadata.
- The checkout exposes Python package metadata through `requirements.txt`,
  `pyproject.toml`, or `setup.py`.
- The checkout contains obvious Python implementation candidates for both
  selected games: `resource_exchange` and `buy_sell`.

This gate is only a local checkout readiness check. It is not benchmark data and
does not create smoke-test transcripts or result metrics.
