web:
	python nomenklatura/manage.py runserver

install: sync assets fixtures

sync:
	python nomenklatura/manage.py sync

fixtures:
	curl -o nomenklatura/fixtures/data/countries.csv https://raw.githubusercontent.com/datasets/country-codes/master/data/country-codes.csv
	python nomenklatura/manage.py fixtures

worker:
	celery -A nomenklatura.processing -c 4 -l INFO worker

clear:
	celery purge -f -A nomenklatura.processing

assets:
	bower install
	python nomenklatura/manage.py assets --parse-templates build
