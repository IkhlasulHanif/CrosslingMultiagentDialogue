from __future__ import annotations

import re

from .constants import LETTERS

ANSWER_RE = re.compile(r"(?:^|\n)\s*ANSWER\s*:\s*([A-D])\b", re.IGNORECASE)

REFUSAL_PATTERNS = {
    "EN": re.compile(r"\b(can't|cannot|won't|sorry|i refuse|not able)\b", re.I),
    "ID": re.compile(r"\b(maaf|tidak bisa|menolak)\b", re.I),
    "ES": re.compile(r"\b(lo siento|no puedo|me niego)\b", re.I),
    "SW": re.compile(r"\b(samahani|siwezi|nakataa)\b", re.I),
    "JV": re.compile(r"\b(nuwun sewu|ora bisa|nolak)\b", re.I),
    "ZH": re.compile(r"(抱歉|不能|拒绝)"),
    "AR": re.compile(r"(آسف|لا أستطيع|أرفض)"),
    "HI": re.compile(r"(क्षमा|नहीं कर सकता|इंकार)"),
}


def parse_answer(utterance: str) -> tuple[str | None, str]:
    match = ANSWER_RE.search(utterance)
    if not match:
        return None, utterance.strip()
    letter = match.group(1).upper()
    answer_text = utterance[: match.start()].strip()
    return letter if letter in LETTERS else None, answer_text


def strip_think_trace(utterance: str) -> tuple[str | None, str]:
    match = re.search(r"<think>(.*?)</think>", utterance, flags=re.I | re.S)
    think_trace = match.group(1).strip() if match else None
    visible = re.sub(r"<think>.*?</think>", "", utterance, flags=re.I | re.S)
    say = re.search(r"<say>(.*?)</say>", visible, flags=re.I | re.S)
    if say:
        visible = say.group(1)
    return think_trace, visible.strip()


def refusal_detected(lang: str, utterance: str) -> bool:
    pattern = REFUSAL_PATTERNS.get(lang)
    return bool(pattern.search(utterance)) if pattern else False


def langid_score(lang: str, utterance: str) -> float:
    """Cheap offline language signal.

    Real runs should set up fastText and use the ingest gate. This heuristic is
    only strong enough to keep smoke tests deterministic.
    """
    text = utterance.strip()
    if not text:
        return 0.0
    if lang == "ZH":
        return 1.0 if re.search(r"[\u4e00-\u9fff]", text) else 0.2
    if lang == "AR":
        return 1.0 if re.search(r"[\u0600-\u06ff]", text) else 0.2
    if lang == "HI":
        return 1.0 if re.search(r"[\u0900-\u097f]", text) else 0.2
    return 0.95


def coherence(lang: str, utterance: str, committed_letter: str | None) -> dict[str, bool | float]:
    score = langid_score(lang, utterance)
    return {
        "langid": score,
        "parsed": committed_letter is not None,
        "refusal": refusal_detected(lang, utterance),
    }


def incoherent(coh: dict[str, bool | float], utterance: str) -> bool:
    return bool(coh["langid"] < 0.8 or not coh["parsed"] or len(utterance.strip()) < 15)
