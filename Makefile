web:
	python nomenklatura/manage.py runserver

worker:
	celery -A nomenklatura.processing -c 4 -l INFO worker

clear:
	celery purge -f -A nomenklatura.processing

assets:
	bower install
	python nomenklatura/manage.py assets --parse-templates build
