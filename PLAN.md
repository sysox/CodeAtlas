# CodeAtlas Implementation Plan

This document outlines the phased development plan for CodeAtlas. The goal is to create a system for AI-driven code understanding and modification based on a structured, reversible representation of the codebase.

## Phase 1: Solidify the Foundation & Manual Workflow

This phase focuses on making the existing tools robust and refining the human-driven, copy-paste workflow. This provides immediate value without incurring any LLM API costs.

1.  **Create Core Documentation:**
    *   Create `PLAN.md` (this file) to house the detailed roadmap.
    *   Create `TODO.md` to track immediate tasks.
    *   Update `README.md` to explain the project's vision, goals, and core workflow.

2.  **Enhance `atlas plan` Command:**
    *   The command will generate the full, ready-to-use prompt text for the user.
    *   It will save this prompt to a file (e.g., `.atlas/runs/YYYYMMDD_HHMMSS/prompt.txt`).
    *   After running, it will print clear instructions for the user to copy the prompt, paste it into an LLM, and save the resulting JSON response.

3.  **Create `atlas apply` Command:**
    *   This new command in `cli.py` will accept a path to a "change packet" JSON file.
    *   It will validate the packet against a schema to ensure it's well-formed.
    *   It will then execute the operations in the packet (e.g., `replace_symbol`, `replace_file`), modifying the code.
    *   This command automates the tedious and error-prone part of manually applying LLM-suggested changes.

## Phase 2: Introduce Optional LLM Integration

This phase makes the process smoother for users who are willing to use an LLM API.

1.  **Add `--with-llm` Flag to `atlas plan`:**
    *   When this flag is present, the command will send the generated prompt to a configured LLM API.
    *   This will require a new configuration file (e.g., `.atlas/llm_cfg.json`) for API keys, endpoints, and model choices.
    *   The command will save the LLM's JSON response directly to the run directory (e.g., `response.json`).

2.  **Integrate `apply` for a One-Shot Workflow:**
    *   Add an `--apply` flag to the `atlas plan` command.
    *   When used with `--with-llm`, it will automatically call the `apply` logic on the `response.json` it just received.
    *   This creates a powerful, one-shot command for fully automated code modification: `atlas plan --target "src/codeatlas/cli.py" --with-llm --apply`.

## Phase 3: Automated Summarization (The "Inverse Operation")

This is the most advanced phase, where the system becomes self-describing and truly achieves the vision of reversible "code-to-spec" and "spec-to-code" operations.

1.  **Create `atlas summarize` Command:**
    *   This command will iterate through every file and symbol (function/class) in the project.
    *   For each symbol, it will generate a prompt asking for a concise summary.
    *   **Default (Manual) Workflow:** It will create a directory (`.atlas/summaries/`) containing one text file per symbol, each with a ready-to-paste prompt. The user can then fill in the summaries manually or by using a web UI.
    *   **Optional LLM Workflow:** An `--with-llm` flag will automate this process, making API calls for each symbol to fetch the summary.

2.  **Create `atlas spec-update` Command:**
    *   This command will read all the generated summaries from `.atlas/summaries/`.
    *   It will inject these summaries into the `summary` fields of the corresponding nodes in `CodeAtlas.json` and `spec/tree.json`.
    *   This final step makes the project's structured description complete and allows the spec to be used for high-fidelity code regeneration.
