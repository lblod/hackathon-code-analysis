repo-analysis: .venv
	.venv/bin/python repo-analysis.py

install-requirements: .venv
	.venv/bin/pip install -r requirements.txt

freeze-requirements: .venv
	.venv/bin/python3 -m pip freeze > requirements.txt

.venv:
	python3 -m venv .venv



.PHONY: install-requirements freeze-requirements repo-analysis
