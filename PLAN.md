# CodeAtlas Implementation Plan

This document outlines the phased development plan for CodeAtlas. The goal is to create a system for AI-driven code understanding and modification based on a structured, reversible representation of the codebase.

## Phase 1: Solidify the Foundation & Manual Workflow (Complete)

This phase focused on making the existing tools robust and refining the human-driven, copy-paste workflow.

## Phase 2: Introduce Optional LLM Integration (Complete)

This phase made the process smoother for users by adding optional, direct integration with LLM APIs.

## Phase 3: Automated Summarization (Complete)

This phase made the system self-describing by creating tools to automatically generate and inject summaries into the project's specification.

## Phase 4: Implement the Generic "Code Tree" Model

This phase will refactor the "Machine Core" to be a truly generic and flexible representation of the codebase, optimizing it for advanced AI interaction.

1.  **Define Generic Node Content:** Evolve the Machine Core format so that any node can represent its content in multiple ways:
    *   **Pointer:** A reference to a file on disk (`{ "type": "pointer", "path": "..." }`).
    *   **Inline Text:** The actual source code contained directly within the node (`{ "type": "text", "content": "..." }`).
    *   **Summary:** A natural language description (`{ "type": "summary", "text": "..." }`).

2.  **Create a "View Layer":** Update `compression.py` to act as a "View Layer". It will read the current pointer-based storage (`nodes.jsonl`) and transform it into this new, generic "Code Tree" format for the LLM. This gives us the benefits of the new model without a disruptive storage-layer refactor.

3.  **Integrate the New Core:** Update the `plan.py` module to understand and render this new, richer Machine Core structure within the LLM prompt, ensuring the AI can leverage the flexible content types.
