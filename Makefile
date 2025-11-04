.PHONY: help build up down restart logs test clean test-api

help:
	@echo "Fintech Card Processing Platform - Make Commands"
	@echo ""
	@echo "Available commands:"
	@echo "  make build      - Build all Docker containers"
	@echo "  make up         - Start all services"
	@echo "  make down       - Stop all services"
	@echo "  make restart    - Restart all services"
	@echo "  make logs       - View logs from all services"
	@echo "  make logs-be    - View backend logs"
	@echo "  make logs-fe    - View frontend logs"
	@echo "  make test       - Run backend tests"
	@echo "  make test-api   - Run API integration tests"
	@echo "  make shell      - Open Django shell"
	@echo "  make migrate    - Run database migrations"
	@echo "  make clean      - Stop services and remove volumes"
	@echo ""

build:
	docker-compose build

up:
	docker-compose up -d
	@echo ""
	@echo "Services started!"
	@echo "Frontend: http://localhost:3000"
	@echo "Backend: http://localhost:8000"
	@echo "API Docs: http://localhost:8000/swagger/"
	@echo ""

down:
	docker-compose down

restart: down up

logs:
	docker-compose logs -f

logs-be:
	docker-compose logs -f backend

logs-fe:
	docker-compose logs -f frontend

test:
	docker-compose exec backend pytest

test-api:
	python test_api.py

shell:
	docker-compose exec backend python manage.py shell

migrate:
	docker-compose exec backend python manage.py makemigrations
	docker-compose exec backend python manage.py migrate

clean:
	docker-compose down -v
	@echo "Containers stopped and volumes removed"

setup: build up
	@echo "Setup complete! Services are running."
