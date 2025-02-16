import os
from dotenv import load_dotenv
from mem0 import Memory

# 加载 .env 文件
load_dotenv()

# 语言模型的API_KEY请统一填写在.env文件中，系统会自动读取；
# 不要进行额外的手动输入，可能会导致API_KEY冲突
# 系统内部的API_KEY使用的是一个统一的变量，因此手动输入可能会发生冲突

# 语言模型
deepseek_config = {
    "provider": "deepseek",
    "config": {
        "model": "deepseek-chat",
        "temperature": 0.0, # 温度设为0.0，防止AI作妖
        "top_p": 0.5,
        "max_tokens": 8000,
        "deepseek_base_url": "https://api.deepseek.com/v1",  # Ensure this URL is correct
    },
}
aliyun_config = {
    "provider": "aliyun",
    "config": {
        "model": "qwen-max-latest",
        "temperature": 0.0, # 温度设为0.0，防止AI作妖
        "top_p": 0.5,
        "max_tokens": 8000,
        "aliyun_base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",  # Ensure this URL is correct
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

# 图数据库
neo4j_config = {
    "provider": "neo4j",
    "config": {
        "url": "neo4j://localhost:7687",
        "username": "neo4j",
        "password": "mo123456789"
    },
    # "llm": deepseek_config,
}

# 主配置
config = {
    "vector_store": qdrant_config,
    "graph_store": neo4j_config,
    "llm": aliyun_config,
    "embedder": siliconflow_config,
    "version": "v1.1",
}

# Initialize Memory with the configuration
m = Memory.from_config(config)

initial_messages = [
    {"role": "user", "content": "你好👋我叫Morethan，我很喜欢吃鱼"},
    {"role": "assistant", "content": "你好呀，Morethan！很高兴认识你。吃鱼是个很棒的选择呢，鱼肉不仅鲜美，还富含优质蛋白质、不饱和脂肪酸，对身体有很多好处。你最喜欢吃什么鱼，或者用什么方式烹饪鱼呢？"}
]

# print(m.add(initial_messages, user_id="morethan", metadata={"food": "fish"}))
# m.add("I like pizza", user_id="morethan")

print(m.search("我喜欢吃什么？", user_id='morethan'))
