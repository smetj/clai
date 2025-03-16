#
#  backends.py
#

import tiktoken
from openai import OpenAI
from clai.prompts import BOOL_PROMPT
from clai.backend.openai import (
    BOOL_PROMPT,
)

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


class ValidateTokenLength:
    def __init__(self, model, max_tokens):
        self.tokenizer = tiktoken.encoding_for_model(model)

        self.total_tokens = 0
        self.max_tokens = max_tokens

    def add(self, data):
        self.total_tokens += len(self.tokenizer.encode(data))
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
    client = OpenAI(api_key=token)

    if bool_prompt:
        response_format = RESPONSE_FORMAT
        system = BOOL_PROMPT
    else:
        response_format = None

    messages = build_messages(max_tokens, model, system, prompts, stdin)

    if debug:
        print(messages)

    response = client.chat.completions.create(
        messages=messages,
        model=model,
        temperature=temperature,
        response_format=response_format,
    )

    return response.choices[0].message.content
