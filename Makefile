up-dev:
	docker-compose -d --build up dev
down-dev:
	docker stop quyca-dev; docker rm quyca-dev; docker rmi colav/quyca-dev:dev
shell-dev:
	docker-compose exec dev bash
build-dev:
	docker build --file Dockerfile -t colav/quyca-dev:dev --target development .

up-prod:
	docker-compose up -d --build prod;
down-prod:
	docker stop quyca-prod; docker rm quyca-prod; docker rmi colav/quyca-prod:latest
shell-prod:
	docker-compose exec prod bash
build-prod:
	docker build --file Dockerfile -t colav/quyca-prod:latest --target development .

up-local:
	docker-compose up --build local;
down-local:
	docker stop quyca-local; docker rm quyca-local; docker rmi colav/quyca-local:local
shell-local:
	docker-compose exec local bash
build-local:
	docker build --file Dockerfile -t colav/quyca-local:local --target local .

