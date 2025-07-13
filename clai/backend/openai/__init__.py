#
#  backends.py
#
from clai.backend import BaseBackend
from clai.backend.openai.tools import build_messages
from clai.prompts import BOOL_PROMPT
from clai.tools import get_exit_code
from openai import OpenAI as _OpenAI

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


class Client(BaseBackend):

    def __init__(self, system, *args, **kwargs):
        self.system = system
        super().__init__(*args, **kwargs)
        self.client = _OpenAI(api_key=self.token)

    def prompt(self, prompt, stdin):
        messages = build_messages(
            max_tokens=self.max_tokens,
            model=self.model,
            system=self.system,
            prompts=[prompt],
            stdin=stdin,
        )
        if self.debug:
            print(messages)

        return (
            self.client.chat.completions.create(
                messages=messages,
                model=self.model,
                temperature=self.temperature,
            )
            .choices[0]
            .message.content
        )

    def bool_prompt(self, prompt, stdin):

        messages = build_messages(
            max_tokens=self.max_tokens,
            model=self.model,
            system=self.system + BOOL_PROMPT,
            prompts=[prompt],
            stdin=stdin,
        )
        if self.debug:
            print(messages)

        response = (
            self.client.chat.completions.create(
                messages=messages,
                model=self.model,
                temperature=self.temperature,
                response_format=RESPONSE_FORMAT,
            )
            .choices[0]
            .message.content
        )

        return (get_exit_code(response), response)
