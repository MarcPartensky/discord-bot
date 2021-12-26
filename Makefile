start:
	pipenv run python .
update:
	pipenv lock --pre --clear
dev:
	docker-compose -f docker-compose.yml up --build --force-recreate --remove-orphans discord-bot
build:
	docker-compose -f docker-compose.yml build discord-bot
push: build
	docker-compose -f docker-compose.yml push discord-bot
requirements:
	pipenv lock -r > requirements.txt
setup:
	pip install pipenv
	pipenv shell
	pipenv install
recreate:
	docker-compose -f docker-compose.yml up --force-recreate
