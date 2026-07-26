PYTHON ?= python3

.PHONY: bootstrap ingest cells run run-all report test check-m0.1 check-m1.1 check-m2.1 check-m2.3 check-m3.1 check-m3.2 check-m3.3 check-m3.4 check-m4.1 check-m5.1

bootstrap:
	$(PYTHON) scripts/bootstrap.py

ingest:
	$(PYTHON) scripts/ingest.py

cells:
	$(PYTHON) scripts/generate_cells.py

run:
	@test -n "$(CELL)" || (echo "CELL is required, e.g. make run CELL=m0_smoke" >&2; exit 2)
	$(PYTHON) scripts/run_cell.py --cell "$(CELL)"

run-all:
	@test -n "$(PHASE)" || (echo "PHASE is required: pilot|core|h5|safety|culture" >&2; exit 2)
	$(PYTHON) scripts/run_all.py --phase "$(PHASE)"

report:
	$(PYTHON) scripts/report.py

test:
	$(PYTHON) -m pytest tests/test_schema.py

check-m0.1:
	$(PYTHON) scripts/check_task.py M0.1

check-m1.1:
	$(PYTHON) scripts/check_task.py M1.1

check-m2.1:
	$(PYTHON) scripts/check_task.py M2.1

check-m2.3:
	$(PYTHON) scripts/check_task.py M2.3

check-m3.1:
	$(PYTHON) scripts/check_task.py M3.1

check-m3.2:
	$(PYTHON) scripts/check_task.py M3.2

check-m3.3:
	$(PYTHON) scripts/check_task.py M3.3

check-m3.4:
	$(PYTHON) scripts/check_task.py M3.4

check-m4.1:
	$(PYTHON) scripts/check_task.py M4.1

check-m5.1:
	$(PYTHON) scripts/check_task.py M5.1
