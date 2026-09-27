# GOALS §8 commands. RUN = run name (configs/runs/$(RUN).toml)
PY ?= python3
N ?= 5

.PHONY: smoke run score report cost test
smoke:
	$(PY) -m arena_plus.run run $(RUN) --n $(N)
run:
	$(PY) -m arena_plus.run run $(RUN)
score:
	$(PY) -m arena_plus.run score $(RUN)
report:
	$(PY) -m arena_plus.report
cost:
	$(PY) -m arena_plus.run cost
test:
	$(PY) -m tests.test_upstream_fidelity && $(PY) -m tests.test_variants
