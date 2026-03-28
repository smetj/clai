import pytest

from clai.backend import BaseBackend
from clai.backend.azure_openai import Client as AzureOpenAIClient
from clai.backend.openai import Client as OpenAIClient


def test_base_backend_defaults_temperature_to_neutral():
    backend = BaseBackend(
        token="token",
        model="gpt-5.4",
        max_tokens=1000,
        debug=False,
    )

    assert backend.temperature == 1.0


def test_base_backend_rejects_invalid_reasoning():
    with pytest.raises(ValueError):
        BaseBackend(
            token="token",
            model="gpt-5.4",
            max_tokens=1000,
            temperature=1.0,
            debug=False,
            reasoning="invalid",
        )


def test_base_backend_rejects_reasoning_for_unsupported_backend():
    with pytest.raises(ValueError, match="Reasoning is not supported"):
        BaseBackend(
            token="token",
            model="gpt-5.4",
            max_tokens=1000,
            temperature=1.0,
            debug=False,
            reasoning="low",
        )


def test_openai_backend_allows_reasoning_without_client_init(monkeypatch):
    monkeypatch.setattr(OpenAIClient, "__init__", BaseBackend.__init__)

    backend = OpenAIClient(
        token="token",
        model="gpt-5.4",
        max_tokens=1000,
        temperature=1.0,
        debug=False,
        reasoning="low",
    )

    assert backend.reasoning == "low"


def test_azure_openai_backend_allows_reasoning_without_client_init(monkeypatch):
    monkeypatch.setattr(AzureOpenAIClient, "__init__", BaseBackend.__init__)

    backend = AzureOpenAIClient(
        token="token",
        model="gpt-5.4",
        max_tokens=1000,
        temperature=1.0,
        debug=False,
        reasoning="low",
    )

    assert backend.reasoning == "low"
