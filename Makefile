setup:
	python3 -m venv venv
	./venv/bin/pip install -q --upgrade pip
	./venv/bin/pip install -q -r requirements.txt


all: venv/bin/python config/settings.yaml config/.secrets.yaml
	venv/bin/python 00-jira-filter-setup/app.py
	venv/bin/python 01-extract/app.py
	venv/bin/python 02-transform/app.py


jira-filter-setup: venv/bin/python config/settings.yaml config/.secrets.yaml
	venv/bin/python 00-jira-filter-setup/app.py


extract: venv/bin/python config/settings.yaml config/.secrets.yaml
	venv/bin/python 01-extract/app.py


transform: venv/bin/python config/settings.yaml
	venv/bin/python 02-transform/app.py
