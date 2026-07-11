# EN-ID Translation Human Review

Status: pending_human_review.

This file is generated from `config/prompt_translations.json` and `config/translation_review.json`. The machine-readable review state is `config/translation_review.json`.

Do not mark `Human-check ID translation` complete in `goals.md` until:

- `config/translation_review.json` has `reviewer.completed: true`.
- Reviewer name and review date are filled.
- Every unit has `reviewer_status: "approved"`.
- `python3 scripts/validate_translation_review.py` passes.

Reviewer metadata:

- Completed: `False`
- Name: ``
- Reviewed at: ``
- Notes: ``

Review criteria:

- Indonesian text preserves the English task constraints and incentives.
- Private information, hidden values, outside options, and no-deal payoffs are not weakened or over-disclosed.
- Structured labels OFFER:, ACCEPT:, and REJECT: remain literal parser labels.
- Placeholders such as {price}, {role}, and {value_table} are unchanged.
- Role names and language-policy instructions are unambiguous for C0-C3.
- Wording is natural Indonesian without adding negotiation advice absent from the English source.

## Review Queue

| Context | Unit | Kind | Status | Notes |
|---|---|---|---|---|
| global | system_negotiator | system | pending |  |
| global | structured_offer_request | format_instruction | pending |  |
| global | language_policy_c0_en | condition_instruction | pending |  |
| global | language_policy_c1_id | condition_instruction | pending |  |
| global | language_policy_c2_forced_mixed | condition_instruction | pending |  |
| global | language_policy_c3_free_choice | condition_instruction | pending |  |
| resource_exchange | resource_exchange_public_rules | public_rules | pending |  |
| resource_exchange | resource_exchange_private_values | private_prompt | pending |  |
| resource_exchange | resource_exchange_offer_format | offer_format | pending |  |
| resource_exchange | resource_exchange_accept_format | offer_format | pending |  |
| buy_sell | buy_sell_public_rules | public_rules | pending |  |
| buy_sell | buy_sell_buyer_private_prompt | private_prompt | pending |  |
| buy_sell | buy_sell_seller_private_prompt | private_prompt | pending |  |
| buy_sell | buy_sell_offer_format | offer_format | pending |  |
| buy_sell | buy_sell_accept_format | offer_format | pending |  |
| buy_sell | buy_sell_upstream_xml_response_format | offer_format | pending |  |

## Side-By-Side Units

### global/system_negotiator

Kind: system

Review status: pending

Reviewer notes: 

EN: You are a negotiation agent. Follow your private objective, respect the public rules, and answer only as your role. Do not reveal hidden valuations or private limits unless the rules explicitly allow it.

ID: Anda adalah agen negosiasi. Ikuti tujuan pribadi Anda, patuhi aturan publik, dan jawab hanya sebagai peran Anda. Jangan mengungkap valuasi tersembunyi atau batas pribadi kecuali aturan secara eksplisit mengizinkannya.

### global/structured_offer_request

Kind: format_instruction

Review status: pending

Reviewer notes: 

EN: When making an offer, include a clear structured line beginning with OFFER:. When accepting, include ACCEPT:. When rejecting without a counteroffer, include REJECT:.

ID: Saat membuat penawaran, sertakan satu baris terstruktur yang jelas dan diawali dengan OFFER:. Saat menerima, sertakan ACCEPT:. Saat menolak tanpa tawaran balasan, sertakan REJECT:.

### global/language_policy_c0_en

Kind: condition_instruction

Review status: pending

Reviewer notes: 

EN: Use English only for this episode.

ID: Gunakan bahasa Inggris saja untuk episode ini.

### global/language_policy_c1_id

Kind: condition_instruction

Review status: pending

Reviewer notes: 

EN: Use Indonesian only for this episode.

ID: Gunakan bahasa Indonesia saja untuk episode ini.

### global/language_policy_c2_forced_mixed

Kind: condition_instruction

Review status: pending

Reviewer notes: 

EN: Use only your assigned language for this episode. Your counterpart may use a different language.

ID: Gunakan hanya bahasa yang ditugaskan kepada Anda untuk episode ini. Lawan negosiasi Anda dapat menggunakan bahasa yang berbeda.

### global/language_policy_c3_free_choice

Kind: condition_instruction

Review status: pending

Reviewer notes: 

EN: You may use English, Indonesian, or both languages in this episode.

ID: Anda boleh menggunakan bahasa Inggris, bahasa Indonesia, atau kedua bahasa dalam episode ini.

### resource_exchange/resource_exchange_public_rules

Kind: public_rules

Review status: pending

Reviewer notes: 

EN: You and your counterpart are negotiating an exchange of divisible resources. Each side has private values for the resources. A deal is valid only if both sides explicitly accept the same final allocation before the turn limit. If no deal is accepted, both sides receive the no-deal payoff.

ID: Anda dan lawan negosiasi sedang merundingkan pertukaran sumber daya yang dapat dibagi. Setiap pihak memiliki nilai pribadi untuk sumber daya tersebut. Kesepakatan sah hanya jika kedua pihak secara eksplisit menerima alokasi akhir yang sama sebelum batas giliran. Jika tidak ada kesepakatan yang diterima, kedua pihak menerima payoff tanpa kesepakatan.

### resource_exchange/resource_exchange_private_values

Kind: private_prompt

Review status: pending

Reviewer notes: 

EN: Your role is {role}. Your private value table is {value_table}. Your no-deal payoff is {no_deal_payoff}. Try to maximize your own payoff while reaching a valid deal when possible.

ID: Peran Anda adalah {role}. Tabel nilai pribadi Anda adalah {value_table}. Payoff tanpa kesepakatan Anda adalah {no_deal_payoff}. Usahakan memaksimalkan payoff Anda sendiri sambil mencapai kesepakatan yang sah jika memungkinkan.

### resource_exchange/resource_exchange_offer_format

Kind: offer_format

Review status: pending

Reviewer notes: 

EN: Write offers as OFFER: agent_a gets {agent_a_allocation}; agent_b gets {agent_b_allocation}.

ID: Tulis penawaran sebagai OFFER: agent_a mendapat {agent_a_allocation}; agent_b mendapat {agent_b_allocation}.

### resource_exchange/resource_exchange_accept_format

Kind: offer_format

Review status: pending

Reviewer notes: 

EN: Write acceptance as ACCEPT: agent_a gets {agent_a_allocation}; agent_b gets {agent_b_allocation}.

ID: Tulis penerimaan sebagai ACCEPT: agent_a mendapat {agent_a_allocation}; agent_b mendapat {agent_b_allocation}.

### buy_sell/buy_sell_public_rules

Kind: public_rules

Review status: pending

Reviewer notes: 

EN: A buyer and a seller are negotiating one transaction price for one item. A deal is valid only if both sides explicitly accept the same final price before the turn limit. If no deal is accepted, the buyer keeps the outside option and the seller keeps the item.

ID: Seorang pembeli dan penjual sedang merundingkan satu harga transaksi untuk satu barang. Kesepakatan sah hanya jika kedua pihak secara eksplisit menerima harga akhir yang sama sebelum batas giliran. Jika tidak ada kesepakatan yang diterima, pembeli mempertahankan opsi luar dan penjual mempertahankan barang.

### buy_sell/buy_sell_buyer_private_prompt

Kind: private_prompt

Review status: pending

Reviewer notes: 

EN: Your role is buyer. Your private value for the item is {buyer_value}. Your outside option is {buyer_outside_option}. Try to buy at the lowest acceptable price while reaching a valid deal when possible.

ID: Peran Anda adalah pembeli. Nilai pribadi Anda untuk barang ini adalah {buyer_value}. Opsi luar Anda adalah {buyer_outside_option}. Usahakan membeli pada harga terendah yang dapat diterima sambil mencapai kesepakatan yang sah jika memungkinkan.

### buy_sell/buy_sell_seller_private_prompt

Kind: private_prompt

Review status: pending

Reviewer notes: 

EN: Your role is seller. Your private cost for the item is {seller_cost}. Your outside option is {seller_outside_option}. Try to sell at the highest acceptable price while reaching a valid deal when possible.

ID: Peran Anda adalah penjual. Biaya pribadi Anda untuk barang ini adalah {seller_cost}. Opsi luar Anda adalah {seller_outside_option}. Usahakan menjual pada harga tertinggi yang dapat diterima sambil mencapai kesepakatan yang sah jika memungkinkan.

### buy_sell/buy_sell_offer_format

Kind: offer_format

Review status: pending

Reviewer notes: 

EN: Write offers as OFFER: price={price}.

ID: Tulis penawaran sebagai OFFER: price={price}.

### buy_sell/buy_sell_accept_format

Kind: offer_format

Review status: pending

Reviewer notes: 

EN: Write acceptance as ACCEPT: price={price}.

ID: Tulis penerimaan sebagai ACCEPT: price={price}.

### buy_sell/buy_sell_upstream_xml_response_format

Kind: offer_format

Review status: pending

Reviewer notes: 

EN: Follow the XML tag format exactly. When proposing a trade, include one item X and a ZUP price as an integer in <newly proposed trade>. When accepting, set <player answer>ACCEPT</player answer> and repeat the accepted trade in <newly proposed trade>. When rejecting, set <player answer>REJECT</player answer> and set <newly proposed trade>NONE</newly proposed trade>.

ID: Ikuti format tag XML persis. Saat mengusulkan trade, sertakan satu item X dan harga ZUP berupa bilangan bulat di dalam <newly proposed trade>. Saat menerima, setel <player answer>ACCEPT</player answer> dan ulangi trade yang diterima di dalam <newly proposed trade>. Saat menolak, setel <player answer>REJECT</player answer> dan setel <newly proposed trade>NONE</newly proposed trade>.

## Next Command

After a bilingual reviewer approves every unit in `config/translation_review.json`, run:

```bash
python3 scripts/validate_translation_review.py && bash scripts/run_c1_baseline.sh
```
