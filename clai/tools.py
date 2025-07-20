#
#  tools.py
#

import argparse
import json
import os
import re
import sys
from collections import namedtuple
from textwrap import dedent

import yaml
from clai.backend import SUPPORTED_BACKENDS
from jsonschema import validate


def cleanup(text):
    return dedent(text).replace("\n", " ")


def validate_bool_response(response):
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


def get_exit_code(response):
    json_response = validate_bool_response(response)

    if json_response["answer"]:
        return 0
    else:
        return 1


def read_config(filename):
    """
    Reads the config file `filename`
    """

    with open(os.path.expanduser(filename)) as filename_fh:
        return yaml.safe_load(filename_fh)


def get_backend_instance_config(config, backend, instance):
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


def read_stdin():
    """Reads input from STDIN if available."""
    if not sys.stdin.isatty():
        for item in sys.stdin.readlines():
            yield item.lstrip().rstrip()
    else:
        return []


def parse_arguments():
    class EnvDefault(argparse.Action):
        def __init__(self, envvar=None, required=True, default=None, **kwargs):
            # Handle environment variable
            env_value = os.environ.get(envvar) if envvar else None
            if env_value is not None:
                default = env_value  # Use envvar if available

            # Update kwargs for argparse
            kwargs["default"] = default
            kwargs["required"] = (
                required and default is None
            )  # Required only if no default

            # Store the environment variable name for debugging
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
