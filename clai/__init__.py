#!/usr/bin/env python

import importlib
import sys

from clai.tools import (
    get_backend_instance_config,
    parse_arguments,
    read_config,
    read_stdin,
)


def main() -> None:
    try:
        args = parse_arguments()
        backend_config = get_backend_instance_config(
            config=read_config(args.config),
            backend=args.backend,
            instance=args.instance,
        )
        Client = getattr(
            importlib.import_module(f"clai.backend.{args.backend}"), "Client"
        )
        client = Client(**backend_config._asdict() | {"debug": args.debug})

        match args.command:
            case "prompt":
                print(client.prompt(prompt=args.prompt, stdin=read_stdin))
            case "bool":
                exit_code, response = client.bool_prompt(
                    prompt=args.prompt, stdin=read_stdin
                )
                print(response)
                sys.exit(exit_code)
    except Exception as err:
        print(f"Failed to execute command. Reason: {err}")
        sys.exit(1)


if __name__ == "__main__":
    main()
