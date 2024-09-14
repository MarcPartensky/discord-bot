run:
	uv clean
	uv --directory discord_bot run python .
update:
	uv lock
	uv pip compile requirements.txt \
	   --universal \
	   --output-file requirements.txt
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
	uv pip install
	uv shell
recreate:
	docker-compose -f docker-compose.yml up --force-recreate dev

