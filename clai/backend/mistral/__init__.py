# MIT License
#
# Copyright (c) 2025 Jelle Smet
#
# This software is released under the MIT License.
# See the LICENSE file in the project root for more information.
#
# mistral.py
#

from clai.backend import BaseBackend
from clai.backend.mistral.tools import build_messages

from mistralai import Mistral
from clai.prompts import BOOL_PROMPT

from clai.tools import get_exit_code
from clai.backend.openai import RESPONSE_FORMAT
from typing import Any, Callable, Iterable, Tuple


class Client(BaseBackend):
    """
    Mistral backend client implementation using the Mistral API.

    Args:
        system (str): System prompt message.
        *args, **kwargs: Additional parameters for BaseBackend.
    """

    def __init__(self, system: str, *args: Any, **kwargs: Any) -> None:
        """
        Initialize the Mistral client with system prompt and credentials.

        Args:
            system (str): System prompt message.
        """
        self.system = system
        super().__init__(*args, **kwargs)

        self.client = Mistral(api_key=self.token)

    def prompt(self, prompt: str, stdin: Callable[[], Iterable[str]]) -> str:
        """
        Send a user prompt to Mistral and return the response content.

        Args:
            prompt (str): User prompt text.
            stdin (callable): Function yielding additional stdin lines.

        Returns:
            str: The response content from the Mistral model.
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
            self.client.chat.complete(
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
            self.client.chat.complete(
                messages=messages,
                model=self.model,
                temperature=self.temperature,
                response_format={"type": "json_object"},
            )
            .choices[0]
            .message.content
        )
        return (get_exit_code(response), response)
