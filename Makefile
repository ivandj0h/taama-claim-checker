.PHONY: up down logs test status

up:
	docker compose up --build -d

down:
	docker compose down

logs:
	docker compose logs -f

status:
	docker compose ps

test:
	docker compose run --rm app pytest