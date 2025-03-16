import subprocess
import json


def execute_command(command):
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
        'clai --backend openai --prompt "say hello in lowercase and nothing more not even punctuation."'
    )
    assert result["stdout"] == "hello"


def test_openai_bool():
    result = execute_command(
        'clai --backend openai --prompt "mixing black and white yields grey" --bool'
    )

    assert json.loads(result["stdout"])["answer"] is True


def test_azure_openai():
    result = execute_command(
        'clai --backend azure_openai --prompt "say hello in lowercase and nothing more not even punctuation."'
    )
    assert result["stdout"] == "hello"


def test_azure_openai_bool():
    result = execute_command(
        'clai --backend azure_openai --prompt "mixing black and white yields grey" --bool'
    )

    assert json.loads(result["stdout"])["answer"] is True


def test_mistral():
    result = execute_command(
        'clai --backend mistral --prompt "say hello in lowercase and nothing more not even punctuation."'
    )
    assert result["stdout"] == "hello"


def test_mistral_bool():
    result = execute_command(
        'clai --backend mistral --prompt "mixing black and white yields grey" --bool'
    )

    assert json.loads(result["stdout"])["answer"] is True


def test_pipe_stdin():
    result = execute_command(
        'echo "black and white" | clai --backend mistral --prompt "mixing these colors yields grey." --bool'
    )

    assert json.loads(result["stdout"])["answer"] is True
