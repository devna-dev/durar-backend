up:
	COMPOSE_HTTP_TIMEOUT=200 docker-compose up -d $(filter-out $@,$(MAKECMDGOALS))

build:
	docker-compose build $(filter-out $@,$(MAKECMDGOALS))

build-no-cache:
	docker-compose build $(filter-out $@,$(MAKECMDGOALS)) --no-cache

stop:
	docker-compose stop $(filter-out $@,$(MAKECMDGOALS))

run:
	docker-compose run --rm $(filter-out $@,$(MAKECMDGOALS))

runserver:
	docker-compose run --rm --service-ports web python manage.py runserver 0.0.0.0:8000

restart:
	docker-compose restart $(filter-out $@,$(MAKECMDGOALS))

manage:
	docker-compose run --rm web python manage.py $(filter-out $@,$(MAKECMDGOALS))

bash:
	docker-compose run --rm web bash

makemigrations:
	docker-compose run --rm web python manage.py makemigrations $(filter-out $@,$(MAKECMDGOALS))

migrate:
	docker-compose run --rm web python manage.py migrate $(filter-out $@,$(MAKECMDGOALS))

merge-fe:
	git submodule update --recursive --remote

urls:
	docker-compose run --rm web python manage.py show_urls

start_celery:
	docker-compose run --rm web sh -c 'start_celery'

logs:
	COMPOSE_HTTP_TIMEOUT=200 docker-compose logs -f --tail=70 $(filter-out $@,$(MAKECMDGOALS))

test:
	docker-compose run --service-ports --rm web python manage.py test --debug-mode $(filter-out $@,$(MAKECMDGOALS))

debug:
	docker-compose run --service-ports --rm web $(filter-out $@,$(MAKECMDGOALS))

init_data:
	docker-compose run --rm web python manage.py generate_initial_data

superadmin:
	docker-compose run --rm web python manage.py createsuperuser

psql:
	docker-compose run --rm db run_psql

restore_db:
	docker-compose run --rm db restore $(filter-out $@,$(MAKECMDGOALS))

backup_db:
	docker-compose run --rm db backup

list_backups:
	docker-compose run --rm db list-backups

ps:
	docker-compose ps

makemessages:
	docker-compose run --rm web python manage.py makemessages

generate_swagger:
	docker-compose run --rm web python manage.py generateschema

silk_clear_request_log:
	docker-compose run --rm web python manage.py silk_clear_request_log

invalidate_cachalot:
	COMPOSE_HTTP_TIMEOUT=200 docker-compose run --rm web python manage.py invalidate_cachalot

down:
	COMPOSE_HTTP_TIMEOUT=200 docker-compose down

site-debug:
	docker-compose run --service-ports -d web; docker-compose up web

