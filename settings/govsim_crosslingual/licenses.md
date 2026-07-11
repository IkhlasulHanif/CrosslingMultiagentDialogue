# GovSim License Verification

Status: local source/license evidence recorded.

## Current Determination

Local GovSim source/license evidence is present. The vendored license file identifies the upstream license as MIT, and the configured fishery prompt/rule files have stable local fingerprints. This records the benchmark evidence gate; it is not legal advice.

## Local Evidence

| Field | Value |
|---|---|
| Checker schema | `govsim-source-license-check-v2` |
| Checker status | `READY_FOR_REVIEW` |
| Manifest | `config/govsim_source.json` |
| Upstream URL | `https://github.com/giorgio-piatti/GovSim` |
| Upstream license URL | `https://github.com/giorgio-piatti/GovSim/blob/main/LICENSE` |
| Upstream license SPDX | `MIT` |
| Paper URL | `https://arxiv.org/abs/2404.16698` |
| Source path | `vendor/govsim` |
| Substrate | `fishery` |
| Fishery allowed by human review | `True` |

## Upstream Evidence Note

The NeurIPS 2024 GovSim paper links the code to github.com/giorgiopiatti/GovSim, which redirects to github.com/giorgio-piatti/GovSim. The GitHub repository page reports an MIT license. The user's binding benchmark goals specify the fishery substrate only for now; local evidence uses subskills/fishing prompt/rule/config files from the cloned repository.

## License Files

- `vendor/govsim/LICENSE`

## Source Prompt / Rule Files

- `vendor/govsim/subskills/fishing/utils.py`
- `vendor/govsim/subskills/fishing/reasoning_free_format.py`
- `vendor/govsim/subskills/fishing/conf/config.yaml`

## License File Fingerprints

| Path | Bytes | SHA-256 |
|---|---:|---|
| `vendor/govsim/LICENSE` | `1071` | `55be1b08220f411edf83dbf7ac9b3b3e7e56b92fb2ef9b10af91526edd38f15e` |

## Source Prompt / Rule File Fingerprints

| Path | Bytes | SHA-256 |
|---|---:|---|
| `vendor/govsim/subskills/fishing/utils.py` | `9179` | `c58bab1597cc45d2c26e69aacb0a0243fd63f79968641b0c6ef1c66c14597ffa` |
| `vendor/govsim/subskills/fishing/reasoning_free_format.py` | `14280` | `33fe16b14fe8831210969085a0610778f0d0898bdb1c5c7ed1e9dd1a9153ee5b` |
| `vendor/govsim/subskills/fishing/conf/config.yaml` | `383` | `35fc53198fd707465ec3a84a1c0b56d960819531d4e23a6b9c4fd6bcf4eeb1a7` |

## Missing Evidence

- none

## Warnings

- none

## Required Next Evidence

- Upstream GovSim repository URL or local source checkout.
- Exact license file text and any citation / usage restrictions.
- Non-empty fishery rule, instruction, and resource-description source files.
- Confirmation that the fishery substrate may be used for this benchmark.
- Stable byte counts and SHA-256 hashes for those local evidence files.

## Repeatable Check

Run:

```bash
python3 scripts/update_license_report.py --root .
```

This writes `artifacts/logs/source_license_status.json` and refreshes this file from local evidence.
The checker returns `BLOCKED` until `config/govsim_source.json` exists, points to
a GovSim source checkout inside this setting, finds a non-empty license file
under that checkout, finds non-empty files listed in `source_prompt_files`,
sets `substrate` to `fishery`, uses a non-placeholder authoritative
`upstream_url`, and records human confirmation that `fishery_substrate_allowed`
is `true`.

Use `config/govsim_source.example.json` as the template. The checker only makes
the evidence gate repeatable; it does not replace human license review.
