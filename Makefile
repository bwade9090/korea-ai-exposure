# Entry points for korea-ai-exposure (see CLAUDE.md). Recipes need GNU Make and a POSIX shell:
# Linux, macOS, or Git Bash on Windows. If Python 3.12 is not found, pass its path:
#   make setup PYTHON=/path/to/python3.12

ifeq ($(OS),Windows_NT)
PYTHON ?= py -3.12
VENV_PY := .venv/Scripts/python.exe
else
PYTHON ?= python3.12
VENV_PY := .venv/bin/python
endif

.PHONY: setup lock check fetch build figures facts brief all

# Create .venv and install the pinned, hash-checked environment.
setup:
	$(PYTHON) -m venv .venv
	$(VENV_PY) -m pip install --require-hashes -r requirements.txt
	$(VENV_PY) -m pip install --no-deps --no-build-isolation -e .

# Re-pin requirements.txt from requirements.in. Run after editing requirements.in.
lock:
	$(VENV_PY) -m piptools compile --quiet --generate-hashes --allow-unsafe --strip-extras \
		--output-file requirements.txt requirements.in

# Lint, format check, and the offline test suite (data-marked tests skip without downloads).
check:
	$(VENV_PY) -m ruff check .
	$(VENV_PY) -m ruff format --check .
	$(VENV_PY) -m pytest

# Download every file pinned in data/manifest.json and verify its checksum.
fetch:
	$(VENV_PY) -m korea_ai_exposure.fetch

# Implemented in later phases (docs/PLAN.md section 8).
build figures facts brief:
	@echo "make $@: not implemented yet (see docs/PLAN.md section 8)"

all: fetch build figures facts brief
