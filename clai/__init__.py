#!/usr/bin/env python

import importlib
import sys

from clai.prompts import BOOL_PROMPT, CLOSING_PROMPT, NOPROSE_PROMPT
from clai.tools import (
    get_backend_instance_config,
    parse_arguments,
    read_config,
    read_stdin,
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

    if bool_prompt:
        prompts.append(BOOL_PROMPT)

    elif no_prose_prompt:
        prompts.append(NOPROSE_PROMPT)

    # prompts.append(CLOSING_PROMPT)
    prompts.append(prompt)

    backend_func = getattr(importlib.import_module("clai.backends"), backend)

    try:
        response = backend_func(
            **backend_config | {"prompts": prompts, "stdin": read_stdin}
        )
    except Exception as err:
        print(f"Failed to process prompt. Reason: f{err}", file=sys.stderr)
        sys.exit(1)

    print(response, file=sys.stdout)

    if bool_prompt:
        exit_codes = {"true": 0, "false": 1, "inconclusive": 2}
        sys.exit(exit_codes.get(response, 3))


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
