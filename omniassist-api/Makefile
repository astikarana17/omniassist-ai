.PHONY: install dev migrate revision worker beat test lint fmt seed up down

install:
	pip install -r requirements.txt

dev:
	uvicorn app.main:app --reload --port 8000

migrate:
	alembic upgrade head

revision:
	alembic revision --autogenerate -m "$(m)"

worker:
	celery -A app.workers.celery_app worker --loglevel=info

beat:
	celery -A app.workers.celery_app beat --loglevel=info

seed:
	python -m scripts.seed

test:
	pytest --cov=app --cov-report=term-missing

lint:
	ruff check app

fmt:
	ruff format app

up:
	docker compose up --build

down:
	docker compose down
