SUPPORTED_BACKENDS = ["azure_openai", "openai", "mistral"]


class BaseBackend:

    def __init__(self, token, model, max_tokens, temperature, debug):
        self.token = token
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.debug = debug

    def bool_prompt(self, prompt, stdin):

        raise NotImplemented("Command not Implemented. Try another backend.")

    def prompt(self, prompt, stdin):

        raise NotImplemented("Command not Implemented. Try another backend.")

    def structured_prompt(self):

        raise NotImplemented("Command not Implemented. Try another backend.")
