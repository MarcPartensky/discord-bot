start:
	pipenv run python .
update:
	pipenv lock --pre --clear
dev:
	docker-compose -f docker-compose.yml up --build --force-recreate --remove-orphans
