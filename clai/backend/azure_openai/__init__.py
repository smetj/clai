# MIT License
#
# Copyright (c) 2025 Jelle Smet
#
# This software is released under the MIT License.
# See the LICENSE file in the project root for more information.
#
#  azure_openai.py
#
import json
import sys
from typing import Any, Callable, Iterable, Tuple

import jsonschema
from openai import OpenAI as _OpenAI

from clai.backend import BaseBackend
from clai.backend.openai import RESPONSE_FORMAT
from clai.backend.openai.tools import ValidateTokenLength, get_output_text
from clai.prompts import BOOL_PROMPT
from clai.tools import get_exit_code


class Client(BaseBackend):
    """
    Azure OpenAI backend client implementation.

    Args:
        endpoint (str): Azure endpoint URL.
        deployment (str): Azure deployment name used for requests.
        system (str): System prompt message.
        *args, **kwargs: Additional parameters for BaseBackend.
    """

    supports_reasoning = True

    def __init__(
        self,
        endpoint: str,
        deployment: str,
        system: str,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """
        Initialize the Azure OpenAI client with endpoint and credentials.

        Args:
            endpoint (str): Azure endpoint URL.
            deployment (str): Azure deployment name used for requests.
            system (str): System prompt message.
        """
        self.token_model = kwargs.pop("token_model", kwargs["model"])
        self.system = system
        super().__init__(*args, **kwargs)
        self.deployment = deployment
        self.client = _OpenAI(
            api_key=self.token,
            base_url=self._get_base_url(endpoint),
        )
        self.vtl = ValidateTokenLength(
            model=self.token_model, max_tokens=self.max_tokens
        )

    def _reasoning(self) -> dict[str, str] | None:
        if self.reasoning is None:
            return None

        return {"effort": self.reasoning}

    @staticmethod
    def _get_base_url(endpoint: str) -> str:
        normalized_endpoint = endpoint.rstrip("/")
        if ".openai.azure.com" not in normalized_endpoint:
            raise ValueError(
                "Azure OpenAI endpoint must end with `.openai.azure.com` when using the Responses API."
            )

        if normalized_endpoint.endswith("/openai/v1"):
            return f"{normalized_endpoint}/"

        if normalized_endpoint.endswith("/openai/v1/"):
            return normalized_endpoint

        return f"{normalized_endpoint}/openai/v1/"

    def prompt(self, prompt: str, stdin: Callable[[], Iterable[str]]) -> str:
        """
        Send a user prompt to Azure OpenAI and return the response content.

        Args:
            prompt (str): User prompt text.
            stdin (callable): Function yielding additional stdin lines.

        Returns:
            str: The response content from the model.
        """

        final_p = [self.vtl.add(prompt)]
        final_i = [self.vtl.add(self.system)]

        for line in stdin():
            final_p.append(self.vtl.add(line))

        if self.debug:
            print("Instructions: ", final_i)
            print("Prompt: ", final_p)

        request = {
            "model": self.deployment,
            "temperature": self.temperature,
            "instructions": "\n".join(final_i),
            "input": "\n".join(final_p),
        }
        if self.reasoning is not None:
            request["reasoning"] = self._reasoning()

        return get_output_text(self.client.responses.create(**request))

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

        final_p = [self.vtl.add(prompt)]
        final_i = [self.vtl.add(self.system + BOOL_PROMPT)]

        for line in stdin():
            final_p.append(self.vtl.add(line))

        if self.debug:
            print("Instructions: ", final_i)
            print("Prompt: ", final_p)

        request = {
            "model": self.deployment,
            "temperature": self.temperature,
            "instructions": "\n".join(final_i),
            "input": "\n".join(final_p),
            "text": RESPONSE_FORMAT,
        }
        if self.reasoning is not None:
            request["reasoning"] = self._reasoning()

        response = get_output_text(self.client.responses.create(**request))

        return (get_exit_code(response), response)

    def structured(
        self,
        prompt: str,
        stdin: Callable[[], Iterable[str]],
        schema: str,
    ) -> str:
        """
        Generate a structured response from the LLM using a provided JSON schema.

        Args:
            prompt (str): The user prompt to send to the LLM.
            stdin (Callable[[], Iterable[str]]): Function yielding additional stdin lines.
            schema (str): Path to the JSON schema file to use for the structured response.

        Returns:
            str: The response content from the model.

        Raises:
            SystemExit: If the provided schema is invalid.
        """
        validator_cls = jsonschema.validators.validator_for(schema)
        with open(schema) as schema_fh:
            schema_obj = {
                "type": "json_schema",
                "json_schema": {
                    "name": "clai",
                    "schema": json.load(schema_fh),
                    "strict": True,
                },
            }

        try:
            validator_cls.check_schema(schema_obj["json_schema"])
        except jsonschema.exceptions.SchemaError as e:
            print("❌ Invalid JSON Schema:", e)
            sys.exit(1)

        final_p = [self.vtl.add(prompt)]
        final_i = [self.vtl.add(self.system)]

        for line in stdin():
            final_p.append(self.vtl.add(line))

        if self.debug:
            print("Instructions: ", final_i)
            print("Prompt: ", final_p)

        request = {
            "model": self.deployment,
            "temperature": self.temperature,
            "instructions": "\n".join(final_i),
            "input": "\n".join(final_p),
            "text": schema_obj,
        }
        if self.reasoning is not None:
            request["reasoning"] = self._reasoning()

        return get_output_text(self.client.responses.create(**request))
