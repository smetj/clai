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


def azure_openai(
    endpoint,
    api_version,
    token,
    max_tokens,
    model,
    system,
    prompt,
    stdin,
    temperature=0,
    base_model=None,
):
    client = AzureOpenAI(
        api_key=token,
        azure_endpoint=endpoint,
        api_version=api_version,
    )

    if base_model:
        vtl = ValidateTokenLength(model=base_model, max_tokens=max_tokens)
    else:
        vtl = ValidateTokenLength(model=model, max_tokens=max_tokens)
    vtl.add(system)

    user = []
    vtl.add(prompt)
    user.append({"role": "user", "content": prompt})

    for line in stdin():
        vtl.add(line)
        user.append({"role": "user", "content": line})

    messages = [
        {
            "role": "system",
            "content": system,
        }
    ] + user

    response = client.chat.completions.create(
        messages=messages, model=model, temperature=temperature
    )
    return response.choices[0].message.content


def openai(token, max_tokens, model, system, prompt, stdin, temperature=0):
    client = OpenAI(
        api_key=token,
    )

    vtl = ValidateTokenLength(model=model, max_tokens=max_tokens)
    vtl.add(system)

    user = []
    vtl.add(prompt)
    user.append({"role": "user", "content": prompt})

    for line in stdin():
        vtl.add(line)
        user.append({"role": "user", "content": line})

    messages = [
        {
            "role": "system",
            "content": system,
        }
    ] + user

    response = client.chat.completions.create(
        messages=messages, model=model, temperature=temperature
    )
    return response.choices[0].message.content
