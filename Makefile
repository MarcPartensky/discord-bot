start:
	pipenv run python .
update:
	pipenv lock --pre --clear
dev:
	docker-compose -f docker-compose.yml up --build --force-recreate --remove-orphans discord-bot-dev
prod:
	docker-compose -f docker-compose.yml up --build --force-recreate --remove-orphans discord-bot-prod
build:
	docker-compose -f docker-compose.yml build discord-bot-prod
push: build
	docker-compose -f docker-compose.yml push discord-bot-prod
requirements:
	pipenv lock -r > requirements.txt
setup:
	pip install pipenv
	pipenv shell
	pipenv install
recreate:
	docker-compose -f docker-compose.yml up --force-recreate discord-bot-dev
fixwithbrew:
	brwe install python@3.8
	sudo ln -sf /home/linuxbrew/.linuxbrew/Cellar/python@3.8/3.8.12_1/bin/python3.8 /usr/bin/python3.8

