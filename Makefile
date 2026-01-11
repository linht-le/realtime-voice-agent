.PHONY: install run-be run-fe reset-db setup migrate-create migrate-upgrade migrate-downgrade

install:
	uv pip install -e ".[dev]"
	cd app/frontend && npm install

run-be:
	uvicorn app.backend.main:app --host 0.0.0.0 --port 8000 --reload

run-fe:
	cd app/frontend && npm run dev

setup:
	alembic upgrade head

reset-db:
	python app/backend/scripts/reset_db.py

migrate-create:
	@read -p "Migration message: " message; \
	alembic revision --autogenerate -m "$$message"

migrate-upgrade:
	alembic upgrade head

migrate-downgrade:
	alembic downgrade -1
