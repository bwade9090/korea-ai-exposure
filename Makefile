# Entry points for korea-ai-exposure (see CLAUDE.md). Recipes need GNU Make and a POSIX shell:
# Linux, macOS, or Git Bash on Windows. If Python 3.12 is not found, pass its path:
#   make setup PYTHON=/path/to/python3.12

# Windows: native make sees OS=Windows_NT; MSYS and Cygwin builds of make do not, but their
# uname reports MINGW64_NT-..., MSYS_NT-... or CYGWIN_NT-...
UNAME := $(shell uname -s 2>/dev/null)
ifneq ($(or $(filter Windows_NT,$(OS)),$(findstring _NT,$(UNAME))),)
PYTHON ?= py -3.12
VENV_PY := .venv/Scripts/python.exe
else
PYTHON ?= python3.12
VENV_PY := .venv/bin/python
endif

.NOTPARALLEL:
.PHONY: setup lock check fetch build replicate figures facts brief all

# Create .venv and install the pinned, hash-checked environment.
setup:
	$(PYTHON) -c "import sys; sys.exit(0 if sys.version_info[:2] == (3, 12) else 'Python 3.12 is required; pass PYTHON=/path/to/python3.12')"
	$(PYTHON) -m venv .venv
	$(VENV_PY) -m pip install --require-hashes -r requirements.txt
	$(VENV_PY) -m pip install --no-deps --no-build-isolation -e .

# Re-pin requirements.txt from requirements.in. The lock is compiled on Windows with Python 3.12
# and CI checks that it installs on Linux; pin any Linux-only dependency in requirements.in.
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

# Canonical tables: data/interim/aei_long.parquet and data/processed/regions.csv.
build: fetch
	$(VENV_PY) -m korea_ai_exposure.build

# Replication checks of PLAN 2.4 against the pinned files, as a Markdown table.
replicate: fetch
	$(VENV_PY) -m korea_ai_exposure.replication

# Figures and facts read data/interim/aei_long.parquet, which make build writes.
figures:
	$(VENV_PY) -m korea_ai_exposure.figures

facts:
	$(VENV_PY) -m korea_ai_exposure.facts

# Phase 6 (docs/PLAN.md section 8); until then it fails.
brief:
	@echo "make $@: not implemented yet (see docs/PLAN.md section 8)"; exit 1

all: build figures facts brief
