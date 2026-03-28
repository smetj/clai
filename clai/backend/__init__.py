# MIT License
#
# Copyright (c) 2025 Jelle Smet
#
# This software is released under the MIT License.
# See the LICENSE file in the project root for more information.

from typing import Callable, Iterable, NoReturn, final

SUPPORTED_BACKENDS = ["azure_openai", "openai", "mistral"]
REASONING_EFFORTS = ("none", "minimal", "low", "medium", "high", "xhigh")


@final
class BaseBackend:
    """
    Base class for CLI backend clients defining common interface and parameters.

    Attributes:
        token (str): API token or key for authentication.
        model (str): Model identifier to use for requests.
        max_tokens (int): Maximum number of tokens allowed in generated responses.
        temperature (float): Sampling temperature for model outputs.
        reasoning (str | None): Reasoning effort for supported reasoning models.
        debug (bool): Flag to enable debug-mode logging of payloads.
    """

    supports_reasoning = False

    def __init__(
        self,
        token: str,
        model: str,
        max_tokens: int,
        debug: bool,
        temperature: float = 1.0,
        reasoning: str | None = None,
    ) -> None:
        """
        Initialize common backend parameters.

        Args:
            token (str): API token or key.
            model (str): Model identifier.
            max_tokens (int): Maximum token count for requests.
            debug (bool): Enable debug output if True.
            temperature (float): Sampling temperature. Defaults to 1.0.
            reasoning (str | None): Reasoning effort for supported reasoning models.
        """
        self.token = token
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        if reasoning is not None and reasoning not in REASONING_EFFORTS:
            supported_reasoning_efforts = ", ".join(REASONING_EFFORTS)
            raise ValueError(
                f"Reasoning must be one of: {supported_reasoning_efforts}"
            )
        if reasoning is not None and not self.supports_reasoning:
            raise ValueError("Reasoning is not supported by this backend.")
        self.reasoning = reasoning
        self.debug = debug

    def bool_prompt(self, prompt: str, stdin: Callable[[], Iterable[str]]) -> NoReturn:
        raise NotImplementedError("Command not Implemented. Try another backend.")

    def prompt(self, prompt: str, stdin: Callable[[], Iterable[str]]) -> NoReturn:
        raise NotImplementedError("Command not Implemented. Try another backend.")

    def structured_prompt(self) -> NoReturn:
        raise NotImplementedError("Command not Implemented. Try another backend.")
