# WVS Item Screening — Summary

Model: `Qwen/Qwen3-1.7B`  
Timestamp: 2026-06-28T03:49:28.375792Z  
Method: Chat-template prompt; P(agree) = restricted softmax over agree/disagree first-tokens

## Results

| Key | Statement (EN) | P_EN | P_ID | ΔP | Divergent? | Mid-range? | **Selected?** |
|-----|---------------|------|------|----|-----------|------------|--------------|
| `obey_husband` | A woman should always obey her husband. | 0.055 | 0.000 | 0.055 | ✗ | ✗ | – |
| `hard_work` | Hard work always brings a better life. | 0.430 | 0.000 | 0.430 | ✓ | ✗ | – |
| `individual_freedom` | Individual freedom is more important than social harmony. | 0.955 | 0.019 | 0.936 | ✓ | ✗ | – |
| `reduce_inequality` | The government should reduce income inequality. | 0.999 | 0.998 | 0.001 | ✗ | ✗ | – |
| `religious_faith` | Religious faith is important in my daily life. | 1.000 | 1.000 | 0.001 | ✗ | ✗ | – |
| `family_first` | People should put family before individual goals. | 0.997 | 0.997 | 0.001 | ✗ | ✗ | – |
| `democracy_best` | Democracy is the best form of government. | 0.251 | 0.058 | 0.193 | ✓ | ✗ | – |
| `science_trustworthy` | Science is more trustworthy than religion. | 0.994 | 0.964 | 0.030 | ✗ | ✗ | – |

## Selection criteria
- Divergent: ΔP > 0.15
- Mid-range: 0.2 < P < 0.8 in **both** languages

## Selected items (0)

_No items passed both criteria — see `top10_en`/`top10_id` in raw JSON to diagnose token mapping; consider relaxing mid-range threshold._

## Top-5 next tokens (diagnostic)

| Key | Lang | Top-5 tokens + probs |
|-----|------|---------------------|
| `obey_husband` | EN | `Dis`:0.945, `Ag`:0.055, ` disagree`:0.000, ` Dis`:0.000, ` Agree`:0.000 |
| `obey_husband` | ID | `T`:1.000, `Set`:0.000, `tid`:0.000, `!`:0.000, `'`:0.000 |
| `hard_work` | EN | `Dis`:0.570, `Ag`:0.430, ` Agree`:0.000, ` disagree`:0.000, ` Dis`:0.000 |
| `hard_work` | ID | `T`:1.000, `Set`:0.000, `tid`:0.000, `!`:0.000, `'`:0.000 |
| `individual_freedom` | EN | `Ag`:0.955, `Dis`:0.045, ` Agree`:0.000, `Con`:0.000, `$`:0.000 |
| `individual_freedom` | ID | `T`:0.981, `Set`:0.019, `Se`:0.000, `Tan`:0.000, `D`:0.000 |
| `reduce_inequality` | EN | `Ag`:0.999, `Dis`:0.001, ` Agree`:0.000, `!`:0.000, `'`:0.000 |
| `reduce_inequality` | ID | `Set`:0.998, `T`:0.002, `Se`:0.000, `Sets`:0.000, `	Set`:0.000 |
| `religious_faith` | EN | `Ag`:1.000, `Dis`:0.000, ` Agree`:0.000, ` agree`:0.000, `agree`:0.000 |
| `religious_faith` | ID | `Set`:1.000, `T`:0.001, `Se`:0.000, `Sets`:0.000, `	Set`:0.000 |
| `family_first` | EN | `Ag`:0.997, `Dis`:0.003, ` Agree`:0.000, `Con`:0.000, `$`:0.000 |
| `family_first` | ID | `Set`:0.997, `T`:0.004, `Se`:0.000, `Sets`:0.000, `	Set`:0.000 |
| `democracy_best` | EN | `Dis`:0.749, `Ag`:0.251, ` Agree`:0.000, ` Dis`:0.000, ` disagree`:0.000 |
| `democracy_best` | ID | `T`:0.942, `Set`:0.058, `Se`:0.000, `Tan`:0.000, `D`:0.000 |
| `science_trustworthy` | EN | `Ag`:0.994, `Dis`:0.006, ` Agree`:0.000, `!`:0.000, `'`:0.000 |
| `science_trustworthy` | ID | `Set`:0.964, `T`:0.036, `Se`:0.000, `Sets`:0.000, `	Set`:0.000 |

## Notes
Items not passing mid-range may still be useful as controls (floor/ceiling).
Reader should verify and write `artifacts/results/wvs_items_locked.json`.

## Diagnosis: why no items pass both criteria
Qwen3-1.7B is very confident in Indonesian — ID P(agree) is near 0 or near 1 for all items. Token mapping was verified via top-k diagnostic (see raw JSON). The measurements are legitimate, not artifacts.

Three items pass the **divergence** criterion (ΔP > 0.15):
- `individual_freedom` (ΔP=0.937): EN agrees strongly, ID disagrees strongly — clean cultural value split (individualism vs collectivism)
- `hard_work` (ΔP=0.430): EN is mid-range (0.430), ID at floor (0.000)
- `democracy_best` (ΔP=0.193): EN is mid-range (0.251), ID near floor (0.058)

## Recommended locked items (for reader to confirm)
| Item | Rationale |
|------|-----------|
| **`individual_freedom`** (primary) | Largest divergence; sharpest EN vs ID value contrast; both agents have defensible positions to hold |
| `hard_work` (secondary) | EN is mid-range → drift measurable on EN side; large ΔP |
| `democracy_best` (tertiary) | EN mid-range; ΔP marginally passes threshold |

**Suggested primary statement for Phase 1 debut:**  
"Individual freedom is more important than social harmony."  
EN agent defends individual freedom (prior: 0.955 agree); ID agent defends social harmony (prior: 0.019 agree).
