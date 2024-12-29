# clai

A CLI tool for interacting with remote LLM APIs with support for multiple
backends and a flexible configuration system.

```
$ echo "red and yellow" | clai --prompt "Does mixing these colors yield orange?"
Yes, mixing red and yellow typically yields orange.
```

```
$ echo "red and black" | clai --bool --prompt "Does mixing these colors yield orange?"
false
echo $?
1
```

## Installation

From the root of the repository:

```bash
python -m pip install .
```

## Configuration

### config file

The CLI requires a config file in which the various LLM backends are
configured. The location of the config file can be set through `--config`.
There is no default location for the config file, so you will have to
explicitly set it. You can avoid the need of having to define it by setting
the location of the config file to in environment variable `CLAI_CONFIG`.

The config file has following format:

```yaml
backends:
  openai:
    default:
      token: ${{CLAI_OPENAI_TOKEN}}
      max_tokens: 4096
      model: gpt-4o
      system: You are a helpful assistent.

  azure_openai:
    default:
      token: ${{CLAI_AZURE_OPENAI_TOKEN}}
      endpoint: "https://api.chatgpt.mycorp.com/"
      api_version: "2024-10-21"
      model: "gpt-4o"
      max_tokens: 4096
      system: You are a helpful assistent.
```

### backends

The config file contains the connection details towards various backends.
Multiple instances per backend are possible. and can be referred to using the
`--backend` and `--instance` parameters:

```bash
clai --prompt "Greetings!" --backend openai --instance default
```

Both `--backend` and `--instance` can be set by assigning a value to
environment variables `CLAI_BACKEND` and `CLAI_INSTANCE` respectively.

See backends section below for a detailed explanation about the various
parameters per backend.

### variable substitution

Values in the configuration file, such as `${{ENV_VAR}}`, will be replaced
with the corresponding environment variable. This approach helps avoid
storing sensitive data in the configuration file, though it is not limited to
this use.

## Usage

The CLI has a number of conveniences builtin.

### STDIN reading

STDIN input is concatenated after the `--prompt` value:

```
cat script.py | clai --prompt "Explain why this code produces the following error: can only concatenate tuple (not str) to tuple"
```

### bool

Enabling `--bool` ensures that the LLM responds with one of three values:
`true`, `false`, or `undetermined`, along with the corresponding exit codes
of 0, 1, and 2, respectively.

```
$ echo 'Mixing red and yellow gives orange' | clai --bool --prompt "Is this true?"
true
$ echo $?
0
$ echo 'Mixing red and yellow gives blue' | clai --bool --prompt "Is this true?"
false
$ echo $?
1
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
- `temperature`: The prompt temperature


### Azure-OpenAI

https://learn.microsoft.com/en-us/azure/ai-services/openai/

- `token`: The Azure OpenAI API token
- `endpoint`: The endpoint to connect to
- `api_version`: The API version to use
- `model`: The model to use
- `base_model`(Default: `None`): In order to tokenize the input we need to
  model name to tokenize the input properly. When `model` has a non-standard
  name, its not possible to infer actual OpenAI model on which this is
  based.
- `max_tokens`: The maximum number of tokens the prompt is allowed to generate
- `system`: The system prompt
- `temperature`: The prompt temperature