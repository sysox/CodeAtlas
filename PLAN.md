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

## Phase 5: Prompt & Core Refinement (Complete)

This phase simplified the data bundle sent to the LLM by removing redundant information, making the Machine Core the single source of truth for context.

## Phase 6: Multi-Agent Collaboration & Review (Complete)

This phase introduced a standardized data format and workflow for having one AI agent review the work of another.

## Phase 7: Human-Oriented Review & Documentation (Complete)

This phase focuses on generating concise, human-readable artifacts from AI-generated proposals, enabling efficient human assessment.

## Phase 8: Intelligent Context & Dependency Analysis (Complete)

This phase makes the system truly "intelligent" by automatically discovering and including the context of a change, enabling safe, large-scale refactoring.

## Phase 9: Causal Change Proposals (Complete)

This phase perfects the multi-agent review workflow by ensuring that the relationships between changes are explicitly captured.

## Future Roadmap: Integration with BridgeAI

CodeAtlas is designed to work in tandem with **BridgeAI**, the dedicated execution engine for AI coding agents.

1.  **CodeAtlas (The Intelligence Engine):** Responsible solely for understanding code, generating the Machine Core, and planning changes. It is a pure "sensory" tool.
2.  **BridgeAI (The Execution Engine):** Responsible for communicating with LLMs, estimating costs, applying changes, running tests, and managing the agentic loop.

**Migration Plan:**
*   Migrate `apply.py` (execution logic) to the BridgeAI repository.
*   Migrate `llm.py` (API communication) and cost estimation logic to the BridgeAI repository.
*   Refactor `CodeAtlas` to remove these components, leaving it as a specialized CLI tool consumed by BridgeAI.
