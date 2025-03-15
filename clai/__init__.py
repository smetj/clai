#!/usr/bin/env python

import importlib
import sys
from clai.tools import (
    get_backend_instance_config,
    parse_arguments,
    read_config,
    read_stdin,
    cleanup,
    get_exit_code,
)


def process_prompt(
    prompt: str, bool_prompt: bool, debug: bool, backend, backend_config
) -> None:
    """
    Main function to execute the prompt.

    Args:
        prompt: The user provided prompt for the LLM to process.
        bool_prompt: Append `BOOL_PROMPT` content to `prompt`.
        backend: The LLM backend function name to import and execute.
        backend_config: The `backend` function variables.
    """
    prompts = [prompt]

    backend_func = importlib.import_module(f"clai.backend.{backend}").prompt

    try:
        response = backend_func(
            **backend_config
            | {
                "prompts": prompts,
                "stdin": read_stdin,
                "debug": debug,
                "bool_prompt": bool_prompt,
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
            debug=args.debug,
            backend=args.backend,
            backend_config=backend_config,
        )

    except Exception as err:
        print(f"Failed to execute command. Reason: {err}")
        sys.exit(1)


if __name__ == "__main__":
    main()
