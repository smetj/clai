# MIT License
#
# Copyright (c) 2025 Jelle Smet
#
# This software is released under the MIT License.
# See the LICENSE file in the project root for more information.

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
                prompt_str = args.prompt
                stdin_lines = list(read_stdin())
                if not prompt_str and stdin_lines:
                    prompt_str = "".join(stdin_lines).strip()
                if not prompt_str:
                    print("No prompt provided via argument or stdin.")
                    sys.exit(1)
                print(client.prompt(prompt=prompt_str, stdin=lambda: iter(stdin_lines)))
            case "bool":
                prompt_str = args.prompt
                stdin_lines = list(read_stdin())
                if not prompt_str and stdin_lines:
                    prompt_str = "".join(stdin_lines).strip()
                if not prompt_str:
                    print("No prompt provided via argument or stdin.")
                    sys.exit(1)
                exit_code, response = client.bool_prompt(
                    prompt=prompt_str, stdin=lambda: iter(stdin_lines)
                )
                print(response)
                sys.exit(exit_code)
    except Exception as err:
        print(f"Failed to execute command. Reason: {err}")
        sys.exit(1)


if __name__ == "__main__":
    main()
