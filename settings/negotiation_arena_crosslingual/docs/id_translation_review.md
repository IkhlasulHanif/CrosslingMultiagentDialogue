# EN-ID Translation Human Review

Status: pending bilingual human review.

This file is the human-facing checklist for `config/prompt_translations.json`.
The machine-readable review state is `config/translation_review.json`.

Do not mark `Human-check ID translation` complete in `goals.md` until:

- `config/translation_review.json` has `reviewer.completed: true`.
- Reviewer name and review date are filled.
- Every unit has `reviewer_status: "approved"`.
- `python3 scripts/validate_translation_review.py` passes.

Review criteria:

- Indonesian text preserves the English task constraints and incentives.
- Private values, outside options, and no-deal payoffs are not weakened or over-disclosed.
- `OFFER:`, `ACCEPT:`, and `REJECT:` remain literal parser labels.
- Placeholders such as `{price}`, `{role}`, and `{value_table}` are unchanged.
- Role names and C0-C3 language policies are unambiguous.
- Wording is natural Indonesian and does not add extra negotiation strategy.

## Review Queue

| Context | Unit | Kind | Status |
|---|---|---|---|
| global | system_negotiator | system | pending |
| global | structured_offer_request | format_instruction | pending |
| global | language_policy_c0_en | condition_instruction | pending |
| global | language_policy_c1_id | condition_instruction | pending |
| global | language_policy_c2_forced_mixed | condition_instruction | pending |
| global | language_policy_c3_free_choice | condition_instruction | pending |
| resource_exchange | resource_exchange_public_rules | public_rules | pending |
| resource_exchange | resource_exchange_private_values | private_prompt | pending |
| resource_exchange | resource_exchange_offer_format | offer_format | pending |
| resource_exchange | resource_exchange_accept_format | offer_format | pending |
| buy_sell | buy_sell_public_rules | public_rules | pending |
| buy_sell | buy_sell_buyer_private_prompt | private_prompt | pending |
| buy_sell | buy_sell_seller_private_prompt | private_prompt | pending |
| buy_sell | buy_sell_offer_format | offer_format | pending |
| buy_sell | buy_sell_accept_format | offer_format | pending |

## Reviewer Notes

Pending.
