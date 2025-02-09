# clai

A CLI tool for interacting with remote LLM APIs with support for multiple
backends and a flexible configuration system.

```bash
$ echo "red and yellow" | clai --prompt "Does mixing these colors yield orange?"
Yes, mixing red and yellow typically yields orange.
```

```bash
$ echo "red and yellow" | clai --bool --prompt "Mixing these colors yields orange."                
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
      model: gpt-4o
      system: You are a helpful assistant.

  azure_openai:
    default:
      token: ${{CLAI_AZURE_OPENAI_TOKEN}}
      endpoint: "https://api.chatgpt.mycorp.com/"
      api_version: "2024-10-21"
      model: "gpt-4o"
      max_tokens: 4096
      system: You are a helpful assistant.
```

### Backends

The config file contains the connection details for various backends.
Multiple instances per backend are possible and can be referred to using the
`--backend` and `--instance` parameters:

```bash
clai --prompt "Greetings!" --backend openai --instance default
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

The CLI has a number of conveniences built-in.

### STDIN reading

STDIN input is concatenated after the `--prompt` value:

```
cat script.py | clai --prompt "Explain why this code produces the following error: can only concatenate tuple (not str) to tuple"
```

### bool

Enabling `--bool` ensures that the LLM returns a JSON formatted response that
includes a boolean `answer` of either `true` or `false` and the `reason` for
that conclusion. Additionally, the exit code will be `0` for true and `1` for
false.

**false example:**
```bash
$ echo "red and blue" | clai --bool --prompt "Mixing these colors yields orange."
{"answer":false,"reason":"Mixing red and blue yields purple, not orange. The context was sufficient as it clearly stated the colors to be mixed."}
$ echo $?
1
```

**true example:**
```bash
$ echo "red and yellow" | clai --bool --prompt "Mixing these colors yields orange."                
{"answer":true,"reason":"Mixing red and yellow colors indeed yields orange, which is a basic principle of color theory. The context provided is sufficient as it directly states the colors involved an the resulting color."}
$ echo $?
0
```

### no-prose

Enabling `--noprose` is useful to make sure the LLM does not add any unwanted
explanation or formatting to the response:

```
cat test.md | clai --prompt "Convert this markdown content to asciidoc."
= Title

== Chapter 1

This is chapter 1
```

## Backends

### OpenAI

https://openai.com/api/

The following parameters are supported:

- `token`: The OpenAI API token
- `max_tokens`: The maximum number of tokens the prompt is allowed to generate
- `model`: The model to use
- `system`: The system prompt
- `temperature`: The prompt temperature (default 0)

### Azure-OpenAI

https://learn.microsoft.com/en-us/azure/ai-services/openai/

- `token`: The Azure OpenAI API token
- `endpoint`: The endpoint to connect to
- `api_version`: The API version to use
- `model`: The model to use
- `base_model` (Default: `None`): In order to tokenize the input, we need the
  model name to tokenize the input properly. When `model` has a non-standard
  name, it's not possible to infer the actual OpenAI model on which this is
  based.
- `max_tokens`: The maximum number of tokens the prompt is allowed to generate
- `system`: The system prompt
- `temperature`: The prompt temperature (default: 0)
