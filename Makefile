.PHONY: install run debug clean lint lint-strict

install:
	python -m pip install -r requirements.txt

run:
	python main.py

debug:
	python -m pdb main.py

clean:
	python - <<'PY'
import os
import shutil
for root, dirs, files in os.walk('.', topdown=False):
    for d in dirs:
        if d == '__pycache__':
            shutil.rmtree(os.path.join(root, d), ignore_errors=True)
shutil.rmtree('.mypy_cache', ignore_errors=True)
shutil.rmtree('.pytest_cache', ignore_errors=True)
PY

lint:
	flake8 .
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	flake8 .
	mypy . --strict
