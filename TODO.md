# CodeAtlas TODO

This file tracks the immediate next tasks for the project.

## Phase 1 (Complete)

- [x] Update `README.md` to explain the project's vision, goals, and the new documentation files (`PLAN.md`, `TODO.md`).
- [x] Enhance the `atlas plan` command to generate and save a complete, copy-paste-ready prompt file.
- [x] Create the new `atlas apply` command in `cli.py` to validate and execute change packets from a JSON file.
- [x] Ensure `CodeAtlas.json` and `spec/tree.json` are kept in sync after any changes.

## Phase 2 (Complete)

- [x] Create a default `llm_cfg.json` file in `store_init.py` to hold LLM API settings.
- [x] Implement the `--with-llm` flag in the `atlas plan` command to enable direct API calls.
- [x] Add an `--apply` flag to `atlas plan` for a one-shot, fully automated workflow.

## Phase 3 (Complete)

- [x] Create `atlas summarize` command to generate prompts for summarizing symbols.
- [x] Implement `--with-llm` for `atlas summarize` to automate summary generation.
- [x] Create `atlas spec-update` command to inject summaries into `CodeAtlas.json`.

## Phase 4 (Complete)

- [x] Update `src/codeatlas/compression.py` to implement the Generic "Code Tree" model (Pointer/Text/Summary).
- [x] Update `src/codeatlas/plan.py` to use the new generic core structure in prompts.

## Phase 5 (Complete)

- [x] Enhance `compression.py` to include symbol metadata in the Machine Core.
- [x] Refactor `plan.py` to remove redundant symbol information from the plan bundle.
- [x] Update tests to reflect the new leaner bundle structure.
