#
#  backends.py
#

import tiktoken
from openai import AzureOpenAI, OpenAI

SUPPORTED_BACKENDS = ["azure_openai", "openai"]


class ValidateTokenLength:
    def __init__(self, model, max_tokens):
        self.tokenizer = tiktoken.encoding_for_model(model)

        self.total_tokens = 0
        self.max_tokens = max_tokens

    def add(self, data):
        self.total_tokens += len(self.tokenizer.encode(data))
        if self.total_tokens > self.max_tokens:
            raise Exception(f"Total input exceeds {self.total_tokens} tokens.")


def build_messages(max_tokens, model, system, prompts, stdin, base_model=None):

    messages = []

    if base_model:
        vtl = ValidateTokenLength(model=base_model, max_tokens=max_tokens)
    else:
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


def azure_openai(
    endpoint,
    api_version,
    token,
    max_tokens,
    model,
    system,
    prompts,
    stdin,
    temperature=0,
    base_model=None,
    response_format=None,
):
    client = AzureOpenAI(
        api_key=token,
        azure_endpoint=endpoint,
        api_version=api_version,
    )

    messages = build_messages(max_tokens, model, system, prompts, stdin, base_model)

    response = client.chat.completions.create(
        messages=messages, model=model, temperature=temperature
    )
    return response.choices[0].message.content


def openai(
    token,
    max_tokens,
    model,
    system,
    prompts,
    stdin,
    temperature=0,
    base_model=None,
    response_format=None,
):

    client = OpenAI(api_key=token)

    messages = build_messages(max_tokens, model, system, prompts, stdin, base_model)

    response = client.chat.completions.create(
        messages=messages,
        model=model,
        temperature=temperature,
        response_format=response_format,
    )

    return response.choices[0].message.content
