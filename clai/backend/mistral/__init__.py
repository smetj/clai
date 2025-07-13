# MIT License
#
# Copyright (c) 2025 Jelle Smet
#
# This software is released under the MIT License.
# See the LICENSE file in the project root for more information.
#
# mistral.py
#

from clai.backend import BaseBackend
from clai.backend.mistral.tools import build_messages

from mistralai import Mistral
import re
from clai.prompts import BOOL_PROMPT

from mistralai.models import responseformat
from pydantic import BaseModel
from clai.tools import get_exit_code
from clai.backend.openai import RESPONSE_FORMAT

class Client(BaseBackend):

    def __init__(self, system, *args, **kwargs):
        self.system = system
        super().__init__(*args, **kwargs)

        self.client = Mistral(api_key=self.token)

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
            self.client.chat.complete(
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
            system=self.system + "Return the answer(field: answer, type bool) and a short and concise reason (field: reason, type: bool) in a single line JSON object.",
            prompts=[prompt],
            stdin=stdin,
        )

        if self.debug:
            print(messages)

        response = (
            self.client.chat.complete(
                messages=messages,
                model=self.model,
                temperature=self.temperature,
                response_format={"type": "json_object"}
            )
            .choices[0]
            .message.content
        )
        return (get_exit_code(response), response)
