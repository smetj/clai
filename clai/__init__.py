#!/usr/bin/env python

import importlib
import sys

from clai.tools import (cleanup, get_backend_instance_config, get_exit_code,
                        parse_arguments, read_config, read_stdin)


def process_prompt(
    prompt: str | None, bool_prompt: bool, debug: bool, backend, backend_config
) -> None:
    """
    Main function to execute the prompt.

    Args:
        prompt: The user provided prompt for the LLM to process.
        bool_prompt: Append `BOOL_PROMPT` content to `prompt`.
        backend: The LLM backend function name to import and execute.
        backend_config: The `backend` function variables.
    """
    prompts = []

    if prompt is not None:
        prompts = [prompt]
    else:
        if sys.stdin.isatty():
            raise Exception("No prompt input to process from either --prompt or STDIN.")
            sys.exit(1)

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

    if bool_prompt:
        exit_code = get_exit_code(response)
    else:
        exit_code = 0

    print(response, file=sys.stdout)
    sys.exit(exit_code)


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
