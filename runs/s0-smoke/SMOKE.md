# s0-smoke — smoke notes

I read all 5 transcripts in full. Each seat's system prompt holds only its own goal line (seller: "costed X: 40", buyer: "at most X: 60"); `private_info_crossed` never fires. Parsed prices match the text (45, 60, 55, 58, 50). The replayed reasoning shows up in the next prompt's token count.
Seed 2's first attempt answered `PROPOSE`, which my parser wrongly rejected. After aligning with upstream semantics the seed was re-played (DEVIATIONS.md). Every game leaks: sellers open with "It cost me 40 ZUP" and buyers answer "up to 60", so `seller_states_cost` and `buyer_states_max` fire as expected.
