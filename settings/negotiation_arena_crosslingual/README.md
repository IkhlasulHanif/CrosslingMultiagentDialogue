# NegotiationArena Cross-Lingual Setting

Separate setting for B5 NegotiationArena cross-lingual contact experiments.

Read first: `reports/status.md`.

Layout:

- `code/negotiation_arena_crosslingual/`: setting implementation package.
- `scripts/`: stable command wrappers and shell entry points.
- `external/NegotiationArena/`: canonical upstream benchmark checkout.

Run:

```bash
./harness.sh status
./harness.sh check
./harness.sh run-smoke
python3 scripts/validate_pairwise_channel_plan.py
python3 scripts/generate_translation_review_packet.py
bash scripts/run_c0_baseline.sh
bash scripts/run_c0_resource_exchange_baseline.sh
bash scripts/run_c0_openai_baseline.sh
bash scripts/run_c0_openai_resource_exchange_baseline.sh
python3 scripts/check_g2_capability_floor.py
bash scripts/run_c1_baseline.sh
bash scripts/run_c1_openai_bridge_baseline.sh
python3 scripts/run_pairwise_buy_sell.py --pair EN-ID --condition C2 --counterbalance buyer_lx_seller_ly --seed 101
python3 scripts/run_pairwise_resource_exchange.py --pair EN-ID --condition C2 --counterbalance buyer_lx_seller_ly --seed 101
```
