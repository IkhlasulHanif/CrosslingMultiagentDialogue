# BiVaD Smoke Runner

`scripts/run_bivad_smoke.py` is an offline deterministic runner for the first executable slice of the BiVaD protocol. It does not call model APIs and must not be reported as empirical evidence.

It verifies the mechanics needed before model-backed trials:

- disagreement screening over private value vectors;
- mixed-language public dialogue with required-language tracking;
- separate private-probe and observer-readout layers;
- drift, convergence, and private-public gap metrics;
- JSON and Markdown artifacts under `runs/bivad-smoke/`.

Run the default English-Indonesian two-turn smoke trial:

```sh
python3 scripts/run_bivad_smoke.py
```

Run the no-dialogue control:

```sh
python3 scripts/run_bivad_smoke.py --condition no-dialogue --turns 0
```

The next implementation step is to replace the deterministic speaker, probe, and observer functions with API-backed calls while preserving the artifact schema.
