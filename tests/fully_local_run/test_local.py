import os
from dotenv import load_dotenv
from mem0 import Memory

# 加载 .env 文件
load_dotenv()

# 向量数据库
qdrant_config = {
    "provider": "qdrant",
    "config": {
        "collection_name": "test",
        "host": "localhost",
        "port": 6333,
        "embedding_model_dims": 1024,  # Change this according to your local model's dimensions
    },
}

# 语言模型
deepseek_config = {
    "provider": "deepseek",
    "config": {
        "model": "deepseek-chat",
        "temperature": 0.5,
        "top_p": 0.5,
        "max_tokens": 8000,
        "ollama_base_url": "https://api.deepseek.com/v1",  # Ensure this URL is correct
        "api_key": os.getenv('DEEPSEEK_API_KEY'),
    },
}
aliyun_config = {
    "provider": "aliyun",
    "config": {
        "model": "qwen-max-latest",
        "temperature": 0.5,
        "top_p": 0.5,
        "max_tokens": 8000,
        "ollama_base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",  # Ensure this URL is correct
        "api_key": os.getenv('ALIYUN_API_KEY'),
    },
}

# 嵌入模型
siliconflow_config = {
    "provider": "siliconflow",
    "config": {
        "model": "Pro/BAAI/bge-m3",
        "siliconflow_base_url": "https://api.siliconflow.cn/v1/embeddings",
        "api_key": os.getenv('SILICONFLOW_API_KEY'),
    },
}

config = {
    "vector_store": qdrant_config,
    "llm": deepseek_config,
    "embedder": siliconflow_config,
}

# Initialize Memory with the configuration
m = Memory.from_config(config)

messages = [
    {"role": "user", "content": "Hi, I'm Morethan. I'm a vegetarian and I'm allergic to nuts."},
    {"role": "assistant", "content": "Hello Morethan! I've noted that you're a vegetarian and have a nut allergy. I'll keep this in mind for any food-related recommendations or discussions."}
]

# To use the latest output_format, set the output_format parameter to "v1.1"
# m.add(messages, user_id="morethan", metadata={"food": "vegan"})

# Retrieve memories
memories = m.get_all(user_id="morethan")
print(memories)