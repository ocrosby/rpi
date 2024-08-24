<<<<<<< HEAD
.DEFAULT_GOAL := data

.PHONY: install freeze clean data

=======
>>>>>>> 000d4ad (chore: wip)
install:
	python3 -m pip install --upgrade pip
	python3 -m pip install -r requirements.txt

freeze:
	pip freeze > requirements.txt
<<<<<<< HEAD

clean:
	find . -name "*.csv" -type f -delete

data: clean
	python3 rpi/services/match.py
=======
>>>>>>> 000d4ad (chore: wip)
