import json
import os
import subprocess


def execute_command(command, env=None):
    """
    Executes a CLI command and returns the output and error (if any).

    Args:
        command (str): The command to execute.

    Returns:
        dict: A dictionary containing 'stdout', 'stderr', and 'returncode'.
    """
    try:
        result = subprocess.run(
            command,
            shell=True,  # Enables executing shell commands
            capture_output=True,  # Captures both stdout and stderr
            text=True,  # Returns output as a string
            env=(os.environ | {"PYTHONPATH": os.getcwd()}) | (env or {}),
        )

        return {
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "returncode": result.returncode,
        }

    except Exception as e:
        return {"error": str(e)}


def test_openai():
    result = execute_command(
        'clai --backend openai prompt "say hello in lowercase and nothing more not even punctuation."'
    )
    assert result["stdout"] == "hello"


def test_openai_bool():
    result = execute_command(
        'clai --backend openai bool "mixing pigments black and white yields grey"'
    )

    assert json.loads(result["stdout"])["answer"] is True


def test_azure_openai():
    result = execute_command(
        'clai --backend azure_openai prompt "say hello in lowercase and nothing more not even punctuation."'
    )
    assert result["stdout"] == "hello"


def test_azure_openai_bool():
    result = execute_command(
        'clai --backend azure_openai bool "mixing pigments black and white yields grey"'
    )

    assert json.loads(result["stdout"])["answer"] is True


def test_mistral():
    result = execute_command(
        'clai --backend mistral prompt "say hello in lowercase and nothing more not even punctuation."'
    )
    assert result["stdout"] == "hello"


def test_mistral_bool():
    result = execute_command(
        'clai --backend mistral bool "mixing pigments black and white yields grey"'
    )

    assert json.loads(result["stdout"])["answer"] is True


def test_pipe_stdin():
    result = execute_command(
        'echo "black and white" | clai --backend mistral bool "mixing these colors yields grey."'
    )

    assert json.loads(result["stdout"])["answer"] is True


def test_pipe_stdin_no_prompt():
    result = execute_command(
        'echo "Mixing pigments black and white yields grey." | clai --backend mistral bool'
    )

    assert json.loads(result["stdout"])["answer"] is True


def test_no_pipe_stdin_no_prompt():
    result = execute_command("clai --backend mistral bool")
    print(result)
    assert result["returncode"] == 1


def test_structured_openai(tmp_path):
    openai_pkg = tmp_path / "openai"
    openai_pkg.mkdir()
    (openai_pkg / "__init__.py").write_text(
        """
class _OutputText:
    type = "output_text"

    def __init__(self, text):
        self.text = text


class _Message:
    type = "message"

    def __init__(self, text):
        self.content = [_OutputText(text)]


class _Response:
    def __init__(self, text):
        self.output = [_Message(text)]


class _Responses:
    def create(self, **kwargs):
        return _Response('{"foo":"hello","bar":42}')


class OpenAI:
    def __init__(self, api_key=None):
        self.responses = _Responses()
""".lstrip()
    )

    # Create a simple JSON schema file
    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "properties": {
            "foo": {"type": "string"},
            "bar": {"type": "integer"},
        },
        "required": ["foo", "bar"],
        "additionalProperties": False,
    }
    schema_path = tmp_path / "schema.json"
    schema_path.write_text(json.dumps(schema))

    # Use a prompt that should produce a valid response
    result = execute_command(
        f'clai --backend openai structured "Respond with foo=hello and bar=42" --schema {schema_path}',
        env={"PYTHONPATH": f"{tmp_path}:{os.getcwd()}"},
    )
    # Should be valid JSON and match the schema
    data = json.loads(result["stdout"])
    assert isinstance(data, dict)
    assert "foo" in data and "bar" in data
    assert isinstance(data["foo"], str)
    assert isinstance(data["bar"], int)
