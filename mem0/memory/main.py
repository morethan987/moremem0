import concurrent
import hashlib
import json
import logging
import uuid
import warnings
from datetime import datetime
from typing import Any, Dict, Optional, List, Union

import pytz
from pydantic import ValidationError

from mem0.configs.base import MemoryConfig, MemoryItem
from mem0.configs.prompts import get_update_memory_messages, get_create_categories_prompt
from mem0.memory.base import MemoryBase
from mem0.memory.setup import setup_config
from mem0.memory.storage import SQLiteManager
from mem0.memory.telemetry import capture_event
from mem0.memory.utils import (
    get_fact_retrieval_messages,
    parse_messages,
    parse_vision_messages,
    remove_code_blocks,
)
from mem0.utils.factory import EmbedderFactory, LlmFactory, VectorStoreFactory

# Setup user config
setup_config()

# 创建 logger 对象
logger = logging.getLogger('mem0')

# 设置 `mem0` logger 的日志级别
logger.setLevel(logging.WARNING)

# 创建控制台 Handler，并设置级别
console_handler = logging.StreamHandler()

# 设置日志输出格式
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)

# 将 Handler 添加到 logger
logger.addHandler(console_handler)

# 关闭其他库的日志输出
logging.getLogger().setLevel(logging.WARNING)  # 关闭默认日志级别为DEBUG的日志，避免无关日志输出


class Memory(MemoryBase):
    def __init__(self, config: MemoryConfig = MemoryConfig()):
        self.config = config

        self.custom_prompt = self.config.vector_store.custom_prompt
        self.embedding_model = EmbedderFactory.create(self.config.embedder.provider, self.config.embedder.config)
        self.vector_store = VectorStoreFactory.create(
            self.config.vector_store.provider, self.config.vector_store.config
        )
        self.llm = LlmFactory.create(self.config.llm.provider, self.config.llm.config)
        self.db = SQLiteManager(self.config.history_db_path)
        self.collection_name = self.config.vector_store.config.collection_name
        self.api_version = self.config.version

        self.enable_graph = False

        if self.config.graph_store.config:
            from mem0.memory.graph_memory import MemoryGraph

            self.graph = MemoryGraph(self.config)
            self.enable_graph = True

        capture_event("mem0.init", self)

    @classmethod
    def from_config(cls, config_dict: Dict[str, Any]):
        try:
            config = cls._process_config(config_dict)
            config = MemoryConfig(**config_dict)
        except ValidationError as e:
            logger.error(f"Configuration validation error: {e}\n")
            raise
        return cls(config)
    
    @staticmethod
    def _process_config(config_dict: Dict[str, Any]) -> Dict[str, Any]:
        if "graph_store" in config_dict:
            if "vector_store" not in config_dict and "embedder" in config_dict:
                config_dict["vector_store"] = {}
                config_dict["vector_store"]["config"] = {}
                config_dict["vector_store"]["config"]["embedding_model_dims"] = config_dict["embedder"]["config"]["embedding_dims"]
        try:
            return config_dict
        except ValidationError as e:
            logger.error(f"Configuration validation error: {e}")
            raise

    def add(self, messages: Union[str, List[Dict[str, str]]], **kwargs) -> Dict[str, Any]:
        """
        Adds, updates, or deletes memories as appropriate, based on the provided message(s).

        Args:
            messages (str or List[Dict[str, str]]): Messages to store in the memory.
            **kwargs: Additional parameters such as user_id, agent_id, app_id, metadata, filters.
                user_id (str, optional): ID of the user creating the memory. Defaults to None.
                agent_id (str, optional): ID of the agent creating the memory. Defaults to None.
                run_id (str, optional): ID of the run creating the memory. Defaults to None.
                metadata (dict, optional): Metadata to store with the memory. Defaults to None.
                filters (dict, optional): Filters to apply to the search for pre-existing memories. Defaults to None.
                infer (boolean): Whether to infer the memories. Defaults to True.
                prompt (str, optional): Prompt to use for memory deduction. Defaults to None.
                graph_prompt (str, optional): Prompt to use for graph memory deduction. Defaults to None.
                includes (str, optional): Prompt to include specified info.
                excludes (str, optional): Prompt to exclude specified info.

        Returns:
            dict: A dictionary containing the result of the memory addition operation.
            result: dict of affected events with each dict has the following key:
              'memories': affected memories
              'graph': affected graph memories

              'memories' and 'graph' is a dict, each with following subkeys:
                'add': added memory
                'update': updated memory
                'delete': deleted memory
        """

        kwargs = self._prepare_params(kwargs)
        if kwargs.get("metadate") is None:
            metadata = {}

        filters = kwargs.get("filters") or {}
        if kwargs.get("user_id"):
            filters["user_id"] = metadata["user_id"] = kwargs.get("user_id")
        if kwargs.get("agent_id"):
            filters["agent_id"] = metadata["agent_id"] = kwargs.get("agent_id")
        if kwargs.get("run_id"):
            filters["run_id"] = metadata["run_id"] = kwargs.get("run_id")

        infer = kwargs.get("infer") if kwargs.get("infer") else True
        
        includes_dic = kwargs.get("includes") or {}
        excludes_dic = kwargs.get("excludes") or {}
        for dic in [includes_dic, excludes_dic]:
            dic["vector"] = dic.get("vector")
            dic["graph"] = dic.get("graph")

        # 解析custom_categories
        custom_categories = kwargs.get("custom_categories") or self.config.vector_store.custom_categories
        if custom_categories:
            custom_categories = "\n".join([f"- {key}: {value}" for category in custom_categories for key, value in category.items()])

        # 解析custom_node_types
        custom_node_types = kwargs.get("custom_node_types") or self.config.graph_store.custom_node_types
        if custom_node_types:
            custom_node_types = "\n".join([f"- {key}: {value}" for node_type in custom_node_types for key, value in node_type.items()])

        # 解析custom_relations
        custom_relations = kwargs.get("custom_relations") or self.config.graph_store.custom_relations
        if custom_relations:
            custom_relations = "\n".join([f"- {key}: {value}" for relation in custom_relations for key, value in relation.items()])

        if not any(key in filters for key in ("user_id", "agent_id", "run_id")):
            raise ValueError("One of the filters: user_id, agent_id or run_id is required!")

        if isinstance(messages, str):
            messages = [{"role": "user", "content": messages}]
        
        if self.config.llm.config.get("enable_vision"):
            messages = parse_vision_messages(messages, self.llm, self.config.llm.config.get("vision_details"))
        else:
            messages = parse_vision_messages(messages)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future1 = executor.submit(self._add_to_vector_store, messages, metadata, filters, infer, custom_categories, prompt=kwargs.get("prompt"), includes=includes_dic["vector"], excludes=excludes_dic["vector"])
            
            future2 = executor.submit(self._add_to_graph, messages, filters, custom_node_types=custom_node_types, custom_relations=custom_relations, graph_prompt=kwargs.get("graph_prompt"), includes=includes_dic["graph"], excludes=excludes_dic["graph"])

            concurrent.futures.wait([future1, future2])

            vector_store_result = future1.result()
            graph_result = future2.result()

        if self.api_version == "v1.0":
            warnings.warn(
                "The current add API output format is deprecated. "
                "To use the latest format, set `api_version='v1.1'`. "
                "The current format will be removed in mem0ai 1.1.0 and later versions.",
                category=DeprecationWarning,
                stacklevel=2,
            )
            return vector_store_result
        
        if self.enable_graph:
            return {
                "results": vector_store_result,
                "relations": graph_result,
            }
        
        return {"results": vector_store_result}
        
    def _prepare_params(self, kwargs: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Prepare query parameters.

        Args:
            kwargs: Keyword arguments to include in the parameters.

        Returns:
            A dictionary containing the prepared parameters.
        """

        if kwargs is None:
            kwargs = {}

        return {k: v for k, v in kwargs.items() if v is not None}

    def _add_to_vector_store(self, messages, metadata, filters, infer, custom_categories=None, prompt=None, includes=None, excludes=None):
        if not infer:
            returned_memories = []
            for message in messages:
                if message["role"] != "system":
                    message_embeddings = self.embedding_model.embed(message["content"], "add")
                    memory_id = self._create_memory(message["content"], message_embeddings, metadata, categories=[])
                    returned_memories.append({"id": memory_id, "memory": message["content"], "event": "ADD"})
            return returned_memories

        parsed_messages = parse_messages(messages)

        custom_prompt = prompt if prompt else self.custom_prompt
        system_prompt, user_prompt = get_fact_retrieval_messages(parsed_messages, includes, excludes, custom_prompt)

        response = self.llm.generate_response(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
        )

        try:
            response = remove_code_blocks(response)
            new_retrieved_facts = json.loads(response)["facts"]
        except Exception as e:
            logging.error(f"Error in new_retrieved_facts: {e}")
            new_retrieved_facts = []

        retrieved_old_memory = []
        new_message_embeddings = {}
        for new_mem in new_retrieved_facts:
            messages_embeddings = self.embedding_model.embed(new_mem, "add")
            new_message_embeddings[new_mem] = messages_embeddings
            existing_memories = self.vector_store.search(
                query=messages_embeddings,
                limit=5,
                filters=filters,
            )
            for mem in existing_memories:
                retrieved_old_memory.append({"id": mem.id, "text": mem.payload["data"]})

        # remove same records
        retrieved_old_memory = list({item["id"]: item for item in retrieved_old_memory}.values())

        logger.info(f"Total existing memories: {len(retrieved_old_memory)}\n")

        # mapping UUIDs with integers for handling UUID hallucinations
        temp_uuid_mapping = {}
        for idx, item in enumerate(retrieved_old_memory):
            temp_uuid_mapping[str(idx)] = item["id"]
            retrieved_old_memory[idx]["id"] = str(idx)

        function_calling_prompt = get_update_memory_messages(retrieved_old_memory, new_retrieved_facts)

        try:
            new_memories_with_actions = self.llm.generate_response(
                messages=[{"role": "user", "content": function_calling_prompt}],
                response_format={"type": "json_object"},
            )
        except Exception as e:
            logging.error(f"Error in new_memories_with_actions: {e}")
            new_memories_with_actions = []

        new_memories_with_actions = self._create_categories(new_memories_with_actions, custom_categories)

        returned_memories = []
        logger.debug(f"the final new_memories_with_actions: {new_memories_with_actions}\n")
        try:
            for resp in new_memories_with_actions.get("memory", []):
                logger.info(f"the element in {resp}\n")
                try:
                    if not resp.get("text"):
                        logging.info("Skipping memory entry because of empty `text` field.")
                        continue
                    elif resp.get("event") == "ADD":
                        memory_id = self._create_memory(
                            data=resp.get("text"), existing_embeddings=new_message_embeddings, metadata=metadata, categories=resp.get("categories")
                        )
                        returned_memories.append(
                            {
                                "id": memory_id,
                                "memory": resp.get("text"),
                                "event": resp.get("event"),
                                "categories": resp.get("categories"),
                            }
                        )
                    elif resp.get("event") == "UPDATE":
                        self._update_memory(
                            memory_id=temp_uuid_mapping[resp.get("id")],
                            data=resp.get("text"),
                            existing_embeddings=new_message_embeddings,
                            metadata=metadata,
                        )
                        returned_memories.append(
                            {
                                "id": temp_uuid_mapping[resp.get("id")],
                                "memory": resp.get("text"),
                                "event": resp.get("event"),
                                "previous_memory": resp.get("old_memory"),
                            }
                        )
                    elif resp.get("event") == "DELETE":
                        self._delete_memory(memory_id=temp_uuid_mapping[resp.get("id")])
                        returned_memories.append(
                            {
                                "id": temp_uuid_mapping[resp.get("id")],
                                "memory": resp.get("text"),
                                "event": resp.get("event"),
                            }
                        )
                except Exception as e:
                    logging.error(f"Error in new_memories_with_actions: {e}")
        except Exception as e:
            logging.error(f"Error in new_memories_with_actions: {e}")

        capture_event("mem0.add", self, {"version": self.api_version, "keys": list(filters.keys())})

        return returned_memories

    def _add_to_graph(self, messages, filters, custom_node_types=None, custom_relations=None, graph_prompt=None, includes=None, excludes=None):
        added_entities = []
        if self.enable_graph:
            if filters.get("user_id") is None:
                filters["user_id"] = "user"

            data = "\n".join([msg["content"] for msg in messages if "content" in msg and msg["role"] != "system"])
            added_entities = self.graph.add(data, filters, custom_node_types, custom_relations, graph_prompt, includes, excludes)

        return added_entities

    def get(self, memory_id):
        """
        Retrieve a memory by ID.

        Args:
            memory_id (str): ID of the memory to retrieve.

        Returns:
            dict: Retrieved memory.
        """
        capture_event("mem0.get", self, {"memory_id": memory_id})
        memory = self.vector_store.get(vector_id=memory_id)
        if not memory:
            return None

        filters = {key: memory.payload[key] for key in ["user_id", "agent_id", "run_id"] if memory.payload.get(key)}

        # Prepare base memory item
        memory_item = MemoryItem(
            id=memory.id,
            memory=memory.payload["data"],
            hash=memory.payload.get("hash"),
            created_at=memory.payload.get("created_at"),
            updated_at=memory.payload.get("updated_at"),
        ).model_dump(exclude={"score"})

        # Add metadata if there are additional keys
        excluded_keys = {
            "user_id",
            "agent_id",
            "run_id",
            "hash",
            "data",
            "created_at",
            "updated_at",
            "id",
        }
        additional_metadata = {k: v for k, v in memory.payload.items() if k not in excluded_keys}
        if additional_metadata:
            memory_item["metadata"] = additional_metadata

        result = {**memory_item, **filters}

        return result

    def get_all(self, **kwargs):
        """
        List all memories.

        Parameters:
        **kwargs:
            user_id (str, optional)
            agent_id (str, optional)
            run_id (str, optional)
            limit (int, optional)

        Returns:
            list: List of all memories.
        """
        params = self._prepare_params(kwargs)
        filters = {}
        if params.get("user_id"):
            filters["user_id"] = params.get("user_id")
        if params.get("agent_id"):
            filters["agent_id"] = params.get("agent_id")
        if params.get("run_id"):
            filters["run_id"] = params.get("run_id")
        if params.get("limit"):
            limit = params.get("limit")
        else:
            limit = 100

        capture_event("mem0.get_all", self, {"limit": limit, "keys": list(filters.keys())})

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_memories = executor.submit(self._get_all_from_vector_store, filters, limit)
            future_graph_entities = executor.submit(self.graph.get_all, filters, limit) if self.enable_graph else None

            concurrent.futures.wait(
                [future_memories, future_graph_entities] if future_graph_entities else [future_memories]
            )

            all_memories = future_memories.result()
            graph_entities = future_graph_entities.result() if future_graph_entities else None

        if self.enable_graph:
            return {"results": all_memories, "relations": graph_entities}

        if self.api_version == "v1.0":
            warnings.warn(
                "The current get_all API output format is deprecated. "
                "To use the latest format, set `api_version='v1.1'`. "
                "The current format will be removed in mem0ai 1.1.0 and later versions.",
                category=DeprecationWarning,
                stacklevel=2,
            )
            return all_memories
        else:
            return {"results": all_memories}

    def _get_all_from_vector_store(self, filters, limit):
        memories = self.vector_store.list(filters=filters, limit=limit)

        excluded_keys = {
            "user_id",
            "agent_id",
            "run_id",
            "hash",
            "data",
            "created_at",
            "updated_at",
            "id",
        }
        all_memories = [
            {
                **MemoryItem(
                    id=mem.id,
                    memory=mem.payload["data"],
                    hash=mem.payload.get("hash"),
                    created_at=mem.payload.get("created_at"),
                    updated_at=mem.payload.get("updated_at"),
                ).model_dump(exclude={"score"}),
                **{key: mem.payload[key] for key in ["user_id", "agent_id", "run_id"] if key in mem.payload},
                **(
                    {"metadata": {k: v for k, v in mem.payload.items() if k not in excluded_keys}}
                    if any(k for k in mem.payload if k not in excluded_keys)
                    else {}
                ),
            }
            for mem in memories[0]
        ]
        return all_memories

    def search(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Search for memories.

        Args:
            query (str): Query to search for.
            **kwargs: 
                user_id (str, optional): ID of the user to search for. Defaults to None.
                agent_id (str, optional): ID of the agent to search for. Defaults to None.
                run_id (str, optional): ID of the run to search for. Defaults to None.
                limit (int, optional): Limit the number of results. Defaults to 100.
                filters (dict, optional): Filters to apply to the search. Defaults to None.

        Returns:
            list: List of search results.
        """
        params = self._prepare_params(kwargs)
        filters = kwargs.get("filters") or {}
        if params.get("user_id"):
            filters["user_id"] = params.get("user_id")
        if params.get("agent_id"):
            filters["agent_id"] = params.get("agent_id")
        if params.get("run_id"):
            filters["run_id"] = params.get("run_id")
        if params.get("limit"):
            limit = params.get("limit")
        else:
            limit = 100

        if not any(key in filters for key in ("user_id", "agent_id", "run_id")):
            raise ValueError("One of the filters: user_id, agent_id or run_id is required!")

        capture_event(
            "mem0.search",
            self,
            {"limit": limit, "version": self.api_version, "keys": list(filters.keys())},
        )

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_memories = executor.submit(self._search_vector_store, query, filters, limit)
            future_graph_entities = (
                executor.submit(self.graph.search, query, filters, limit) if self.enable_graph else None
            )

            concurrent.futures.wait(
                [future_memories, future_graph_entities] if future_graph_entities else [future_memories]
            )

            original_memories = future_memories.result()
            graph_entities = future_graph_entities.result() if future_graph_entities else None

        if self.enable_graph:
            return {"results": original_memories, "relations": graph_entities}

        if self.api_version == "v1.0":
            warnings.warn(
                "The current get_all API output format is deprecated. "
                "To use the latest format, set `api_version='v1.1'`. "
                "The current format will be removed in mem0ai 1.1.0 and later versions.",
                category=DeprecationWarning,
                stacklevel=2,
            )
            return original_memories
        else:
            return {"results": original_memories}

    def _search_vector_store(self, query, filters, limit):
        embeddings = self.embedding_model.embed(query, "search")
        memories = self.vector_store.search(query=embeddings, limit=limit, filters=filters)

        excluded_keys = {
            "user_id",
            "agent_id",
            "run_id",
            "hash",
            "data",
            "created_at",
            "updated_at",
            "categories",
            "id",
        }

        original_memories = [
            {
                **MemoryItem(
                    id=mem.id,
                    memory=mem.payload["data"],
                    hash=mem.payload.get("hash"),
                    created_at=mem.payload.get("created_at"),
                    updated_at=mem.payload.get("updated_at"),
                    score=mem.score, 
                    categories=mem.payload.get("categories"),
                ).model_dump(),
                **{key: mem.payload[key] for key in ["user_id", "agent_id", "run_id"] if key in mem.payload},
                **(
                    {"metadata": {k: v for k, v in mem.payload.items() if k not in excluded_keys}}
                    if any(k for k in mem.payload if k not in excluded_keys)
                    else {}
                ),
            }
            for mem in memories
        ]

        return original_memories

    def update(self, memory_id, data):
        """
        Update a memory by ID.

        Args:
            memory_id (str): ID of the memory to update.
            data (dict): Data to update the memory with.

        Returns:
            dict: Updated memory.
        """
        capture_event("mem0.update", self, {"memory_id": memory_id})

        existing_embeddings = {data: self.embedding_model.embed(data, "update")}

        self._update_memory(memory_id, data, existing_embeddings)
        return {"message": "Memory updated successfully!"}

    def delete(self, memory_id):
        """
        Delete a memory by ID.

        Args:
            memory_id (str): ID of the memory to delete.
        """
        capture_event("mem0.delete", self, {"memory_id": memory_id})
        self._delete_memory(memory_id)
        return {"message": "Memory deleted successfully!"}

    def delete_all(self, user_id=None, agent_id=None, run_id=None):
        """
        Delete all memories.

        Args:
            user_id (str, optional): ID of the user to delete memories for. Defaults to None.
            agent_id (str, optional): ID of the agent to delete memories for. Defaults to None.
            run_id (str, optional): ID of the run to delete memories for. Defaults to None.
        """
        filters = {}
        if user_id:
            filters["user_id"] = user_id
        if agent_id:
            filters["agent_id"] = agent_id
        if run_id:
            filters["run_id"] = run_id

        if not filters:
            raise ValueError(
                "At least one filter is required to delete all memories. If you want to delete all memories, use the `reset()` method."
            )

        capture_event("mem0.delete_all", self, {"keys": list(filters.keys())})
        memories = self.vector_store.list(filters=filters)[0]
        for memory in memories:
            self._delete_memory(memory.id)

        logger.info(f"Deleted {len(memories)} memories\n")

        if self.enable_graph:
            self.graph.delete_all(filters)

        return {"message": "Memories deleted successfully!"}

    def history(self, memory_id):
        """
        Get the history of changes for a memory by ID.

        Args:
            memory_id (str): ID of the memory to get history for.

        Returns:
            list: List of changes for the memory.
        """
        capture_event("mem0.history", self, {"memory_id": memory_id})
        return self.db.get_history(memory_id)

    def _create_categories(self, new_memories_with_actions, custom_categories):
        """
        为记忆创建categories标签。
        
        Args:
            new_memories_with_actions: 包含记忆和动作的字典
            custom_categories: 自定义分类标签
            
        Returns:
            处理后的new_memories_with_actions字典
        """
        # 从原始响应中解析出记忆
        try:
            new_memories_with_actions = remove_code_blocks(new_memories_with_actions)
            new_memories_with_actions = json.loads(new_memories_with_actions)
        except Exception as e:
            logging.error(f"Invalid JSON response: {e}")
            new_memories_with_actions = []
        
        # 过滤出ADD类型的记忆
        add_memories = [mem for mem in new_memories_with_actions["memory"] if mem["event"] == "ADD"]
        
        if add_memories:
            # 只对ADD类型记忆生成categories标签
            categories_generating_prompt = get_create_categories_prompt({"memory": add_memories}, custom_categories)
            memories_with_categories = self.llm.generate_response(
                messages=[{"role": "user", "content": categories_generating_prompt}],
                response_format={"type": "json_object"},
            )
            try:
                memories_with_categories = remove_code_blocks(memories_with_categories)
                memories_with_categories = json.loads(memories_with_categories)
            except Exception as e:
                logging.error(f"Invalid JSON response: {e}")
                memories_with_categories = []
            
            # 将categories合并回原始记忆中
            add_memories_dict = {mem["text"]: mem for mem in add_memories}
            for mem in memories_with_categories["memory"]:
                if mem["text"] in add_memories_dict:
                    add_memories_dict[mem["text"]]["categories"] = mem.get("categories", "")
            
            # 将非ADD类型记忆添加回结果中
            non_add_memories = [mem for mem in new_memories_with_actions["memory"] if mem["event"] != "ADD"]
            new_memories_with_actions["memory"] = add_memories + non_add_memories
            
        return new_memories_with_actions


    def _create_memory(self, data, existing_embeddings, categories, metadata=None):
        logger.info(f"Creating memory with {data=}\n")
        if data in existing_embeddings:
            embeddings = existing_embeddings[data]
        else:
            embeddings = self.embedding_model.embed(data, "add")
        memory_id = str(uuid.uuid4())
        metadata = metadata or {}
        metadata["data"] = data
        metadata["hash"] = hashlib.md5(data.encode()).hexdigest()
        metadata["created_at"] = datetime.now(pytz.timezone("US/Pacific")).isoformat()
        metadata["categories"] = categories

        self.vector_store.insert(
            vectors=[embeddings],
            ids=[memory_id],
            payloads=[metadata],
        )
        self.db.add_history(memory_id, None, data, categories, "ADD", created_at=metadata["created_at"])
        capture_event("mem0._create_memory", self, {"memory_id": memory_id})
        return memory_id

    def _update_memory(self, memory_id, data, existing_embeddings, metadata=None):
        logger.info(f"Updating memory with {data=}\n")

        try:
            existing_memory = self.vector_store.get(vector_id=memory_id)
        except Exception:
            raise ValueError(f"Error getting memory with ID {memory_id}. Please provide a valid 'memory_id'")
        prev_value = existing_memory.payload.get("data")

        new_metadata = metadata or {}
        new_metadata["data"] = data
        new_metadata["hash"] = hashlib.md5(data.encode()).hexdigest()
        new_metadata["created_at"] = existing_memory.payload.get("created_at")
        new_metadata["updated_at"] = datetime.now(pytz.timezone("US/Pacific")).isoformat()

        if "user_id" in existing_memory.payload:
            new_metadata["user_id"] = existing_memory.payload["user_id"]
        if "agent_id" in existing_memory.payload:
            new_metadata["agent_id"] = existing_memory.payload["agent_id"]
        if "run_id" in existing_memory.payload:
            new_metadata["run_id"] = existing_memory.payload["run_id"]

        if data in existing_embeddings:
            embeddings = existing_embeddings[data]
        else:
            embeddings = self.embedding_model.embed(data, "update")
        self.vector_store.update(
            vector_id=memory_id,
            vector=embeddings,
            payload=new_metadata,
        )
        logger.info(f"Updating memory with ID {memory_id=} with {data=}\n")
        self.db.add_history(
            memory_id,
            prev_value,
            data,
            None,
            "UPDATE",
            created_at=new_metadata["created_at"],
            updated_at=new_metadata["updated_at"],
        )
        capture_event("mem0._update_memory", self, {"memory_id": memory_id})
        return memory_id

    def _delete_memory(self, memory_id):
        logger.info(f"Deleting memory with {memory_id=}\n")
        existing_memory = self.vector_store.get(vector_id=memory_id)
        prev_value = existing_memory.payload["data"]
        self.vector_store.delete(vector_id=memory_id)
        self.db.add_history(memory_id, prev_value, None, None, "DELETE", is_deleted=1)
        capture_event("mem0._delete_memory", self, {"memory_id": memory_id})
        return memory_id

    def reset(self):
        """
        Reset the memory store.
        """
        logger.warning("Resetting all memories\n")
        self.vector_store.delete_col()
        self.vector_store = VectorStoreFactory.create(
            self.config.vector_store.provider, self.config.vector_store.config
        )
        self.db.reset()
        capture_event("mem0.reset", self)

    def chat(self, query):
        raise NotImplementedError("Chat function not implemented yet.")
