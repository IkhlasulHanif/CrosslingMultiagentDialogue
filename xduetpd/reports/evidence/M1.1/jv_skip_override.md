# JV Skip Override

- date: 2026-07-26
- requester: human owner
- instruction: ignore JV for now and do not stop at pilot
- implementation: skip JV cells, and skip any cell whose required stimulus language variant is unavailable
- guard: skipped cells are reported as shortfalls; unavailable language variants must not fall back to English
