import pytest
from unittest.mock import Mock, patch
from mem0.embeddings.siliconflow import SiliconFlowEmbedding
from mem0.configs.embeddings.base import BaseEmbedderConfig


@pytest.fixture
def mock_requests():
    with patch("mem0.embeddings.siliconflow.requests") as mock_req:
        yield mock_req


def test_embed_default_model(mock_requests):
    config = BaseEmbedderConfig()
    embedder = SiliconFlowEmbedding(config)
    mock_response = Mock()
    mock_response.data = [Mock(embedding=[0.1, 0.2, 0.3])]
    mock_requests.request.return_value = mock_response

    result = embedder.embed("Hello world")

    mock_requests.request.assert_called_once_with(
        "POST",
        embedder.base_url,
        json={
            "model": "BAAI/bge-m3",
            "input": "Hello world",
            "encoding_format": "float"
        },
        headers={
            "Authorization": f"Bearer {embedder.api_key}",
            "Content-Type": "application/json"
        }
    )
    assert result == [0.1, 0.2, 0.3]


def test_embed_custom_model(mock_requests):
    config = BaseEmbedderConfig(model="custom-model", embedding_dims=1024)
    embedder = SiliconFlowEmbedding(config)
    mock_response = Mock()
    mock_response.data = [Mock(embedding=[0.4, 0.5, 0.6])]
    mock_requests.request.return_value = mock_response

    result = embedder.embed("Test embedding")

    mock_requests.request.assert_called_once_with(
        "POST",
        embedder.base_url,
        json={
            "model": "custom-model",
            "input": "Test embedding",
            "encoding_format": "float"
        },
        headers={
            "Authorization": f"Bearer {embedder.api_key}",
            "Content-Type": "application/json"
        }
    )
    assert result == [0.4, 0.5, 0.6]


def test_embed_removes_newlines(mock_requests):
    config = BaseEmbedderConfig()
    embedder = SiliconFlowEmbedding(config)
    mock_response = Mock()
    mock_response.data = [Mock(embedding=[0.7, 0.8, 0.9])]
    mock_requests.request.return_value = mock_response

    result = embedder.embed("Hello\nworld")

    mock_requests.request.assert_called_once_with(
        "POST",
        embedder.base_url,
        json={
            "model": "BAAI/bge-m3",
            "input": "Hello world",
            "encoding_format": "float"
        },
        headers={
            "Authorization": f"Bearer {embedder.api_key}",
            "Content-Type": "application/json"
        }
    )
    assert result == [0.7, 0.8, 0.9]


def test_embed_without_api_key_env_var(mock_requests):
    config = BaseEmbedderConfig(api_key="test_key")
    embedder = SiliconFlowEmbedding(config)
    mock_response = Mock()
    mock_response.data = [Mock(embedding=[1.0, 1.1, 1.2])]
    mock_requests.request.return_value = mock_response

    result = embedder.embed("Testing API key")

    mock_requests.request.assert_called_once_with(
        "POST",
        embedder.base_url,
        json={
            "model": "BAAI/bge-m3",
            "input": "Testing API key",
            "encoding_format": "float"
        },
        headers={
            "Authorization": "Bearer test_key",
            "Content-Type": "application/json"
        }
    )
    assert result == [1.0, 1.1, 1.2]


def test_embed_uses_environment_api_key_and_base_url(mock_requests, monkeypatch):
    monkeypatch.setenv("SILICONFLOW_API_KEY", "env_key")
    monkeypatch.setenv("SILICONFLOW_API_BASE", "http://test.api.base")
    config = BaseEmbedderConfig()
    embedder = SiliconFlowEmbedding(config)
    mock_response = Mock()
    mock_response.data = [Mock(embedding=[1.3, 1.4, 1.5])]
    mock_requests.request.return_value = mock_response

    result = embedder.embed("Environment config test")

    mock_requests.request.assert_called_once_with(
        "POST",
        "http://test.api.base",
        json={
            "model": "BAAI/bge-m3",
            "input": "Environment config test",
            "encoding_format": "float"
        },
        headers={
            "Authorization": "Bearer env_key",
            "Content-Type": "application/json"
        }
    )
    assert result == [1.3, 1.4, 1.5]