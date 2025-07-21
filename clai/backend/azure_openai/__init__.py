#
#  azure_openai.py
#

from clai.backend import BaseBackend
from clai.backend.openai.tools import build_messages
from clai.prompts import BOOL_PROMPT
from clai.tools import get_exit_code
from openai import AzureOpenAI
from typing import Any, Callable, Iterable, Tuple
from clai.backend.openai import RESPONSE_FORMAT


class Client(BaseBackend):
    """
    Azure OpenAI backend client implementation.

    Args:
        endpoint (str): Azure endpoint URL.
        api_version (str): Azure API version identifier.
        system (str): System prompt message.
        *args, **kwargs: Additional parameters for BaseBackend.
    """

    def __init__(
        self,
        endpoint: str,
        api_version: str,
        system: str,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """
        Initialize the Azure OpenAI client with endpoint and credentials.

        Args:
            endpoint (str): Azure endpoint URL.
            api_version (str): Azure API version identifier.
            system (str): System prompt message.
        """
        self.token_model = kwargs.pop("token_model", kwargs["model"])
        self.system = system
        super().__init__(*args, **kwargs)
        self.client = AzureOpenAI(
            api_key=self.token, azure_endpoint=endpoint, api_version=api_version
        )

    def prompt(self, prompt: str, stdin: Callable[[], Iterable[str]]) -> str:
        """
        Send a user prompt to Azure OpenAI and return the response content.

        Args:
            prompt (str): User prompt text.
            stdin (callable): Function yielding additional stdin lines.

        Returns:
            str: The response content from the model.
        """

        messages = build_messages(
            max_tokens=self.max_tokens,
            model=self.token_model,
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
            model=self.token_model,
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
