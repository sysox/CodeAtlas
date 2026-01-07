# CodeAtlas

CodeAtlas is a system for creating and maintaining a structured, reversible description of a codebase. It serves as a two-way bridge between human intent and source code, designed to be driven by Large Language Models (LLMs).

## Core Concept: The Intelligence Engine

CodeAtlas acts as the "Sensory System" for AI coding agents. Its primary job is to **understand** a codebase and present it in a format that LLMs can process efficiently and cheaply.

It achieves this through:
1.  **Deep Indexing:** Parsing code to build a hierarchical tree of files, classes, and functions.
2.  **Machine Core:** Generating a compressed, token-efficient JSON representation of the project structure.
3.  **Intelligent Context:** Automatically finding dependencies and "hydrating" only the relevant parts of the code into the context for a specific task.

## Getting Started on a New Project

You do not need to write a specification manually. CodeAtlas generates it from your code.

1.  **Initialize:**
    ```bash
    atlas init
    ```
    Creates the `.atlas` directory.

2.  **Index:**
    ```bash
    atlas index
    ```
    Scans your project and builds the deep symbol tree.

3.  **Summarize (Optional but Recommended):**
    ```bash
    atlas summarize --with-llm
    atlas spec-update
    ```
    Uses an LLM to generate summaries for every symbol and injects them into `CodeAtlas.json`.

## Workflow

### 1. Planning & Context Generation
The `atlas plan` command is the heart of the system. It takes a high-level goal and a target file/symbol.

```bash
atlas plan --goal "Refactor the login logic" --target "src/auth.py"
```

It outputs:
*   `bundle.json`: A complete, machine-readable context bundle.
*   `prompt.txt`: A ready-to-paste prompt containing the Machine Core and the user's goal.

### 2. Multi-Agent Review
To have a second AI review a proposed change:

```bash
atlas package-proposal --bundle .atlas/runs/.../bundle.json --packet change_packet.json
```

This generates:
*   `proposal.json`: A machine-readable packet linking primary changes to their dependencies.
*   `proposal.yaml`: A human-readable dashboard for quick assessment.

### 3. Execution
To apply the changes:

```bash
atlas apply change_packet.json
```

## Using CodeAtlas in Other Projects (Bootstrapping)

If you are building an agent (like **BridgeAI**) that uses `CodeAtlas` as a library, you need to teach that agent how `CodeAtlas` works.

1.  **Generate the CodeAtlas Core:**
    Run this command *inside the CodeAtlas repository*:
    ```bash
    atlas export-core > codeatlas_core.json
    ```

2.  **Feed it to the Agent:**
    Provide `codeatlas_core.json` as context to your agent. This file contains the compressed structure, function signatures, and docstrings of the entire `CodeAtlas` library. It allows the agent to write valid code using `codeatlas` functions without needing to read the source files.

## Installation

CodeAtlas is a standard Python package.

```bash
# Build the wheel
pip install build
python -m build

# Install in another project
pip install /path/to/CodeAtlas/dist/codeatlas-0.1.0-py3-none-any.whl
```

## Documentation

*   [PLAN.md](PLAN.md): Detailed engineering roadmap and migration plan.
*   [TODO.md](TODO.md): Current task tracking.
