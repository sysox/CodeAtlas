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

## Phase 6: Multi-Agent Collaboration & Review

This phase introduces a standardized data format and workflow for having one AI agent review the work of another.

1.  **Define "Change Proposal Packet":** Create a new, self-contained JSON format (`proposal.json`) that includes the user's goal, the "before" code snippet, and the "after" code snippet. This packet is the unit of exchange for reviews.
2.  **Implement `atlas package-proposal` Command:** Create a new CLI command that takes the original context bundle and the first AI's change packet, and packages them into the standardized `proposal.json` for review.
3.  **Establish Review Workflow:** Document the end-to-end process for multi-agent collaboration, enabling efficient and flexible reviews.
