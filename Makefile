<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> 5a1bcf8 (chore: wip)
.DEFAULT_GOAL := data

.PHONY: install freeze clean data

<<<<<<< HEAD
=======
>>>>>>> 000d4ad (chore: wip)
=======
>>>>>>> 5a1bcf8 (chore: wip)
install:
	python3 -m pip install --upgrade pip
	python3 -m pip install -r requirements.txt

freeze:
	pip freeze > requirements.txt
<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> 5a1bcf8 (chore: wip)

clean:
	find . -name "*.csv" -type f -delete

data: clean
	python3 rpi/services/match.py
<<<<<<< HEAD
=======
>>>>>>> 000d4ad (chore: wip)
=======
>>>>>>> 5a1bcf8 (chore: wip)
