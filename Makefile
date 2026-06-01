.PHONY: install generate-data run-pipeline test lint dashboard api docker-up docker-down deploy-check

install:
	pip install -r requirements.txt

generate-data:
	python -m src.data_generation.generate_tasks
	python -m src.data_generation.generate_model_registry
	python -m src.data_generation.generate_model_outputs
	python -m src.data_generation.generate_constraints

run-pipeline:
	python -m src.pipeline.run_all

test:
	python -m pytest

lint:
	python -m ruff check .

dashboard:
	streamlit run src/dashboard/app.py

api:
	uvicorn src.api.main:app --reload

docker-up:
	docker compose up --build

docker-down:
	docker compose down

deploy-check:
	python scripts/deploy_readiness_check.py
