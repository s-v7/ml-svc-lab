.PHONY: setup ingest baseline test lint

PY = python3
export PYTHONPATH := .

setup:
	pip install -r requirements.txt --break-system-packages
ingest: ## Baixa série histórica (Open-Meteo, sem chave)
	$(PY) -m experiments.weather.ingest_openmeteo
baseline: ## Roda os baselines (régua dos modelos)
	$(PY) -m experiments.weather.baseline
test:
	$(PY) -m pytest tests/ -q
lint:
	ruff check .



