start:
	pipenv run python .
update:
	pipenv lock --pre --clear
dev:
	docker-compose -f docker-compose.yml up -d --build --force-recreate --remove-orphans dev
prod:
	docker-compose -f docker-compose.yml up -d --build --force-recreate --remove-orphans prod
build: requirements
	docker-compose -f docker-compose.yml build prod
push: build
	docker-compose -f docker-compose.yml push prod
requirements:
	pipenv lock -r > requirements.txt
setup:
	pip install pipenv
	pipenv shell
	pipenv install
recreate:
	docker-compose -f docker-compose.yml up --force-recreate dev
fixwithbrew:
	brwe install python@3.8
	sudo ln -sf /home/linuxbrew/.linuxbrew/Cellar/python@3.8/3.8.12_1/bin/python3.8 /usr/bin/python3.8

