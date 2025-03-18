import hashlib
import json
import os
from datetime import datetime
from unittest.mock import Mock, MagicMock, patch

import pytest
import pytz

from mem0.configs.base import MemoryConfig
from mem0.memory.main import Memory
from mem0.utils.factory import VectorStoreFactory


@pytest.fixture(autouse=True)
def mock_openai():
    os.environ["OPENAI_API_KEY"] = "123"
    with patch("openai.OpenAI") as mock:
        mock.return_value = Mock()
        yield mock


@pytest.fixture
def memory_instance():
    with patch("mem0.utils.factory.EmbedderFactory") as mock_embedder, patch(
        "mem0.utils.factory.VectorStoreFactory"
    ) as mock_vector_store, patch("mem0.utils.factory.LlmFactory") as mock_llm, patch(
        "mem0.memory.telemetry.capture_event"
    ), patch("mem0.memory.graph_memory.MemoryGraph"):
        mock_embedder.create.return_value = Mock()
        mock_vector_store.create.return_value = Mock()
        mock_llm.create.return_value = Mock()

        config = MemoryConfig(version="v1.1")
        config.graph_store.config = {"some_config": "value"}
        return Memory(config)


@pytest.mark.parametrize(
    "version, enable_graph, custom_prompt",
    [
        ("v1.0", False, None),
        ("v1.1", True, None),
        ("v1.0", False, "CustomPrompt"),
        ("v1.1", True, "CustomPrompt"),
    ]
)
def test_add(memory_instance, version, enable_graph, custom_prompt):
    memory_instance.config.version = version
    memory_instance.enable_graph = enable_graph
    memory_instance._add_to_vector_store = Mock(return_value=[{"memory": "Test memory", "event": "ADD"}])
    memory_instance._add_to_graph = Mock(return_value=[])

    result = memory_instance.add(
        messages=[{"role": "user", "content": "Test message"}],
        user_id="test_user",
        prompt=custom_prompt,
        graph_prompt=custom_prompt,
        includes={"vector": "test_include", "graph": "test_graph_include"},
        excludes={"vector": "test_exclude", "graph": "test_graph_exclude"},
        custom_categories=[{"category1": "desc1"}],
        custom_node_types=[{"type1": "desc1"}],
        custom_relations=[{"relation1": "desc1"}]
    )

    if enable_graph:
        assert "results" in result
        assert result["results"] == [{"memory": "Test memory", "event": "ADD"}]
        assert "relations" in result
        assert result["relations"] == []
    else:
        assert "results" in result
        assert result["results"] == [{"memory": "Test memory", "event": "ADD"}]

    memory_instance._add_to_vector_store.assert_called_once_with(
        [{"role": "user", "content": "Test message"}],
        {"user_id": "test_user"},
        {"user_id": "test_user"},
        True,
        "- category1: desc1",
        prompt=custom_prompt,
        includes="test_include",
        excludes="test_exclude"
    )

    memory_instance._add_to_graph.assert_called_once_with(
        [{"role": "user", "content": "Test message"}],
        {"user_id": "test_user"},
        "- type1: desc1",
        "- relation1: desc1",
        custom_prompt,
        "test_graph_include",
        "test_graph_exclude"
    )


def test_get(memory_instance):
    mock_memory = Mock(
        id="test_id",
        payload={
            "data": "Test memory",
            "user_id": "test_user",
            "hash": "test_hash",
            "created_at": "2023-01-01T00:00:00",
            "updated_at": "2023-01-02T00:00:00",
            "extra_field": "extra_value",
        },
    )
    memory_instance.vector_store.get = Mock(return_value=mock_memory)

    result = memory_instance.get("test_id")

    assert result["id"] == "test_id"
    assert result["memory"] == "Test memory"
    assert result["user_id"] == "test_user"
    assert result["hash"] == "test_hash"
    assert result["created_at"] == "2023-01-01T00:00:00"
    assert result["updated_at"] == "2023-01-02T00:00:00"
    assert result["metadata"] == {"extra_field": "extra_value"}


@pytest.mark.parametrize(
    "version, enable_graph, test_params",
    [
        ("v1.0", False, {"user_id": "test_user", "limit": 100}),
        ("v1.1", True, {"user_id": "test_user", "limit": 50}),
        ("v1.1", False, {"agent_id": "test_agent", "limit": 10}),
        ("v1.1", True, {"user_id": "test_user", "agent_id": "test_agent", "run_id": "test_run", "limit": 5}),
    ],
)
def test_search(memory_instance, version, enable_graph, test_params):
    memory_instance.config.version = version
    memory_instance.enable_graph = enable_graph
    mock_memories = [
        Mock(id="1", payload={"data": "Memory 1", **{k:v for k,v in test_params.items() if k != 'limit'}}, score=0.9),
        Mock(id="2", payload={"data": "Memory 2", **{k:v for k,v in test_params.items() if k != 'limit'}}, score=0.8),
    ]
    memory_instance.vector_store.search = Mock(return_value=mock_memories[:test_params.get('limit', 100)])
    memory_instance.embedding_model.embed = Mock(return_value=[0.1, 0.2, 0.3])
    memory_instance.graph.search = Mock(return_value=[{"relation": "test_relation"}])

    result = memory_instance.search("test query", **test_params)

    if version == "v1.1":
        assert "results" in result
        assert len(result["results"]) <= test_params.get('limit', 100)
        assert result["results"][0]["id"] == "1"
        assert result["results"][0]["memory"] == "Memory 1"
        for k, v in test_params.items():
            if k != 'limit':
                assert result["results"][0][k] == v
        assert result["results"][0]["score"] == 0.9
        if enable_graph:
            assert "relations" in result
            assert result["relations"] == [{"relation": "test_relation"}]
        else:
            assert "relations" not in result
    else:
        assert isinstance(result, dict)
        assert "results" in result
        assert len(result["results"]) <= test_params.get('limit', 100)

    filters = {k:v for k,v in test_params.items() if k != 'limit'}
    memory_instance.vector_store.search.assert_called_once_with(
        query=[0.1, 0.2, 0.3],
        limit=test_params.get('limit', 100),
        filters=filters
    )
    memory_instance.embedding_model.embed.assert_called_once_with("test query", "search")

    if enable_graph:
        memory_instance.graph.search.assert_called_once_with(
            "test query",
            filters,
            test_params.get('limit', 100)
        )
    else:
        memory_instance.graph.search.assert_not_called()


def test_update(memory_instance):
    memory_instance.embedding_model = Mock()
    memory_instance.embedding_model.embed = Mock(return_value=[0.1, 0.2, 0.3])

    memory_instance._update_memory = Mock()

    result = memory_instance.update("test_id", "Updated memory")

    memory_instance._update_memory.assert_called_once_with(
        "test_id", "Updated memory", {"Updated memory": [0.1, 0.2, 0.3]}
    )

    assert result["message"] == "Memory updated successfully!"


def test_delete(memory_instance):
    memory_instance._delete_memory = Mock()

    result = memory_instance.delete("test_id")

    memory_instance._delete_memory.assert_called_once_with("test_id")
    assert result["message"] == "Memory deleted successfully!"


@pytest.mark.parametrize("version, enable_graph", [("v1.0", False), ("v1.1", True)])
def test_delete_all(memory_instance, version, enable_graph):
    memory_instance.config.version = version
    memory_instance.enable_graph = enable_graph
    mock_memories = [Mock(id="1"), Mock(id="2")]
    memory_instance.vector_store.list = Mock(return_value=(mock_memories, None))
    memory_instance._delete_memory = Mock()
    memory_instance.graph.delete_all = Mock()

    result = memory_instance.delete_all(user_id="test_user")

    assert memory_instance._delete_memory.call_count == 2

    if enable_graph:
        memory_instance.graph.delete_all.assert_called_once_with({"user_id": "test_user"})
    else:
        memory_instance.graph.delete_all.assert_not_called()

    assert result["message"] == "Memories deleted successfully!"


def test_reset(memory_instance):
    memory_instance.vector_store.delete_col = Mock()
    # persisting vector store to make sure previous collection is deleted
    initial_vector_store = memory_instance.vector_store
    memory_instance.db.reset = Mock()

    with patch.object(VectorStoreFactory, "create", return_value=Mock()) as mock_create:
        memory_instance.reset()

        initial_vector_store.delete_col.assert_called_once()
        memory_instance.db.reset.assert_called_once()
        mock_create.assert_called_once_with(
            memory_instance.config.vector_store.provider, memory_instance.config.vector_store.config
        )


@pytest.mark.parametrize(
    "version, enable_graph, test_params, expected_result",
    [
        (
            "v1.0",
            False,
            {"user_id": "test_user", "limit": 100},
            {"results": [{"id": "1", "memory": "Memory 1", "user_id": "test_user"}]}
        ),
        (
            "v1.1",
            False,
            {"agent_id": "test_agent", "limit": 50},
            {"results": [{"id": "1", "memory": "Memory 1", "agent_id": "test_agent"}]}
        ),
        (
            "v1.1",
            True,
            {"user_id": "test_user", "agent_id": "test_agent", "run_id": "test_run", "limit": 10},
            {
                "results": [{"id": "1", "memory": "Memory 1", "user_id": "test_user", "agent_id": "test_agent", "run_id": "test_run"}],
                "relations": [{"source": "entity1", "relationship": "rel", "target": "entity2"}],
            },
        ),
    ],
)
def test_get_all(memory_instance, version, enable_graph, test_params, expected_result):
    memory_instance.config.version = version
    memory_instance.enable_graph = enable_graph
    
    # Create mock memory with all test parameters except limit
    memory_payload = {"data": "Memory 1"}
    memory_payload.update({k:v for k,v in test_params.items() if k != 'limit'})
    mock_memories = [Mock(id="1", payload=memory_payload)]
    
    memory_instance.vector_store.list = Mock(return_value=(mock_memories[:test_params.get('limit', 100)], None))
    memory_instance.graph.get_all = Mock(
        return_value=[{"source": "entity1", "relationship": "rel", "target": "entity2"}]
    )

    result = memory_instance.get_all(**test_params)

    assert isinstance(result, dict)
    assert "results" in result
    assert len(result["results"]) == len(expected_result["results"])
    for expected_item, result_item in zip(expected_result["results"], result["results"]):
        assert all(key in result_item for key in expected_item)
        assert result_item["id"] == expected_item["id"]
        assert result_item["memory"] == expected_item["memory"]
        for k, v in test_params.items():
            if k != 'limit':
                assert result_item[k] == v

    if enable_graph:
        assert "relations" in result
        assert result["relations"] == expected_result["relations"]
    else:
        assert "relations" not in result

    filters = {k:v for k,v in test_params.items() if k != 'limit'}
    memory_instance.vector_store.list.assert_called_once_with(
        filters=filters,
        limit=test_params.get('limit', 100)
    )

    if enable_graph:
        memory_instance.graph.get_all.assert_called_once_with(
            filters,
            test_params.get('limit', 100)
        )
    else:
        memory_instance.graph.get_all.assert_not_called()

    # Test with no filters
    with pytest.raises(ValueError, match="One of the filters: user_id, agent_id or run_id is required!"):
        memory_instance.get_all()

def test_prepare_params():
    memory = Memory()
    
    # Test with None input
    result = memory._prepare_params()
    assert result == {}
    
    # Test with empty dict
    result = memory._prepare_params({})
    assert result == {}
    
    # Test with valid params
    params = {"key1": "value1", "key2": None, "key3": "value3"}
    result = memory._prepare_params(params)
    assert result == {"key1": "value1", "key3": "value3"}

def test_create_categories(memory_instance):
    memory_instance.llm.generate_response = Mock(return_value=json.dumps({
        "memory": [
            {
                "text": "Memory 1",
                "categories": ["category1", "category2"]
            }
        ]
    }))

    test_memories = {
        "memory": [
            {
                "text": "Memory 1",
                "event": "ADD"
            }
        ]
    }
    
    result = memory_instance._create_categories(json.dumps(test_memories), "custom_categories")
    
    assert "memory" in result
    assert len(result["memory"]) == 1
    assert result["memory"][0]["categories"] == ["category1", "category2"]
    
    memory_instance.llm.generate_response.assert_called_once()

def test_create_memory(memory_instance):
    test_data = "Test memory"
    test_embeddings = {"Test memory": [0.1, 0.2, 0.3]}
    test_categories = ["category1"]
    test_metadata = {"user_id": "test_user"}
    
    with patch("uuid.uuid4", return_value="test-uuid"):
        memory_id = memory_instance._create_memory(
            test_data,
            test_embeddings,
            test_categories,
            test_metadata
        )
    
    expected_metadata = {
        **test_metadata,
        "data": test_data,
        "hash": hashlib.md5(test_data.encode()).hexdigest(),
        "created_at": datetime.now(pytz.timezone("US/Pacific")).isoformat(),
        "categories": test_categories
    }
    
    memory_instance.vector_store.insert.assert_called_once_with(
        vectors=[test_embeddings["Test memory"]],
        ids=["test-uuid"],
        payloads=[expected_metadata]
    )
    
    assert memory_id == "test-uuid"

def test_update_memory(memory_instance):
    test_id = "test-id"
    test_data = "Updated memory"
    test_embeddings = {"Updated memory": [0.1, 0.2, 0.3]}
    test_metadata = {"user_id": "test_user"}
    
    existing_memory = Mock(
        payload={
            "data": "Original memory",
            "created_at": "2023-01-01T00:00:00",
            "user_id": "test_user"
        }
    )
    memory_instance.vector_store.get = Mock(return_value=existing_memory)
    
    memory_instance._update_memory(test_id, test_data, test_embeddings, test_metadata)
    
    memory_instance.vector_store.update.assert_called_once()
    update_call = memory_instance.vector_store.update.call_args[1]
    assert update_call["vector_id"] == test_id
    assert update_call["vector"] == test_embeddings["Updated memory"]
    assert update_call["payload"]["data"] == test_data
    assert "updated_at" in update_call["payload"]
    assert update_call["payload"]["user_id"] == "test_user"

def test_delete_memory(memory_instance):
    test_id = "test-id"
    existing_memory = Mock(payload={"data": "Test memory"})
    memory_instance.vector_store.get = Mock(return_value=existing_memory)
    
    memory_instance._delete_memory(test_id)
    
    memory_instance.vector_store.delete.assert_called_once_with(vector_id=test_id)
    memory_instance.db.add_history.assert_called_once()

def test_history(memory_instance):
    test_id = "test-id"
    expected_history = [
        {"action": "ADD", "timestamp": "2023-01-01T00:00:00"}
    ]
    memory_instance.db.get_history = Mock(return_value=expected_history)
    
    result = memory_instance.history(test_id)
    
    assert result == expected_history
    memory_instance.db.get_history.assert_called_once_with(test_id)

def test_add_with_invalid_filters():
    memory = Memory()
    
    with pytest.raises(ValueError, match="One of the filters: user_id, agent_id or run_id is required!"):
        memory.add("Test message")

def test_from_config_invalid_config():
    with pytest.raises(ValueError):
        Memory.from_config({"invalid": "config"})

@pytest.mark.parametrize(
    "input_data, expected_output",
    [
        ({"graph_store": {}, "embedder": {"config": {"embedding_dims": 768}}},
         {"graph_store": {}, "embedder": {"config": {"embedding_dims": 768}}, "vector_store": {"config": {"embedding_model_dims": 768}}}),
        ({}, {})
    ]
)
def test_process_config(input_data, expected_output):
    result = Memory._process_config(input_data)
    assert result == expected_output

def test_add_with_vision_enabled(memory_instance):
    memory_instance.config.llm.config["enable_vision"] = True
    memory_instance.config.llm.config["vision_details"] = True
    
    messages = [{"role": "user", "content": "Test message with image"}]
    memory_instance.llm.generate_response = Mock(return_value="Processed vision content")
    
    with patch("mem0.memory.utils.parse_vision_messages") as mock_parse:
        mock_parse.return_value = [{"role": "user", "content": "Processed vision content"}]
        memory_instance.add(messages, user_id="test_user")
        
        mock_parse.assert_called_once_with(messages, memory_instance.llm, True)
