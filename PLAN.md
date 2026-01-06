# CodeAtlas Implementation Plan

This document outlines the phased development plan for CodeAtlas. The goal is to create a system for AI-driven code understanding and modification based on a structured, reversible representation of the codebase.

## Phase 1: Solidify the Foundation & Manual Workflow (Complete)

This phase focused on making the existing tools robust and refining the human-driven, copy-paste workflow.

## Phase 2: Introduce Optional LLM Integration (Complete)

This phase made the process smoother for users by adding optional, direct integration with LLM APIs.

## Phase 3: Automated Summarization (Complete)

This phase made the system self-describing by creating tools to automatically generate and inject summaries into the project's specification.

## Phase 4: Implement the Generic "Code Tree" Model (Complete)

This phase refactored the "Machine Core" to be a truly generic and flexible representation of the codebase, optimizing it for advanced AI interaction.

## Phase 5: Prompt & Core Refinement

This phase will simplify the data bundle sent to the LLM by removing redundant information, making the Machine Core the single source of truth for context.

1.  **Enhance Machine Core:** Update `compression.py` to include metadata (like line numbers) for symbol nodes directly within the compressed output.
2.  **Refactor Plan Bundle:** Remove the now-redundant `py_symbols_by_path` and `symbol_snippets` sections from the output of the `atlas plan` command.
3.  **Simplify Prompt:** Update the prompt generation logic in `plan.py` to rely exclusively on the unified Machine Core for all structural and content context.
4.  **Update Tests:** Adjust tests to align with the new, leaner plan bundle structure.
