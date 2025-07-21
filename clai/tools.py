#
#  tools.py
#

import argparse
import json
import os
import sys
from collections import namedtuple
from textwrap import dedent
from typing import Any, Dict, Iterator

import yaml
from clai.backend import SUPPORTED_BACKENDS
from jsonschema import validate


def cleanup(text: str) -> str:
    """
    Normalize the given multi-line text by dedenting and collapsing line breaks into spaces.

    Args:
        text (str): The text to clean up.

    Returns:
        str: The cleaned text.
    """
    return dedent(text).replace("\n", " ")


def validate_bool_response(response: str) -> Dict[str, Any]:
    """
    Parse and validate a JSON-formatted boolean response against the expected schema.

    Args:
        response (str): The raw JSON string returned by the model.

    Returns:
        dict: The parsed JSON object containing 'reason' and 'answer'.

    Exits:
        Exits the process with code 3 if validation fails.
    """
    try:
        json_response = json.loads(response)
        validate(
            json_response,
            {
                "$schema": "https://json-schema.org/draft/2020-12/schema",
                "type": "object",
                "properties": {
                    "reason": {"type": "string"},
                    "answer": {"type": "boolean"},
                },
                "required": ["reason", "answer"],
                "additionalProperties": False,
            },
        )
    except Exception as _:
        print(
            "Invalid response format received. Does the model support structured output?"
        )
        sys.exit(3)

    return json_response


def get_exit_code(response: str) -> int:
    """
    Determine the exit code based on the boolean answer field in the response.

    Args:
        response (str): The raw JSON string representing the structured response.

    Returns:
        int: Returns 0 if answer is True, 1 otherwise.
    """
    json_response = validate_bool_response(response)

    if json_response["answer"]:
        return 0
    else:
        return 1


def read_config(filename: str) -> dict[str, Any]:
    """
    Load a YAML configuration file from the given path.

    Args:
        filename (str): Path to the YAML config file (tilde-expansion supported).

    Returns:
        dict: Parsed configuration dictionary.
    """

    with open(os.path.expanduser(filename)) as filename_fh:
        return yaml.safe_load(filename_fh)


def get_backend_instance_config(
    config: Dict[str, Any], backend: str, instance: str
) -> Any:
    """
    Extract and resolve a specific backend instance configuration.

    Args:
        config (dict): Full configuration dictionary containing backend definitions.
        backend (str): Name of the backend to use.
        instance (str): Name of the backend instance to load.

    Returns:
        namedtuple: A BackendConfig namedtuple with the instance parameters.

    Raises:
        Exception: If the backend or instance is not defined, or referenced environment variables are missing.
    """

    def backend_config_factory(data):

        nt = namedtuple("BackendConfig", data.keys())

        return nt(**data)

    if backend not in SUPPORTED_BACKENDS:
        supported_backends = ", ".join(SUPPORTED_BACKENDS)
        raise Exception(
            f"Backend `{backend}` is not supported. Supported backends are: {supported_backends}"
        )

    if backend not in config["backends"]:
        raise Exception(f"There is no backend `{backend}` defined in the config.")

    if instance not in config["backends"][backend]:
        raise Exception(
            f"Backend `{backend}` has no instance configured named `{instance}.`"
        )

    backend_config = config["backends"][backend][instance]
    for key, value in backend_config.items():
        env_var = re.match(r"^\$\{\{(.*)?\}\}$", str(value))
        if env_var:
            if env_var.groups()[0] in os.environ:
                backend_config[key] = os.environ[env_var.groups()[0]]
            else:
                raise Exception(
                    f"Backend `{backend}` instance `{instance}` refers to a non-existing environment variable named `{env_var.groups()[0]}`."
                )
    return backend_config_factory(backend_config)


def read_stdin() -> Iterator[str]:
    """
    Yield stripped lines from standard input if available.
    """
    if not sys.stdin.isatty():
        for item in sys.stdin.readlines():
            yield item.lstrip().rstrip()


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments and return the populated namespace.

    Returns:
        argparse.Namespace: Parsed command-line arguments.
    """

    class EnvDefault(argparse.Action):
        """
        Argparse action to read default value from an environment variable if set.

        Args:
            envvar (str): Name of the environment variable to check.
            required (bool): Whether the argument is required if no default is set.
        """

        def __init__(self, envvar=None, required=True, default=None, **kwargs):
            env_value = os.environ.get(envvar) if envvar else None
            if env_value is not None:
                default = env_value

            kwargs["default"] = default
            kwargs["required"] = required and default is None

            self.envvar = envvar
            super().__init__(**kwargs)

        def __call__(self, parser, namespace, values, option_string=None):
            setattr(namespace, self.dest, values)

    main = argparse.ArgumentParser(
        description="A CLI tool that facilitates decision-making, automation, and problem-solving through the use of LLM AI."
    )
    main.add_argument(
        "--config",
        type=str,
        required=True,
        action=EnvDefault,
        envvar="CLAI_CONFIG",
        help="The path of the config to use.",
    )
    main.add_argument(
        "--backend",
        type=str,
        required=True,
        action=EnvDefault,
        envvar="CLAI_BACKEND",
        help="The llm backend to select from `config`.",
    )
    main.add_argument(
        "--instance",
        type=str,
        required=True,
        action=EnvDefault,
        envvar="CLAI_INSTANCE",
        help="The backend instance to select from `config`.",
    )
    main.add_argument(
        "--debug",
        action="store_true",
        help="Prints the payload submitted to the backend API.",
    )

    subparsers = main.add_subparsers(dest="command", required=True)

    # vanilla prompt
    parser_prompt = subparsers.add_parser(
        "prompt",
        help="Generate a plain, unstructured prompt and return the LLM's raw response.",
    )
    parser_prompt.add_argument(
        "prompt",
        type=str,
        nargs="?",
        default="",
        help="The LLM prompt to execute.",
    )

    # bool prompt
    bool_prompt = subparsers.add_parser(
        "bool",
        help="Ask the LLM a true/false question and return an appropriate exit code (0 for True, 1 for False).",
    )
    bool_prompt.add_argument(
        "prompt",
        type=str,
        nargs="?",
        default="",
        help="The LLM prompt to execute.",
    )

    # structured prompt
    structured_prompt = subparsers.add_parser(
        "structured",
        help="Provide a prompt along with a JSON schema to receive a structured, schema-compliant response from the LLM.",
    )
    structured_prompt.add_argument(
        "--prompt",
        type=str,
        nargs="?",
        default="",
        help="The LLM prompt to execute.",
    )
    structured_prompt.add_argument(
        "--schema",
        type=str,
        help="The JSON schema to apply.",
    )

    return main.parse_args()
