# NegotiationArena EN-ID Translation Notes

`config/prompt_translations.json` contains the setting-local Indonesian draft
for selected NegotiationArena rules and prompt units.

Status: translated, pending human check.

Human-review packet:

- `docs/id_translation_review.md` is the reviewer-facing checklist.
- `config/translation_review.json` is the machine-readable review queue.
- `scripts/validate_translation_review.py` checks that the queue is aligned
  with `config/prompt_translations.json` and that completion is not claimed
  unless every unit is approved by a named reviewer.

Scope:

- Global negotiation system prompt.
- Structured offer / accept / reject instruction.
- C0-C3 language policy instructions.
- Resource exchange public rules, private value prompt, offer format, and accept format.
- Buy/sell public rules, buyer prompt, seller prompt, offer format, and accept format.

Known limits:

- These are canonical setting-local prompt units, not verified upstream prompt
  IDs. The upstream mapping remains blocked until a local NegotiationArena
  checkout is available.
- Human bilingual review is still required before using the Indonesian prompts
  for reported benchmark runs.
- Structured labels `OFFER:`, `ACCEPT:`, `REJECT:`, placeholder names, and role
  identifiers are intentionally not translated so parsers can share one schema.
