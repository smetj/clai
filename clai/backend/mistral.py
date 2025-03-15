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


def build_messages(max_tokens, model, system, prompts, stdin):
    messages = []

    # vtl = ValidateTokenLength(model=model, max_tokens=max_tokens)

    # vtl.add(system)
    messages.append({"role": "system", "content": system.lstrip().rstrip()})

    for prompt in prompts:
        # vtl.add(prompt)
        messages.append({"role": "user", "content": prompt.lstrip().rstrip()})

    stdin_content = []
    for line in stdin():
        # vtl.add(line)
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

    messages = build_messages(max_tokens, model, system, prompts, stdin)

    if debug:
        print(messages)

    chat_response = client.chat.complete(model=model, messages=messages)

    return chat_response.choices[0].message.content
