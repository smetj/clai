# MIT License
#
# Copyright (c) 2025 Jelle Smet
#
# This software is released under the MIT License.
# See the LICENSE file in the project root for more information.
#
# mistral.py
#
from mistralai import Mistral
import re
from clai.prompts import BOOL_PROMPT

from mistralai.models import responseformat
from pydantic import BaseModel


class BoolResponseModel(BaseModel):
    reason: str
    answer: bool


class ValidateTokenLength:
    def __init__(self, model, max_tokens):
        self.tokenizer = re.compile(
            r"\b\w+\b|[^\w\s]"
        ).findall  # very rudimentary tokenizer
        self.total_tokens = 0
        self.max_tokens = max_tokens

    def add(self, data):
        self.total_tokens += len(self.tokenizer(data))
        if self.total_tokens > self.max_tokens:
            raise Exception(f"Total input exceeds {self.total_tokens} tokens.")


def build_messages(max_tokens, model, system, prompts, stdin):
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


def prompt(
    token,
    max_tokens,
    model,
    system,
    prompts,
    stdin,
    temperature=0,
    bool_prompt=False,
    debug=False,
):
    client = Mistral(api_key=token)

    if bool_prompt:
        messages = build_messages(
            max_tokens=max_tokens,
            model=model,
            system=BOOL_PROMPT,
            prompts=prompts,
            stdin=stdin,
        )
    else:
        messages = build_messages(
            max_tokens=max_tokens,
            model=model,
            system=system,
            prompts=prompts,
            stdin=stdin,
        )

    if debug:
        print(messages)

    if bool_prompt:
        chat_response = client.chat.parse(
            model=model,
            messages=messages,
            temperature=temperature,
            response_format=BoolResponseModel,
        )
    else:
        chat_response = client.chat.complete(
            model=model,
            messages=messages,
            temperature=temperature,
        )

    return chat_response.choices[0].message.content
