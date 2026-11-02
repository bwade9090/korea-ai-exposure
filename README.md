# korea-ai-exposure

Where AI is used, and where AI-exposed work sits, across Korea's 17 metropolitan cities and
provinces. Measured from public data: the Anthropic Economic Index, occupational exposure scores
(ILO; Anthropic), and Korean official statistics.

**Brief:** *Regional Patterns of Generative AI Use in Korea: Evidence from Claude Conversation
Data* (November 2026) — [PDF](report/brief.pdf), [Word](report/brief.docx). Detailed methods:
[`report/methodology.md`](report/methodology.md).

## Questions

1. How does Korea's Claude.ai usage compare with peer economies?
2. How is usage distributed across Korea's regions, relative to population and employment?
3. How much of the regional pattern does occupational composition account for, and how does usage
   compare with exposure?

## Reproducibility

`make all` regenerates every figure and number from pinned public sources. Small inputs are
stored in `data/raw/`; the large Anthropic Economic Index files are downloaded by `make fetch`.
Every number in the brief is a fact in [`outputs/facts.json`](outputs/facts.json), with its unit,
period and sources; `python -m korea_ai_exposure.brief` rebuilds `report/brief.docx` from the
facts and figures, and the PDF is exported from Word.

- Sources, versions, and licenses: [`docs/DATA_SOURCES.md`](docs/DATA_SOURCES.md)
- Plan: [`docs/PLAN.md`](docs/PLAN.md)

## Development

Requires Python 3.12, GNU Make, and a POSIX shell (Git Bash on Windows).

```sh
make setup   # create .venv with the pinned, hash-checked environment
make check   # ruff lint, ruff format check, offline tests
make fetch   # download the pinned public files into data/raw/ and verify their checksums
make build   # canonical tables (fetches first)
make replicate   # recompute published values from the pinned files and compare
make figures && make facts   # figures, tables and the facts sheet in outputs/
```

If `make setup` cannot find Python 3.12, pass the interpreter: `make setup PYTHON=/path/to/python3.12`.
Copy `.env.example` to `.env` for the KOSIS API key and the BLS User-Agent; `.env` is never
committed. See [`data/README.md`](data/README.md) for how downloads are pinned.

## Attribution and disclaimer

This project uses data from the Anthropic Economic Index (Anthropic; CC-BY) and the other public
sources listed, with their licences, in [`docs/DATA_SOURCES.md`](docs/DATA_SOURCES.md). It is
independent research, not affiliated with or endorsed by Anthropic, the Bank of Korea or any other
institution; the views are the author's own.
