#
#  azure_openai.py
#

import tiktoken
from openai import AzureOpenAI
from clai.backend.openai import (
    ValidateTokenLength,
    build_messages,
    RESPONSE_FORMAT,
)
from clai.prompts import AZURE_BOOL_PROMPT

from pydantic import BaseModel


class BoolResponseModel(BaseModel):
    reason: str
    answer: bool


def prompt(
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
    bool_prompt=False,
    debug=False,
):
    client = AzureOpenAI(
        api_key=token,
        azure_endpoint=endpoint,
        api_version=api_version,
    )

    if base_model is None:
        token_model = model
    else:
        token_model = base_model

    if bool_prompt:
        system = AZURE_BOOL_PROMPT

    messages = build_messages(max_tokens, token_model, system, prompts, stdin)

    if debug:
        print(messages)

    if bool_prompt:
        response = client.chat.completions.create(
            messages=messages,
            model=model,
            temperature=temperature,
            response_format={"type": "json_object"},
        )
    else:
        response = client.chat.completions.create(
            messages=messages,
            model=model,
            temperature=temperature,
        )
    return response.choices[0].message.content
