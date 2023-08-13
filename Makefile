start:
	poetry run python .
update:
	poetry update
	poetry export --output requirements.txt
dev:
	docker-compose -f docker-compose.yml up -d --build --force-recreate --remove-orphans dev
prod:
	docker-compose -f docker-compose.yml up -d --build --force-recreate --remove-orphans prod
build: update
	docker-compose -f docker-compose.yml build prod
push: build
	docker-compose -f docker-compose.yml push prod
deploy: push
	DOCKER_HOST=ssh://vps docker service update vps_esclave
setup:
	poetry install
	poetry shell
recreate:
	docker-compose -f docker-compose.yml up --force-recreate dev

