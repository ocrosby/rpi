.DEFAULT_GOAL := data

.PHONY: install freeze clean data

install:
	python3 -m pip install --upgrade pip
	python3 -m pip install -r requirements.txt

freeze:
	pip freeze > requirements.txt

clean:
	find . -name "*.csv" -type f -delete

data: clean
	python3 rpi/services/match.py
