.PHONY: makeup down logs test

makeup:
	docker compose up --build -d

down:
	docker compose down

logs:
	docker compose logs -f

test:
	docker compose run --rm app pytest