# clai

A CLI tool to interact with remote LLM APIs with support for multiple backends
and a flexible configuration system.

```bash
$ echo "red and yellow" | clai --config config.yaml --backend openai --instance default prompt "Does mixing these colors yield orange?"
Orange.
```

```bash
$ echo "red and yellow" | clai --config config.yaml --backend openai --instance default bool "Mixing these colors yields orange."
{"answer":true,"reason":"Mixing red and yellow colors indeed yields orange, which is a basic principle of color theory. The context provided is sufficient as it directly states the colors involved an the resulting color."}
$ echo $?
0
```

## Installation

From the root of the repository:

```bash
python -m pip install .
```

## Configuration

### Config file

The CLI requires a config file in which the various LLM backends are
configured. The location of the config file can be set through `--config`.
There is no default location for the config file, so you will have to
explicitly set it. You can avoid the need to define it by setting
the location of the config file in the environment variable `CLAI_CONFIG`.

The config file has the following format:

```yaml
backends:
  openai:
    default:
      token: ${{CLAI_OPENAI_TOKEN}}
      max_tokens: 4096
      model: gpt-5.4
      system: You are a helpful assistant.
      temperature: 1.0
      reasoning: low

  azure_openai:
    default:
      token: ${{CLAI_AZURE_OPENAI_TOKEN}}
      endpoint: "https://my-resource.openai.azure.com"
      deployment: "gpt-5.4"
      model: "gpt-5.4"
      max_tokens: 4096
      system: You are a helpful assistant.
      temperature: 1.0
      reasoning: low

  mistral:
    default:
      token: ${{CLAI_MISTRAL_TOKEN}}
      max_tokens: 4096
      model: mistral-small-latest
      system: You are a helpful assistant.
      temperature: 1.0
```

### Backends

The config file contains the connection details for various backends.
Multiple instances per backend are possible and can be referred to using the
`--backend` and `--instance` parameters:

```bash
clai --backend openai --instance default prompt "Greetings!"
```

Both `--backend` and `--instance` can be set by assigning a value to
environment variables `CLAI_BACKEND` and `CLAI_INSTANCE` respectively.

See the backends section below for a detailed explanation about the various
parameters per backend.

### Variable substitution

Values in the configuration file, such as `${{ENV_VAR}}`, will be replaced
with the corresponding environment variable. This approach helps avoid
storing sensitive data in the configuration file, though it is not limited to
this use.

## Usage

The CLI provides several subcommands for different prompt types:

### Basic prompt

To generate a plain, unstructured response from the LLM:

```bash
clai --config config.yaml --backend openai --instance default prompt "Explain why the sky is blue."
```

You can also pipe input from STDIN, which will be appended after the prompt:

```bash
cat script.py | clai --config config.yaml --backend openai --instance default prompt "Explain why this code produces the following error: can only concatenate tuple (not str) to tuple"
```

If no prompt argument is provided and STDIN is available, the piped content is
used as the prompt:

```bash
echo "Mixing pigments black and white yields grey." | clai --config config.yaml --backend mistral --instance default bool
```

### Boolean prompt

To ask a true/false question and receive a structured JSON response (with exit code 0 for true, 1 for false):

```bash
clai --config config.yaml --backend openai --instance default bool "Mixing these colors yields orange."
```

Or with STDIN:

```bash
echo "red and yellow" | clai --config config.yaml --backend openai --instance default bool "Mixing these colors yields orange."
```

**false example:**
```bash
$ echo "red and blue" | clai --config config.yaml --backend openai --instance default bool "Mixing these colors yields orange."
{"answer":false,"reason":"Mixing red and blue yields purple, not orange. The context was sufficient as it clearly stated the colors to be mixed."}
$ echo $?
1
```

**true example:**
```bash
$ echo "red and yellow" | clai --config config.yaml --backend openai --instance default bool "Mixing these colors yields orange."
{"answer":true,"reason":"Mixing red and yellow colors indeed yields orange, which is a basic principle of color theory. The context provided is sufficient as it directly states the colors involved an the resulting color."}
$ echo $?
0
```

### Structured prompt

To generate a structured response from the LLM using a provided JSON schema:

```bash
clai --config config.yaml --backend openai --instance default structured "Respond with foo=hello and bar=42" --schema path/to/schema.json
```

- The `--schema` argument must point to a valid JSON schema file.
- The model will be instructed to return a response that matches the schema.
- The output will be a JSON object conforming to your schema.

**Example schema (`schema.json`):**
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "properties": {
    "foo": {"type": "string"},
    "bar": {"type": "integer"}
  },
  "required": ["foo", "bar"],
  "additionalProperties": false
}
```

**Example usage:**
```bash
clai --config config.yaml --backend openai --instance default structured "Respond with foo=hello and bar=42" --schema schema.json
```

**Example output:**
```json
{"foo": "hello", "bar": 42}
```

### Environment variable support

You can set `CLAI_CONFIG`, `CLAI_BACKEND`, and `CLAI_INSTANCE` as environment variables to avoid passing them as CLI arguments each time.

```bash
export CLAI_CONFIG=~/myconfig.yaml
export CLAI_BACKEND=openai
export CLAI_INSTANCE=default
clai prompt "Say hello!"
```

## Backends

### OpenAI

https://openai.com/api/

The following parameters are supported:

- `token`: The OpenAI API token
- `max_tokens`: The maximum number of tokens the prompt is allowed to generate
- `model`: The model to use
- `system`: The system prompt
- `temperature`: The prompt temperature (default: `1.0`)
- `reasoning` (optional): One of `none`, `minimal`, `low`, `medium`, `high`, `xhigh`

### Azure-OpenAI

https://learn.microsoft.com/en-us/azure/ai-services/openai/

- `token`: The Azure OpenAI API token
- `endpoint`: The Azure OpenAI resource endpoint. `clai` will derive the
  Responses API base URL and expects an endpoint ending in `.openai.azure.com`.
- `deployment`: The Azure deployment name used for requests
- `model`: The model to use
- `token_model` (optional): Tokenizer model name to use when `deployment` does
  not match a standard OpenAI model identifier
- `max_tokens`: The maximum number of tokens the prompt is allowed to generate
- `system`: The system prompt
- `temperature`: The prompt temperature (default: `1.0`)
- `reasoning` (optional): One of `none`, `minimal`, `low`, `medium`, `high`, `xhigh`

### Mistral

https://mistral.ai/

The following parameters are supported:

- `token`: The Mistral API token
- `max_tokens`: The maximum number of input tokens allowed
- `model`: The model to use
- `system`: The system prompt
- `temperature`: The prompt temperature (default: `1.0`)

Mistral support currently targets `mistralai>=2.1.3` and requires
`mistral-common[sentencepiece]` for local tokenization.

## Notes

- `structured` responses are currently implemented for the `openai` and
  `azure_openai` backends.
- `reasoning` is only supported by the `openai` and `azure_openai` backends.
