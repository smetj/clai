# MIT License
#
# Copyright (c) 2025 Jelle Smet
#
# This software is released under the MIT License.
# See the LICENSE file in the project root for more information.

import tiktoken
from typing import Callable, Iterable, List


class ValidateTokenLength:
    def __init__(self, model: str, max_tokens: int) -> None:
        """
        Initialize the token length validator.

        Args:
            model (str): Model name to select the tokenizer.
            max_tokens (int): Maximum number of tokens allowed.
        """
        self.tokenizer = tiktoken.encoding_for_model(model)

        self.total_tokens = 0
        self.max_tokens = max_tokens

    def add(self, data: str) -> None:
        """
        Add the token count of data to the running total and raise if limit exceeded.

        Args:
            data (str): Text to tokenize and count.

        Raises:
            Exception: If total token count exceeds max_tokens.
        """
        self.total_tokens += len(self.tokenizer.encode(data))
        if self.total_tokens > self.max_tokens:
            raise Exception(f"Total input exceeds {self.total_tokens} tokens.")


def build_messages(
    max_tokens: int,
    model: str,
    system: str,
    prompts: List[str],
    stdin: Callable[[], Iterable[str]],
) -> list[dict[str, str]]:
    messages = []

    vtl = ValidateTokenLength(model=model, max_tokens=max_tokens)

    vtl.add(system)
    messages.append({"role": "system", "content": system.lstrip().rstrip()})

    for prompt in prompts:
        vtl.add(prompt)
        messages.append({"role": "user", "content": prompt.lstrip().rstrip()})

    stdin_content = []
    for line in stdin():
        vtl.add(line)
        stdin_content.append(line.lstrip().rstrip())

    if len(stdin_content) > 0:
        messages.append(
            {"role": "user", "content": "".join(stdin_content)},
        )

    return messages
