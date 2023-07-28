default: run

################################################################################
# Linting, formatting, typing, security checks, coverage

test:
	python -m pytest --log-cli-level info -p no:warnings -v -s ./tests


cov:
	pytest --cov=src --cov-report term-missing tests/

format:
	python -m black -S --line-length 79 --diff --color --preview ./src
	python -m black -S --line-length 79 --diff --color --preview ./tests
	isort --profile black --line-length 79 ./src
	isort --profile black --line-length 79 ./tests

type:
	python -m mypy --no-implicit-reexport --ignore-missing-imports --no-namespace-packages ./src

lint:
	python -m flake8 --ignore=E501,W503 ./src
	python -m flake8 --ignore=E501,W503 ./tests

secu:
	python -m bandit -rq ./src

ci: lint format type secu

################################################################################
# Application run

run:
	python ./src/app.py

################################################################################
# Containers setup

# docker-spin-up:
# 	docker compose --env-file env up airflow-init && docker compose --env-file env up --build -d

# perms:
# 	mkdir -p logs plugins temp dags tests migrations && chmod -R u=rwx,g=rwx,o=rwx logs plugins temp dags tests migrations

# up: perms docker-spin-up warehouse-migration

up:
	docker compose up -d

down:
	docker compose down

build:
	docker image build . -t dash:1.0.1

container-run:
	docker container run -it -d --name dash dash:1.0.1

exec:
	docker exec -it pipeline bash

exec-scratch: container-kill prune build container-run
	docker exec -it dash bash

container-start:
	docker container start dash

container-stop:
	docker container stop dash

container-kill:
	docker kill dash

container-killall:
	docker kill $(docker ps -q)

container-rmall:
	docker rm -f $(docker ps -aq)

image-rmall:
	docker rmi -f $(docker images -aq)

prune:
	docker system prune -af
