# Project Overview

## Modules

### `debug_index.py`

### `src/codeatlas/__init__.py`

### `src/codeatlas/analysis.py`

| Symbol | Type | Description |
|---|---|---|
| `find_usages_with_grep` | function | The function 'find_usages_with_grep' searches for occurrences of a specified symbol in a given directory using grep and returns a list of dictionaries, each containing the file path, line number, and code line where the symbol is found. |

### `src/codeatlas/apply.py`

| Symbol | Type | Description |
|---|---|---|
| `SymbolReplacer` | class | SymbolReplacer is a LibCST transformer class that replaces a specified class or function definition identified by its qualified name with new code provided as input. |
| `apply_with_cst` | function | Replaces a specified symbol in source code using LibCST and returns the modified code and a success flag. |
| `run_command` | function | Executes a shell command in a given directory and returns a dictionary containing the command, its exit code, standard output, and error output. |
| `apply_change_packet` | function | The `apply_change_packet` function applies changes described in a JSON packet to files in a given directory, executes specified command-line operations, and performs Git operations, returning a detailed dictionary of results and statuses. |

### `src/codeatlas/cli.py`

| Symbol | Type | Description |
|---|---|---|
| `main` | function | The `main` function is a command-line interface handler for a tool named 'atlas', using argparse to parse various subcommands that perform actions like initializing a workspace, indexing, diffing, grepping code snippets, resolving nodes, exporting data, and generating project overviews, returning an exit status code based on execution success or failure. |

### `src/codeatlas/compression.py`

| Symbol | Type | Description |
|---|---|---|
| `compress_node` | function | Converts a node dictionary to a compressed format for a generic code tree, taking inputs of a node, optional root path, and expansion flag, and outputs a transformed dictionary with compressed type, children, summary, meta information, and content data. |
| `build_machine_core` | function | Generates a compressed 'Machine Core' representation of a project by processing nodes and optionally expanding specific node IDs from a given root path, returning a dictionary with versioning and node data. |

### `src/codeatlas/ctx.py`

| Symbol | Type | Description |
|---|---|---|
| `_cap_bytes` | function | The _cap_bytes function truncates a UTF-8 encoded string to a specified maximum byte length, ensuring valid encoding and indicating if truncation occurred. |
| `_slice_lines` | function | Slices a string into head and tail segments based on line count and returns the concatenated result with an ellipsis in between, along with a boolean indicating if any lines were omitted. |
| `build_ctx` | function | The 'build_ctx' function generates a JSON-serializable context bundle for LLMs by resolving node IDs from specified paths, optionally including content with limits specified by 'head', 'tail', and 'max_bytes', and returns a dictionary containing the results and errors encountered. |

### `src/codeatlas/diff.py`

| Symbol | Type | Description |
|---|---|---|
| `compute_diff` | function | Computes the difference between old and new file fingerprints in a directory, taking a root path as input and returning a dictionary with total file count and differences. |

### `src/codeatlas/fingerprint.py`

| Symbol | Type | Description |
|---|---|---|
| `fingerprint_file` | function | Generates a SHA-256 hash fingerprint for a file given its path, returning the hash as a hexadecimal string. |
| `build_fingerprints` | function | Generates a dictionary of file fingerprints for given relative paths using a specified root directory. |
| `diff_fingerprints` | function | Compares two dictionaries representing 'fingerprints' and returns a dictionary detailing keys added, deleted, changed, or unchanged between them. |

### `src/codeatlas/grep.py`

| Symbol | Type | Description |
|---|---|---|
| `grep_snippets` | function | The function 'grep_snippets' searches for lines matching a regex pattern within a file, returning a dictionary with context lines, match details, and metadata about the search operation. |

### `src/codeatlas/humanize.py`

| Symbol | Type | Description |
|---|---|---|
| `_generate_diff` | function | Generates a unified diff string comparing two text versions, taking 'before' and 'after' strings and a 'filename' as inputs, and returning the diff as a string. |
| `_render_changes_to_yaml` | function | Renders a list of file changes into a structured YAML format by categorizing changes by file paths and appending their details to a given list of strings. |
| `render_proposal_yaml` | function | Generates a human-readable YAML report summarizing the goal, file impact, and changes from a causal proposal packet, taking a dictionary as input and outputting a string. |
| `render_project_cheatsheet` | function | Generates a YAML cheatsheet detailing the project structure from a hierarchical node representation, outlining files and, at higher levels, their classes and functions, returning a formatted string. |

### `src/codeatlas/index.py`

| Symbol | Type | Description |
|---|---|---|
| `_kind_from_path` | function | Determines the file type based on the file extension of the given relative path, returning a string representing the file type. |
| `build_or_update` | function | The function 'build_or_update' indexes the entire workspace by analyzing files and parsing symbols to create a hierarchical node structure, taking a root directory as input and returning a dictionary with indexing outcomes and file changes. |

### `src/codeatlas/layout.py`

| Symbol | Type | Description |
|---|---|---|
| `AtlasPaths` | class | The AtlasPaths class represents a directory structure for an 'atlas' with properties to access various subdirectories and files, and a method to ensure those directories exist, taking a root Path as input and outputting corresponding Path objects for the files and directories. |

### `src/codeatlas/llm.py`

| Symbol | Type | Description |
|---|---|---|
| `_call_openai` | function | Sends a prompt to an OpenAI API using specified configuration and API key, returning the parsed response content or an error message if the request fails. |
| `_call_gemini` | function | Sends a prompt to Google's Gemini API using a specified model and configuration, returning a parsed JSON response or an error message. |
| `call_llm_api` | function | Calls a specified LLM API ('openai' or 'gemini') with a prompt using configuration details and returns the API's JSON response. |

### `src/codeatlas/model.py`

| Symbol | Type | Description |
|---|---|---|
| `Node` | class | The Node class represents a tree-like structure element with attributes like id, type, path, and optional anchor, summary, children, and metadata, providing methods to convert between Node instances and their dictionary representations. |
| `make_id` | function | Generates a deterministic ID string based on kind, relative path, and an optional anchor. |

### `src/codeatlas/overview.py`

| Symbol | Type | Description |
|---|---|---|
| `render_human_overview` | function | The `render_human_overview` function generates a Markdown overview of a project's structure and components based on a hierarchical dictionary input (machine_core), detailing modules, files, and their summaries for human readers. |

### `src/codeatlas/patch_skel.py`

| Symbol | Type | Description |
|---|---|---|
| `patch_skeleton` | function | Generates a packet skeleton for a BridgeAI operation to modify code, taking inputs such as file path, optional qualified name, operation type, test commands, and commit message, and outputs a dictionary detailing the operation and associated metadata. |

### `src/codeatlas/plan.py`

| Symbol | Type | Description |
|---|---|---|
| `Target` | class | Represents a file path and an optional qualified name identifier. |
| `parse_target` | function | Parses a string input to extract a file path and an optional qualified name, returning a Target object with path and qualname attributes. |
| `build_plan` | function | Creates a backward-compatible execution plan for a single target using provided parameters for file path, operation, and optional execution details, outputting a dictionary of plan specifications. |
| `build_plan_multi` | function | The 'build_plan_multi' function creates an intelligent context bundle for a large language model by expanding relevant context from specified targets and returns details of target paths, goals, and processing instructions as a dictionary. |
| `render_prompt_text` | function | Generates a text prompt for a language model by formatting a JSON bundle, containing project context and a task skeleton, according to a specified goal. |

### `src/codeatlas/proposal.py`

| Symbol | Type | Description |
|---|---|---|
| `build_proposal_packet` | function | The function 'build_proposal_packet' generates a self-contained review packet based on JSON input files for a bundle and a packet, identifying and categorizing changes as primary or dependent, and returns details in a structured dictionary. |

### `src/codeatlas/py_enrich.py`

| Symbol | Type | Description |
|---|---|---|
| `get_annotation` | function | The function `get_annotation` recursively converts an AST node representing a type annotation into its corresponding string representation. |
| `EnrichmentVisitor` | class | EnrichmentVisitor is a custom AST NodeVisitor class that analyzes Python code to record function call names, identify read and write variable operations, and detect potential side effects related to file system, subprocess, network, git, and database operations. |
| `enrich_symbol` | function | Analyzes an Abstract Syntax Tree (AST) node for a function or class to extract detailed metadata including its signature, docstring, calls, variable accesses, and side effects, returning a dictionary with this information. |

### `src/codeatlas/py_extract.py`

| Symbol | Type | Description |
|---|---|---|
| `extract_qualname_source` | function | Extracts and returns the source code snippet of a specified qualified name from a Python file, including optional context lines, as a dictionary with metadata. |

### `src/codeatlas/py_symbols.py`

| Symbol | Type | Description |
|---|---|---|
| `Sym` | class | The Sym class represents a Python code symbol with attributes for its name, type, and position in the code, and provides a method to return this information as a dictionary. |
| `_Visitor` | class | The _Visitor class traverses an abstract syntax tree (AST) to collect and store fully-qualified names and details of class and function definitions in a list, using node attributes such as name and line numbers. |
| `list_python_symbols` | function | Returns a list of dictionaries containing Python symbols with their qualified names and line spans from the specified file path. |
| `parse_symbols` | function | Parses a Python file at the given path into abstract syntax trees (ASTs) and returns a sorted list of Sym objects with attached AST nodes. |

### `src/codeatlas/resolve.py`

| Symbol | Type | Description |
|---|---|---|
| `lookup_path` | function | Finds and returns the value mapped to a relative path from a JSON index where the root directory is resolved as an absolute path, or None if not found. |
| `resolve_node` | function | Resolves and returns a dictionary representation of a node with a given ID from a nodes map file located at a specified root path. |
| `resolve_content` | function | The function 'resolve_content' retrieves the entire text of a file specified by a node_id in the format 'ref:path:<relpath>' relative to a given root directory, returning the file content as a string. |

### `src/codeatlas/scan.py`

| Symbol | Type | Description |
|---|---|---|
| `_match_any` | function | Determines if a given POSIX path matches any pattern in an iterable using Unix shell-style wildcards, returning a boolean result. |
| `scan_files` | function | The function 'scan_files' returns a stable sorted list of relative POSIX paths for files within a specified root directory that match inclusion patterns and do not match exclusion patterns. |

### `src/codeatlas/skeleton.py`

| Symbol | Type | Description |
|---|---|---|
| `render_llm_skeleton` | function | Renders a detailed, token-efficient overview of a project's structure for large language models by traversing a dictionary-based representation of the project to include file signatures, structural code blocks, and basic I/O details, returning it as a formatted string. |

### `src/codeatlas/state.py`

| Symbol | Type | Description |
|---|---|---|
| `load_json` | function | Reads a JSON file from a given path and returns its contents, or a default value if the file does not exist or is empty. |
| `write_json` | function | The 'write_json' function writes a given Python object to a JSON file at the specified path, creating necessary directories if they don't exist. |
| `load_nodes_jsonl` | function | Reads a JSONL file from the given Path object and returns a list of dictionaries representing each JSON line. |
| `load_nodes_map` | function | Converts a JSON Lines file of node data from the given path into a dictionary mapping node IDs to their respective data, filtering for nodes with string IDs. |
| `write_nodes_jsonl` | function | Writes a list of dictionary nodes to a JSONL file at the specified path, creating any necessary parent directories. |

### `src/codeatlas/store_init.py`

| Symbol | Type | Description |
|---|---|---|
| `init_workspace` | function | Initializes a workspace by creating required directories and default configuration files in a specified root path, returning an AtlasPaths object reflecting the new setup. |

### `src/codeatlas/summarize.py`

| Symbol | Type | Description |
|---|---|---|
| `generate_summary_prompt` | function | Generates a template for requesting a one-sentence summary of a Python symbol's purpose, inputs, and outputs, using the provided symbol name and code. |
| `summarize_symbols` | function | Generates summaries for indexed symbol nodes in a given root directory, optionally using an LLM API to produce summaries or saving prompt files, based on paths and configuration files provided as inputs, and outputs a dictionary with results and status. |
| `update_spec_with_summaries` | function | Updates the CodeAtlas.json and nodes.jsonl files with summaries from the summaries directory, using the specified root path as input and returning a dictionary indicating success and number of updates made. |

### `tests/test_apply.py`

| Symbol | Type | Description |
|---|---|---|
| `test_apply_replace_symbol` | function | Tests the `apply_change_packet` function by verifying it correctly replaces the Python function `my_function` in a file with new code specified in a change packet, while ensuring other code remains unchanged. |
| `test_apply_replace_nested_symbol` | function | Tests the application of a change packet that replaces a method in a Python class within a temporary directory, by verifying the replacement in the code file and confirming successful execution. |
| `test_apply_multiple_replacements` | function | Tests the 'apply_change_packet' function by replacing multiple functions in a Python file with new code snippets, ensuring successful application and correct file content updates, taking 'tmp_path' as input and producing verification results. |

### `tests/test_ctx.py`

| Symbol | Type | Description |
|---|---|---|
| `test_ctx_returns_items_and_content` | function | Tests that the build_ctx function correctly returns items with file path and partial content from a text file, using a temporary path setup. |
| `test_ctx_max_bytes_truncates` | function | Tests that the build_ctx function correctly truncates file content exceeding the specified max_bytes parameter. |

### `tests/test_diff.py`

| Symbol | Type | Description |
|---|---|---|
| `test_diff_added_changed_deleted` | function | Tests the 'compute_diff' function by verifying its ability to detect added, changed, and deleted files in a temporary directory. |

### `tests/test_grep.py`

| Symbol | Type | Description |
|---|---|---|
| `test_grep_snippets_basic` | function | Tests the grep_snippets function to verify it correctly finds and returns snippets matching a pattern with context from a text file. |
| `test_grep_invalid_regex` | function | Tests the behavior of grep_snippets function when given an invalid regular expression pattern, verifying it returns an 'ok': False result. |

### `tests/test_index_basic.py`

| Symbol | Type | Description |
|---|---|---|
| `test_index_creates_paths_index_and_meta` | function | Tests that the indexing function creates correct path index and metadata for files in a temporary directory, verifying that the files are indexed correctly with appropriate metadata including type, path, and hash. |

### `tests/test_init.py`

| Symbol | Type | Description |
|---|---|---|
| `test_init_creates_atlas_layout` | function | Tests the init_workspace function to ensure it creates the necessary directory and file structure for the atlas layout within a temporary path. |

### `tests/test_patch_skel.py`

| Symbol | Type | Description |
|---|---|---|
| `test_patch_skeleton_replace_symbol` | function | Tests the patch_skeleton function to ensure it correctly specifies a replace_symbol operation for the method 'A.m' in the file 'x.py'. |
| `test_patch_skeleton_replace_file` | function | Tests if the 'patch_skeleton' function correctly generates a patch operation to replace a file, verifying the 'replace_file' operation and checking if 'content' is included. |

### `tests/test_plan.py`

| Symbol | Type | Description |
|---|---|---|
| `test_plan_includes_machine_core_and_patch` | function | This function tests whether a build system includes both machine core and patch details when replacing a function in a Python file, by verifying the output structure of a build plan after performing symbolic updates. |

### `tests/test_plan_multi.py`

| Symbol | Type | Description |
|---|---|---|
| `test_plan_multi_two_targets` | function | Tests the multi-target build plan functionality by checking that specified Python files and README are processed correctly and verifying the outputs and transformations including symbol replacement and patch operations. |

### `tests/test_py_extract.py`

| Symbol | Type | Description |
|---|---|---|
| `test_extract_qualname_source` | function | Tests the extract_qualname_source function to ensure it retrieves source code for specified qualified names from a Python file written to a temporary path. |

### `tests/test_py_symbols.py`

| Symbol | Type | Description |
|---|---|---|
| `test_py_symbols_basic` | function | This function tests the list_python_symbols function by creating a temporary Python file with a class and a function, and asserts that their qualified names are correctly identified. |

### `tests/test_resolve.py`

| Symbol | Type | Description |
|---|---|---|
| `test_resolve_returns_file_content` | function | Verifies that a file's content can be correctly resolved using its node ID after setting up and updating a temporary workspace with the file. |

### `tests/test_smoke.py`

| Symbol | Type | Description |
|---|---|---|
| `test_import` | function | Checks if the 'codeatlas' module can be imported by asserting its version attribute. |

