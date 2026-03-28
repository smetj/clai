# MIT License
#
# Copyright (c) 2025 Jelle Smet
#
# This software is released under the MIT License.
# See the LICENSE file in the project root for more information.

from typing import Callable, Iterable, List

import tiktoken


def get_tokenizer(model: str) -> tiktoken.Encoding:
    try:
        return tiktoken.encoding_for_model(model)
    except KeyError:
        # Newer model variants like `gpt-5.4` may not be recognized yet by
        # the installed `tiktoken`, while their family alias is.
        family_aliases = (
            "gpt-5",
            "gpt-4.1",
            "gpt-4o",
            "o1",
            "o3",
            "o4",
        )
        for family_alias in family_aliases:
            if model == family_alias or model.startswith(f"{family_alias}."):
                return tiktoken.encoding_for_model(family_alias)

        raise


def get_output_text(response) -> str:
    texts = []

    for output in response.output:
        if output.type != "message":
            continue

        message_text = []
        for content in output.content:
            if content.type == "output_text":
                message_text.append(content.text)

        if message_text:
            texts.append("".join(message_text))

    if not texts:
        return ""

    return texts[-1]


class ValidateTokenLength:
    def __init__(self, model: str, max_tokens: int) -> None:
        """
        Initialize the token length validator.

        Args:
            model (str): Model name to select the tokenizer.
            max_tokens (int): Maximum number of tokens allowed.
        """
        self.tokenizer = get_tokenizer(model)

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
        return data


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
