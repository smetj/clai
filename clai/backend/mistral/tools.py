# MIT License
#
# Copyright (c) 2025 Jelle Smet
#
# This software is released under the MIT License.
# See the LICENSE file in the project root for more information.

from typing import Callable, Iterable, List

from mistral_common.tokens.tokenizers.mistral import MistralTokenizer


MISTRAL_TOKENIZER = MistralTokenizer.v3()


def get_token_length(data: str) -> int:
    return len(
        MISTRAL_TOKENIZER.instruct_tokenizer.tokenizer.encode(
            data, bos=False, eos=False
        )
    )


class ValidateTokenLength:
    """
    Track and enforce token length limits for Mistral model prompts.

    Attributes:
        tokenizer: The Mistral tokenizer instance.
        total_tokens (int): Running total of token count.
        max_tokens (int): Maximum allowed tokens.
    """

    def __init__(self, model: str, max_tokens: int) -> None:
        self.total_tokens = 0
        self.max_tokens = max_tokens

    def add(self, data: str) -> None:
        self.total_tokens += get_token_length(data)
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
