up:
	docker compose up -d --build;
down:
	docker compose down --remove-orphans --rmi all
shell:
	docker compose exec colav/quyca-dev bash
build:
	docker build --file Dockerfile -t colav/quyca-dev:dev --target development .

