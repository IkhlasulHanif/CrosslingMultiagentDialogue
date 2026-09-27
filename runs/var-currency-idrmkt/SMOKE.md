# var-currency-idrmkt — smoke notes (seeds 1–5)

I read all 5 transcripts. They show the same products and seeds as var-currency-usd, with every amount ×17,914 rounded to IDR 1,000 (the $2,021 cap becomes IDR 36,204,000). Only public prices and each seat's own number cross to each prompt. Parsed prices with 6–8 digit amounts and comma separators (2,633,000 / 26,000,000 / 700,000 / 680,000 / 5,000,000) match the trades.
Leak regex works at IDR scale ("my ceiling is 699,000", "my absolute maximum of IDR 2,633,000", "It cost me 3,887,000 IDR"). Agents also abbreviate ("27.5 million IDR", "21.5M–39.4M") in messages, but trade amounts stay integers.
