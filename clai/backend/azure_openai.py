#
#  azure_openai.py
#

import tiktoken
from openai import AzureOpenAI
from clai.backend.openai import ValidateTokenLength, build_messages, RESPONSE_FORMAT


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
        messages = build_messages(max_tokens, model, system, prompts, stdin)
    else:
        messages = build_messages(max_tokens, base_model, system, prompts, stdin)

    if bool_prompt:
        response_format = RESPONSE_FORMAT
    else:
        response_format = None

    if debug:
        print(messages)

    response = client.chat.completions.create(
        messages=messages, model=model, temperature=temperature
    )
    return response.choices[0].message.content
