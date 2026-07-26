from __future__ import annotations

LANGUAGES = ("EN", "ID", "ZH", "ES", "AR", "HI", "SW", "JV")
H5_LANGUAGES = ("EN", "ID", "AR", "SW", "JV")
LETTERS = ("A", "B", "C", "D")
DIRECTIONS = ("misleading", "corrective")
PERSONAS = ("none", "congruent", "incongruent", "en_persona")
REASONING_MODES = ("native", "oracle")
MODELS_T = ("gpt-4o-mini", "gpt-4o")
MODEL_P_DEFAULT = "gpt-4o-mini"

APPEAL_ORDER = (
    "credibility",
    "logic_true",
    "logic_fabricated",
    "emotion",
    "social_proof",
    "authority",
)

ANCHOR_COUNTRY = {
    "EN": "USA",
    "ID": "Indonesia",
    "ZH": "China",
    "ES": "Spain",
    "AR": "Egypt",
    "HI": "India",
    "SW": "Kenya",
    "JV": "Indonesia/Java",
}

INCONGRUENT_COUNTRY = {
    "EN": "China",
    "ID": "USA",
    "ZH": "Spain",
    "ES": "Egypt",
    "AR": "India",
    "HI": "Kenya",
    "SW": "Indonesia",
    "JV": "USA",
}

LANGUAGE_NAMES = {
    "EN": "English",
    "ID": "Indonesian",
    "ZH": "Chinese",
    "ES": "Spanish",
    "AR": "Arabic",
    "HI": "Hindi",
    "SW": "Swahili",
    "JV": "Javanese",
}

PHASES = ("pilot", "core", "h5", "safety", "culture")
