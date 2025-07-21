# MIT License
#
# Copyright (c) 2025 Jelle Smet
#
# This software is released under the MIT License.
# See the LICENSE file in the project root for more information.

SUPPORTED_BACKENDS = ["azure_openai", "openai", "mistral"]

from typing import Any, Callable, Iterable, NoReturn, final


@final
class BaseBackend:
    """
    Base class for CLI backend clients defining common interface and parameters.

    Attributes:
        token (str): API token or key for authentication.
        model (str): Model identifier to use for requests.
        max_tokens (int): Maximum number of tokens allowed in generated responses.
        temperature (float): Sampling temperature for model outputs.
        debug (bool): Flag to enable debug-mode logging of payloads.
    """

    def __init__(
        self,
        token: str,
        model: str,
        max_tokens: int,
        temperature: float,
        debug: bool,
    ) -> None:
        """
        Initialize common backend parameters.

        Args:
            token (str): API token or key.
            model (str): Model identifier.
            max_tokens (int): Maximum token count for requests.
            temperature (float): Sampling temperature.
            debug (bool): Enable debug output if True.
        """
        self.token = token
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.debug = debug

    def bool_prompt(self, prompt: str, stdin: Callable[[], Iterable[str]]) -> NoReturn:
        raise NotImplementedError("Command not Implemented. Try another backend.")

    def prompt(self, prompt: str, stdin: Callable[[], Iterable[str]]) -> NoReturn:
        raise NotImplementedError("Command not Implemented. Try another backend.")

    def structured_prompt(self) -> NoReturn:
        raise NotImplementedError("Command not Implemented. Try another backend.")
