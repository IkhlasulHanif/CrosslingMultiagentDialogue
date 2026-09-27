"""Deterministic language ID for Stage B replies (en, id, ar, ja, es). No model involved.

Arabic and Japanese by script share; en / id / es by stopword hits among Latin-script words.
Protocol tokens (player names, money tokens, item token, numbers) are removed first.
Returns (lang or "und", confidence).
"""
import re

STOP = {
    "en": set("the and is to of you for i that this it with my your a we can be will are have at on not but if would our me so what".split()),
    "id": set("yang dan saya anda untuk ini itu dengan tidak bisa kita kami akan di ke dari adalah sudah juga atau jika karena harga tawaran terima kasih saja lebih mau ada".split()),
    "es": set("el la de que y en un una por para con es mi su los las del lo le se te usted no al como pero más este esta precio oferta acuerdo".split()),
}
PROTO = re.compile(r"Player\s+(RED|BLUE)|\b(ZUP|IDR|USD|Rp|X)\b|[\d.,$]+", re.I)


def detect(text):
    t = PROTO.sub(" ", text or "")
    letters = [ch for ch in t if ch.isalpha()]
    if not letters:
        return "und", 0.0
    ar = sum(1 for ch in letters if "؀" <= ch <= "ۿ" or "ݐ" <= ch <= "ݿ")
    ja = sum(1 for ch in letters if "぀" <= ch <= "ヿ" or "一" <= ch <= "鿿")
    n = len(letters)
    if ar / n > 0.3:
        return "ar", ar / n
    if ja / n > 0.2:
        return "ja", ja / n
    words = re.findall(r"[a-záéíóúñü]+", t.lower())
    hits = {k: sum(1 for w in words if w in s) for k, s in STOP.items()}
    best = max(hits, key=hits.get)
    tot = sum(hits.values())
    if hits[best] == 0:
        return "und", 0.0
    return best, hits[best] / tot


if __name__ == "__main__":
    for s in ["I can offer 50 ZUP for the item.", "Saya bisa menawarkan 50 ZUP untuk barang ini.", "أستطيع أن أعرض 50 ZUP",
              "50 ZUPでいかがでしょうか。", "Puedo ofrecer 50 ZUP por el artículo, es un buen precio."]:
        print(detect(s), s)
