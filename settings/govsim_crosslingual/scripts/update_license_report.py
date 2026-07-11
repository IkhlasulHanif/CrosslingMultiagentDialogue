#!/usr/bin/env python3
"""Synchronize the GovSim source/license evidence report."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "code"))

from source_license_check import check_source_license  # noqa: E402


DEFAULT_JSON_OUT = Path("artifacts/logs/source_license_status.json")
DEFAULT_MARKDOWN_OUT = Path("licenses.md")


def _display_path(root: Path, value: str | None) -> str:
    if not value:
        return "absent"
    path = Path(value)
    try:
        return f"`{path.resolve().relative_to(root.resolve())}`"
    except ValueError:
        return f"`{value}`"


def _display_list(root: Path, values: list[str]) -> str:
    if not values:
        return "- absent"
    return "\n".join(f"- {_display_path(root, value)}" for value in values)


def _display_metadata_table(root: Path, values: list[dict[str, object]]) -> str:
    if not values:
        return "No local file fingerprints are available."

    rows = ["| Path | Bytes | SHA-256 |", "|---|---:|---|"]
    for item in values:
        path = item.get("path") if isinstance(item, dict) else None
        byte_count = item.get("bytes") if isinstance(item, dict) else None
        sha256 = item.get("sha256") if isinstance(item, dict) else None
        rows.append(
            f"| {_display_path(root, path if isinstance(path, str) else None)} "
            f"| `{byte_count if isinstance(byte_count, int) else 'absent'}` "
            f"| `{sha256 if isinstance(sha256, str) else 'absent'}` |"
        )
    return "\n".join(rows)


def _display_value(value: object) -> str:
    if value is None:
        return "absent"
    return f"`{value}`"


def render_license_markdown(root: Path) -> str:
    result = check_source_license(root)
    data = result.as_dict()

    missing = result.missing or ["none"]
    warnings = result.warnings or ["none"]
    status_line = (
        "local source/license evidence recorded"
        if result.status == "READY_FOR_REVIEW"
        else "blocked pending GovSim source/license material"
    )
    determination = (
        "Local GovSim source/license evidence is present. The vendored license "
        "file identifies the upstream license as MIT, and the configured fishery "
        "prompt/rule files have stable local fingerprints. This records the "
        "benchmark evidence gate; it is not legal advice."
        if result.status == "READY_FOR_REVIEW"
        else "The GovSim license is not verified from local evidence. Do not "
        "vendor, run, or adapt GovSim code for this setting until the upstream "
        "repository or license text is added under this setting and reviewed."
    )

    return f"""# GovSim License Verification

Status: {status_line}.

## Current Determination

{determination}

## Local Evidence

| Field | Value |
|---|---|
| Checker schema | `{data["schema_version"]}` |
| Checker status | `{result.status}` |
| Manifest | {_display_path(root, data["manifest_path"])} |
| Upstream URL | {_display_value(result.upstream_url)} |
| Upstream license URL | {_display_value(result.upstream_license_url)} |
| Upstream license SPDX | {_display_value(result.upstream_license_spdx_id)} |
| Paper URL | {_display_value(result.paper_url)} |
| Source path | {_display_path(root, result.source_path)} |
| Substrate | {_display_value(result.substrate)} |
| Fishery allowed by human review | {_display_value(result.fishery_substrate_allowed)} |

## Upstream Evidence Note

{result.upstream_evidence_note or "No upstream provenance note is recorded in the manifest."}

## License Files

{_display_list(root, result.license_files)}

## Source Prompt / Rule Files

{_display_list(root, result.source_prompt_files)}

## License File Fingerprints

{_display_metadata_table(root, result.license_file_metadata)}

## Source Prompt / Rule File Fingerprints

{_display_metadata_table(root, result.source_prompt_file_metadata)}

## Missing Evidence

{chr(10).join(f"- {item}" for item in missing)}

## Warnings

{chr(10).join(f"- {item}" for item in warnings)}

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

This writes `{DEFAULT_JSON_OUT}` and refreshes this file from local evidence.
The checker returns `BLOCKED` until `config/govsim_source.json` exists, points to
a GovSim source checkout inside this setting, finds a non-empty license file
under that checkout, finds non-empty files listed in `source_prompt_files`,
sets `substrate` to `fishery`, uses a non-placeholder authoritative
`upstream_url`, and records human confirmation that `fishery_substrate_allowed`
is `true`.

Use `config/govsim_source.example.json` as the template. The checker only makes
the evidence gate repeatable; it does not replace human license review.
"""


def sync_report(root: Path, json_out: Path, markdown_out: Path) -> str:
    root = root.resolve()
    result = check_source_license(root)
    data = result.as_dict()

    json_path = root / json_out
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    markdown_path = root / markdown_out
    markdown_path.write_text(render_license_markdown(root), encoding="utf-8")
    return result.status


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="Setting root to inspect.")
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON_OUT, help="JSON output path relative to root.")
    parser.add_argument("--markdown-out", type=Path, default=DEFAULT_MARKDOWN_OUT, help="Markdown output path relative to root.")
    parser.add_argument("--strict", action="store_true", help="Return nonzero when the checker is still blocked.")
    args = parser.parse_args()

    status = sync_report(args.root, args.json_out, args.markdown_out)
    print(status)
    return 0 if status == "READY_FOR_REVIEW" or not args.strict else 2


if __name__ == "__main__":
    raise SystemExit(main())
