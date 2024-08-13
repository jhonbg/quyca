up-dev:
	docker-compose up dev
down-dev:
	docker stop quyca-dev; docker rm quyca-dev; docker rmi colav/quyca-dev:dev
up-prod:
	docker-compose up prod;
down-prod:
	docker stop quyca-prod; docker rm quyca-prod; docker rmi colav/quyca-prod:latest
shell-dev:
	docker-compose exec dev bash
shell-prod:
	docker-compose exec prod bash
build-dev:
	docker build --file Dockerfile -t colav/quyca-dev:dev --target development .
build-prod:
	docker build --file Dockerfile -t colav/quyca-prod:latest --target development .

