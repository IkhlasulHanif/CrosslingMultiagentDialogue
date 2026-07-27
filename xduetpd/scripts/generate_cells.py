#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
LANGUAGES = ["EN", "ID", "ZH", "ES", "AR", "HI", "SW", "JV"]
H5_LANGUAGES = ["EN", "ID", "AR", "SW", "JV"]
DIRECTIONS = ["misleading", "corrective"]
PERSONAS = ["none", "congruent", "incongruent", "en_persona"]
REASONING = ["native", "oracle"]
MODEL_PRIMARY = "gpt-4o-mini"
MODEL_P_DEFAULT = "gpt-4o-mini"
CORE_DIALOGUES_PER_CELL = 1
H5_DIALOGUES_PER_CELL = 1
SAFETY_DIALOGUES_PER_CELL = 1
CULTURE_DIALOGUES_PER_CELL = 1

# Legacy suffixes are retained so existing manifests and STATE.yaml remain
# resumable after switching the actual API model.
PILOT_MODEL_SLOTS = [("4omini", MODEL_PRIMARY), ("4o", MODEL_PRIMARY)]


def main() -> int:
    out = ROOT / "configs" / "cells"
    out.mkdir(parents=True, exist_ok=True)
    cells = []
    cells.append(
        cell(
            cell_id="m0_smoke",
            phase="m0",
            target_lang="EN",
            persuader_lang="EN",
            direction="misleading",
            persona="none",
            reasoning="native",
            model_T=MODEL_PRIMARY,
            n_dialogues=1,
            stimulus_set="sample/s1_smoke",
            seeds=[101],
        )
    )
    for target_lang in ["EN", "ID", "SW"]:
        for direction in DIRECTIONS:
            for slot, model_t in PILOT_MODEL_SLOTS:
                cells.append(
                    cell(
                        cell_id=f"pilot_t{target_lang.lower()}_p{target_lang.lower()}_{direction}_{slot}",
                        phase="pilot",
                        target_lang=target_lang,
                        persuader_lang=target_lang,
                        direction=direction,
                        persona="none",
                        reasoning="native",
                        model_T=model_t,
                        n_dialogues=30,
                        stimulus_set="s1",
                    )
                )
    for target_lang in LANGUAGES:
        for persona in PERSONAS:
            for reasoning in REASONING:
                for direction in DIRECTIONS:
                    cells.append(
                        cell(
                            cell_id=f"core_t{target_lang.lower()}_pen_{persona}_{reasoning}_{direction}_4omini",
                            phase="core",
                            target_lang=target_lang,
                            persuader_lang="EN",
                            direction=direction,
                            persona=persona,
                            reasoning=reasoning,
                            model_T=MODEL_PRIMARY,
                            n_dialogues=CORE_DIALOGUES_PER_CELL,
                            stimulus_set="s1",
                        )
                    )
                    if target_lang == "EN":
                        cells.append(
                            cell(
                                cell_id=f"core_ten_pen_{persona}_{reasoning}_{direction}_4o",
                                phase="core",
                                target_lang="EN",
                                persuader_lang="EN",
                                direction=direction,
                                persona=persona,
                                reasoning=reasoning,
                                model_T=MODEL_PRIMARY,
                                n_dialogues=CORE_DIALOGUES_PER_CELL,
                                stimulus_set="s1",
                            )
                        )
    for target_lang in H5_LANGUAGES:
        for persuader_lang in H5_LANGUAGES:
            for direction in DIRECTIONS:
                cells.append(
                    cell(
                        cell_id=f"h5_t{target_lang.lower()}_p{persuader_lang.lower()}_{direction}_4omini",
                        phase="h5",
                        target_lang=target_lang,
                        persuader_lang=persuader_lang,
                        direction=direction,
                        persona="none",
                        reasoning="native",
                        model_T=MODEL_PRIMARY,
                        n_dialogues=H5_DIALOGUES_PER_CELL,
                        stimulus_set="s1",
                    )
                )
    for target_lang in LANGUAGES:
        cells.append(
            cell(
                cell_id=f"safety_t{target_lang.lower()}_pen_misleading_4omini",
                phase="safety",
                target_lang=target_lang,
                persuader_lang="EN",
                direction="misleading",
                persona="none",
                reasoning="native",
                model_T=MODEL_PRIMARY,
                n_dialogues=SAFETY_DIALOGUES_PER_CELL,
                stimulus_set="s2",
            )
        )
    for target_lang in LANGUAGES:
        for persona in ["none", "congruent"]:
            cells.append(
                cell(
                    cell_id=f"culture_t{target_lang.lower()}_{persona}_4omini",
                    phase="culture",
                    target_lang=target_lang,
                    persuader_lang="EN",
                    direction="corrective",
                    persona=persona,
                    reasoning="native",
                    model_T=MODEL_PRIMARY,
                    n_dialogues=CULTURE_DIALOGUES_PER_CELL,
                    stimulus_set="s3",
                    probe_only=True,
                )
            )
    for item in cells:
        (out / f"{item['cell_id']}.yaml").write_text(
            yaml.safe_dump(item, sort_keys=False), encoding="utf-8"
        )
    index = {
        "total_cells": len(cells),
        "by_phase": {phase: sum(1 for item in cells if item["phase"] == phase) for phase in sorted({c["phase"] for c in cells})},
        "cells": [item["cell_id"] for item in cells],
    }
    (ROOT / "configs" / "cells_index.json").write_text(
        json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    evidence = ROOT / "reports" / "evidence" / "M2.1" / "cells_report.md"
    evidence.parent.mkdir(parents=True, exist_ok=True)
    evidence.write_text(
        "# Cells Report\n\n"
        f"- total cells: {index['total_cells']}\n"
        + "\n".join(f"- {phase}: {count}" for phase, count in sorted(index["by_phase"].items()))
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps(index, sort_keys=True))
    return 0


def cell(**kwargs):
    data = {
        "cell_id": kwargs["cell_id"],
        "phase": kwargs["phase"],
        "target_lang": kwargs["target_lang"],
        "persuader_lang": kwargs["persuader_lang"],
        "direction": kwargs["direction"],
        "persona": kwargs["persona"],
        "reasoning": kwargs["reasoning"],
        "model_T": kwargs["model_T"],
        "model_P": kwargs.get("model_P", MODEL_P_DEFAULT),
        "n_dialogues": kwargs["n_dialogues"],
        "stimulus_set": kwargs["stimulus_set"],
        "seeds": kwargs.get("seeds", [1001, 2001, 3001, 4001, 5001]),
        "temperature_dialogue": 0.7,
        "probe_k": 8,
    }
    if kwargs.get("probe_only"):
        data["probe_only"] = True
    return data


def model_slug(model: str) -> str:
    return model.replace("gpt-", "").replace("-", "")


if __name__ == "__main__":
    raise SystemExit(main())
