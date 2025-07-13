#
#  azure_openai.py
#

from clai.backend import BaseBackend
from clai.backend.openai.tools import build_messages
from clai.prompts import BOOL_PROMPT
from clai.tools import get_exit_code
from openai import AzureOpenAI
from clai.backend.openai import RESPONSE_FORMAT

class Client(BaseBackend):

    def __init__(self, endpoint, api_version, system, *args, **kwargs):
        self.token_model=kwargs.pop("token_model", kwargs["model"])
        self.system = system
        super().__init__(*args, **kwargs)
        self.client = AzureOpenAI(
            api_key=self.token,
            azure_endpoint=endpoint,
            api_version=api_version
        )

    def prompt(self, prompt, stdin):

        messages = build_messages(
            max_tokens=self.max_tokens,
            model=self.token_model,
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
            model=self.token_model,
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


