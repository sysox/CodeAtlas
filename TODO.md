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

## Phase 6 (Complete)

- [x] Create `src/codeatlas/proposal.py` to implement the logic for building the `proposal.json`.
- [x] Implement `atlas package-proposal` command in `cli.py`.

## Phase 7 (Complete)

- [x] Create `src/codeatlas/humanize.py` to implement `render_proposal_yaml`.
- [x] Update `atlas package-proposal` in `cli.py` to generate `proposal.yaml`.

## Phase 8 (Complete)

- [x] Create `src/codeatlas/analysis.py` to implement `find_usages`.
- [x] Implement Granular Context Expansion in `compression.py`.
- [x] Integrate dependency analysis into `plan.py`.

## Phase 9 (Complete)

- [x] Implement token estimation and user confirmation prompts in `cli.py`.
- [x] Refactor `proposal.py` to generate hierarchical "Causal Change Proposals".
- [x] Update `humanize.py` to render the new causal structure.

## Future: Integration with BridgeAI

- [ ] Migrate `src/codeatlas/apply.py` logic to the BridgeAI repository.
- [ ] Migrate `src/codeatlas/llm.py` and cost estimation logic to the BridgeAI repository.
- [ ] Refactor `CodeAtlas` to remove these components, finalizing its role as a pure context engine.
