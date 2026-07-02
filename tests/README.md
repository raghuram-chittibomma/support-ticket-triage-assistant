# tests/

Pytest unit and integration tests for the runtime application in `src/`.

Structure mirrors `src/`: `tests/schemas/`, `tests/services/`, etc. Test files are added alongside the runtime component they cover, per `docs/02_testing/TEST_STRATEGY.md`. Every implementation PR is expected to add or update tests here (see Definition of Done).

Run with `.venv\Scripts\python.exe -m pytest` from the repo root (see `docs/03_operations/RUNBOOK.md`).
