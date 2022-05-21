start:
	pipenv run python .
update:
	pipenv lock --pre --clear
	pipenv lock -r > requirements.txt
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
	pip install pipenv
	pipenv shell
	pipenv install
recreate:
	docker-compose -f docker-compose.yml up --force-recreate dev
