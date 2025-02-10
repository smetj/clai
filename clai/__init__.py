#!/usr/bin/env python

import importlib
import sys
from clai.prompts import BOOL_PROMPT, CLOSING_PROMPT, NOPROSE_PROMPT
from clai.tools import (
    get_backend_instance_config,
    parse_arguments,
    read_config,
    read_stdin,
    cleanup,
    get_exit_code,
)


def process_prompt(
    prompt: str, bool_prompt: bool, no_prose_prompt, backend, backend_config
) -> None:
    """
    Main function to execute the prompt.

    Args:
        prompt: The user provided prompt for the LLM to process.
        bool_prompt: Append `BOOL_PROMPT` content to `prompt`.
        no_prose_prompt: Append `NOPROSE_PROMPT` content to `prompt`.
        backend: The LLM backend function name to import and execute.
        backend_config: The `backend` function variables.
    """
    prompts = []
    response_format = None

    if bool_prompt:
        response_format = {
            "type": "json_schema",
            "json_schema": {
                "name": "true_false",
                "schema": {
                    "type": "object",
                    "properties": {
                        "answer": {
                            "type": "boolean",
                        },
                        "reason": {"type": "string"},
                    },
                    "required": ["answer", "reason"],
                    "additionalProperties": False,
                },
                "strict": True,
            },
        }
        prompts.append(cleanup(BOOL_PROMPT))

    elif no_prose_prompt:
        prompts.append(cleanup(NOPROSE_PROMPT))

    prompts.append(cleanup(CLOSING_PROMPT))
    prompts.append(prompt)

    backend_func = getattr(importlib.import_module("clai.backends"), backend)

    try:
        response = backend_func(
            **backend_config
            | {
                "prompts": prompts,
                "stdin": read_stdin,
                "response_format": response_format,
            }
        )
    except Exception as err:
        print(f"Failed to process prompt. Reason: f{err}", file=sys.stderr)
        sys.exit(1)

    print(response, file=sys.stdout)

    if bool_prompt:
        sys.exit(get_exit_code(response))


def main():
    try:
        args = parse_arguments()
        config = read_config(args.config)
        backend_config = get_backend_instance_config(
            config=config, backend=args.backend, instance=args.instance
        )

        process_prompt(
            prompt=args.prompt,
            bool_prompt=args.bool,
            no_prose_prompt=args.no_prose,
            backend=args.backend,
            backend_config=backend_config,
        )
    except Exception as err:
        print(f"Failed to execute command. Reason: {err}")
        sys.exit(1)


if __name__ == "__main__":
    main()
