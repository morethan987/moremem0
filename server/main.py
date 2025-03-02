import os
from fastapi import FastAPI, HTTPException, Query, Path
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List, Any, Dict
from mem0 import Memory
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# 从环境变量获取数据库配置或使用默认值
NEO4J_HOST = os.getenv("NEO4J_HOST", "localhost")
NEO4J_PORT = os.getenv("NEO4J_PORT", "7687")
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = os.getenv("QDRANT_PORT", "6333")

# 默认配置
DEFAULT_CONFIG = {
    "version": "v1.1",
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "collection_name": "test",
            "host": QDRANT_HOST,
            "port": int(QDRANT_PORT),
            "embedding_model_dims": 1024
        }
    },
    # "graph_store": {
    #     "provider": "neo4j",
    #     "config": {
    #         "url": f"neo4j://{NEO4J_HOST}:{NEO4J_PORT}",
    #         "username": "neo4j",
    #         "password": "mo123456789"
    #     }
    # },
    "llm": {
        "provider": "aliyun",
        "config": {
            "model": "qwen-max-latest",
            "temperature": 0.0,
            "top_p": 0.1,
            "max_tokens": 8000,
            "aliyun_base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1"
        }
    },
    "embedder": {
        "provider": "siliconflow",
        "config": {
            "model": "Pro/BAAI/bge-m3",
            "siliconflow_base_url": "https://api.siliconflow.cn/v1/embeddings"
        }
    },
}

# 初始化Memory实例
MEMORY_INSTANCE = Memory.from_config(DEFAULT_CONFIG)

app = FastAPI(
    title="Mem0 REST APIs",
    description="A REST API for managing and searching memories for your AI Agents and Apps.",
    version="1.0.0",
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://frp-put.com:42344", "http://localhost:4173"],  # 允许的前端源
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有HTTP方法
    allow_headers=["*"],  # 允许所有请求头
)

class Message(BaseModel):
    role: str = Field(..., description="Role of the message (user or assistant).")
    content: str = Field(..., description="Message content.")


class MemoryCreate(BaseModel):
    messages: List[Message] = Field(..., description="List of messages to store.")
    user_id: Optional[str] = None
    agent_id: Optional[str] = None
    run_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class SearchRequest(BaseModel):
    query: str = Field(..., description="Search query.")
    user_id: Optional[str] = None
    run_id: Optional[str] = None
    agent_id: Optional[str] = None
    filters: Optional[Dict] = None


@app.post("/configure", summary="Configure Mem0")
def set_config(config: Dict[str, Any]):
    """Set memory configuration."""
    global MEMORY_INSTANCE
    
    # 定义一个深度合并字典的函数
    def deep_merge(default_dict: Dict[str, Any], user_dict: Dict[str, Any]) -> Dict[str, Any]:
        """递归合并两个字典，用户字典中的值优先，缺失值用默认字典填充"""
        merged = default_dict.copy()  # 创建默认字典的副本
        
        for key, user_value in user_dict.items():
            # 如果两个字典中的值都是字典，则递归合并
            if key in default_dict and isinstance(default_dict[key], dict) and isinstance(user_value, dict):
                merged[key] = deep_merge(default_dict[key], user_value)
            else:  # 否则直接使用用户字典中的值
                merged[key] = user_value
        return merged
    
    # 合并用户配置和默认数据库配置
    merged_config = deep_merge(DEFAULT_CONFIG, config)
    # 传递环境变量
    merged_config["vector_store"]["config"]["host"] = QDRANT_HOST
    merged_config["vector_store"]["config"]["port"] = int(QDRANT_PORT)
    merged_config["graph_store"]["config"]["url"] = f"neo4j://{NEO4J_HOST}:{NEO4J_PORT}"
    
    MEMORY_INSTANCE = Memory.from_config(merged_config)
    return {"message": "Configuration set successfully"}


@app.post("/memories", summary="Create memories")
def add_memory(memory_create: MemoryCreate):
    """Store new memories."""
    if not any([memory_create.user_id, memory_create.agent_id, memory_create.run_id]):
        raise HTTPException(
            status_code=400, detail="At least one identifier (user_id, agent_id, run_id) is required."
        )

    params = {k: v for k, v in memory_create.model_dump().items() if v is not None and k != "messages"}
    try:
        response = MEMORY_INSTANCE.add(messages=[m.model_dump() for m in memory_create.messages], **params)
        return JSONResponse(content=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/memories", summary="Get memories")
def get_all_memories(
    user_id: Optional[str] = None,
    run_id: Optional[str] = None,
    agent_id: Optional[str] = None,
):
    """Retrieve stored memories."""
    if not any([user_id, run_id, agent_id]):
        raise HTTPException(status_code=400, detail="At least one identifier is required.")
    try:
        params = {k: v for k, v in {"user_id": user_id, "run_id": run_id, "agent_id": agent_id}.items() if v is not None}
        return MEMORY_INSTANCE.get_all(**params)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/memories/{memory_id}", summary="Get a memory")
def get_memory(memory_id: str):
    """Retrieve a specific memory by ID."""
    try:
        return MEMORY_INSTANCE.get(memory_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/search", summary="Search memories")
def search_memories(search_req: SearchRequest):
    """Search for memories based on a query."""
    try:
        params = {k: v for k, v in search_req.model_dump().items() if v is not None and k != "query"}
        return MEMORY_INSTANCE.search(query=search_req.query, **params)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/memories/{memory_id}", summary="Update a memory")
def update_memory(memory_id: str, updated_memory: Dict[str, Any]):
    """Update an existing memory."""
    try:
        return MEMORY_INSTANCE.update(memory_id=memory_id, data=updated_memory)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/memories/{memory_id}/history", summary="Get memory history")
def memory_history(memory_id: str):
    """Retrieve memory history."""
    try:
        return MEMORY_INSTANCE.history(memory_id=memory_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/memories/{memory_id}", summary="Delete a memory")
def delete_memory(memory_id: str):
    """Delete a specific memory by ID."""
    try:
        MEMORY_INSTANCE.delete(memory_id=memory_id)
        return {"message": "Memory deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/memories", summary="Delete all memories")
def delete_all_memories(
    user_id: Optional[str] = None,
    run_id: Optional[str] = None,
    agent_id: Optional[str] = None,
):
    """Delete all memories for a given identifier."""
    if not any([user_id, run_id, agent_id]):
        raise HTTPException(status_code=400, detail="At least one identifier is required.")
    try:
        params = {k: v for k, v in {"user_id": user_id, "run_id": run_id, "agent_id": agent_id}.items() if v is not None}
        MEMORY_INSTANCE.delete_all(**params)
        return {"message": "All relevant memories deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/reset", summary="Reset all memories")
def reset_memory():
    """Completely reset stored memories."""
    try:
        MEMORY_INSTANCE.reset()
        return {"message": "All memories reset"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/", summary="Redirect to the OpenAPI documentation", include_in_schema=False)
def home():
    """Redirect to the OpenAPI documentation."""
    return RedirectResponse(url='/docs')
