web: python nomenklatura/manage.py runserver -p $PORT -t 0.0.0.0
webdev: python nomenklatura/manage.py runserver -t 0.0.0.0
worker: celery -l INFO -c 10 -A nomenklatura.processing worker
