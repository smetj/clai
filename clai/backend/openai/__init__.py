# MIT License
#
# Copyright (c) 2025 Jelle Smet
#
# This software is released under the MIT License.
# See the LICENSE file in the project root for more information.
#
#  backends.py
#
from typing import Any, Callable, Iterable, Tuple

from clai.backend import BaseBackend
from clai.backend.openai.tools import build_messages
from clai.prompts import BOOL_PROMPT
from clai.tools import get_exit_code
from openai import OpenAI as _OpenAI
import jsonschema
import json

RESPONSE_FORMAT = {
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


class Client(BaseBackend):
    """
    OpenAI backend client implementation using the official OpenAI Python SDK.

    Args:
        system (str): System prompt message.
        *args, **kwargs: Additional parameters for BaseBackend.
    """

    def __init__(self, system: str, *args: Any, **kwargs: Any) -> None:
        """
        Initialize the OpenAI client with system prompt and credentials.

        Args:
            system (str): System prompt message.
        """
        self.system = system
        super().__init__(*args, **kwargs)
        self.client = _OpenAI(api_key=self.token)

    def prompt(self, prompt: str, stdin: Callable[[], Iterable[str]]) -> str | None:
        """
        Send a user prompt to OpenAI and return the response content.

        Args:
            prompt (str): User prompt text.
            stdin (callable): Function yielding additional stdin lines.

        Returns:
            str: The response content from the model.
        """
        messages = build_messages(
            max_tokens=self.max_tokens,
            model=self.model,
            system=self.system,
            prompts=[prompt],
            stdin=stdin,
        )
        if self.debug:
            print(messages)

        return (
            self.client.chat.completions.create(
                messages=messages,
                model=self.model,
                temperature=self.temperature,
            )
            .choices[0]
            .message.content
        )

    def bool_prompt(
        self, prompt: str, stdin: Callable[[], Iterable[str]]
    ) -> Tuple[int, str]:
        """
        Send a true/false prompt, parse and return exit code and model response.

        Args:
            prompt (str): True/false question prompt.
            stdin (callable): Function yielding additional stdin lines.

        Returns:
            tuple[int, str]: A tuple of exit code and raw JSON response.
        """

        messages = build_messages(
            max_tokens=self.max_tokens,
            model=self.model,
            system=self.system + BOOL_PROMPT,
            prompts=[prompt],
            stdin=stdin,
        )
        if self.debug:
            print(messages)

        response = (
            self.client.chat.completions.create(
                messages=messages,
                model=self.model,
                temperature=self.temperature,
                response_format=RESPONSE_FORMAT,
            )
            .choices[0]
            .message.content
        )

        return (get_exit_code(response), response)

    def structured(self, prompt, stdin, schema):

        ValidatorClass = jsonschema.validators.validator_for(schema)
        with open(schema) as schema_fh:
            schema = {
                "type": "json_schema",
                "json_schema": {
                    "name": "clai",
                    "schema": json.load(schema_fh),
                    "strict": True,
                },
            }

        try:
            ValidatorClass.check_schema(schema["json_schema"])
        except jsonschema.exceptions.SchemaError as e:
            print("❌ Invalid JSON Schema:", e)
            sys.exit(1)

        messages = build_messages(
            max_tokens=self.max_tokens,
            model=self.model,
            system=self.system,
            prompts=[prompt],
            stdin=stdin,
        )
        if self.debug:
            print(messages)

        return (
            self.client.chat.completions.create(
                messages=messages,
                model=self.model,
                temperature=self.temperature,
                response_format=schema,
            )
            .choices[0]
            .message.content
        )
