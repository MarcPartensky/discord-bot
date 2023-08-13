start:
	poetry run python .
update:
	pipenv update
	pipenv run pip freeze > requirements.txt
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
fixwithbrew:
	brew install python@3.8
	sudo ln -sf /home/linuxbrew/.linuxbrew/Cellar/python@3.8/3.8.12_1/bin/python3.8 /usr/bin/python3.8

