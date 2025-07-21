## What

This pull request refactors the codebase to remove redundant comments, unused imports, and simplifies code across the `clai` project files.

- Removed unused imports and unnecessary docstrings.
- Simplified exception handling and removed unreachable code.
- Cleaned up argument parsing and configuration loading logic.
- Ensured all modules are free of dead code and follow best practices.

## Why

These changes improve code readability, maintainability, and reduce technical debt. By eliminating unused code and redundant comments, the codebase becomes easier to understand and less error-prone. This also helps future contributors quickly grasp the core logic and reduces the risk of bugs related to legacy or dead code.
## What

This PR adds support for the `structured` command to the CLI, enabling users to request structured responses from LLM backends (OpenAI, Azure OpenAI, and Mistral) using a user-supplied JSON schema. The implementation includes:
- CLI argument parsing for the `structured` subcommand and `--schema` argument.
- Backend support for OpenAI, Azure OpenAI, and Mistral to validate and use the provided JSON schema for response formatting.
- Tests to validate the structured command for OpenAI.
- Documentation in the README with usage examples and schema samples.

## Why

Structured output is essential for downstream automation, validation, and integration with other tools. By allowing users to specify a JSON schema, the CLI can enforce response structure, making it easier to consume and validate LLM outputs programmatically. This feature increases the flexibility and reliability of the CLI for advanced workflows and automation scenarios.
