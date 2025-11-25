.PHONY: run install ui

install:
	pip install -e .

run:
	python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

ui:
	open app/test_ui.html
