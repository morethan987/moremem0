from mem0.client_simplified.main import MemoryClient
from dotenv import load_dotenv
import os

# 加载 .env 文件
load_dotenv()

client = MemoryClient(host=os.getenv("HOST_URL")) # 实例化客户端

# 语言模型
deepseek_config = {
    "provider": "deepseek",
    "config": {
        "model": "deepseek-chat",
        "temperature": 0.0, # 温度设为0.0，防止AI作妖
        "top_p": 0.1, # 设为0.1，防止AI作妖
        "max_tokens": 8000,
        "deepseek_base_url": "https://api.deepseek.com/v1",  # Ensure this URL is correct
    },
}
aliyun_config = {
    "provider": "aliyun",
    "config": {
        "model": "qwen-max-latest",
        "temperature": 0.0, # 温度设为0.0，防止AI作妖
        "top_p": 0.1, # 设为0.1，防止AI作妖
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
    },
}

custom_categories = [
    {"personal_information": "Basic information about the user including name, preferences, and personality traits"},
    {"health": "Physical and mental health status, medical history, and wellness routines"}
]

# 向量数据库
qdrant_config = {
    "provider": "qdrant",
    "config": {
        "collection_name": "test",
        "host": "localhost",
        "port": 6333,
        "embedding_model_dims": 1024,  # Change this according to your local model's dimensions
    },
    # 针对向量数据库的自定义提示词
    # "custom_prompt": custom_prompt_for_vector,
    "custom_categories": custom_categories,
}

# 也可以在graph_store的配置中直接设置，避免add指令过于复杂
custom_node_types = [
    {"food_preference": "User's preference for food"},
    {"pet": "stands for the all kinds of pets"},
    {"health_condition": "Physical and mental health status, medical history, and wellness routines"},
    {"person": "The person mentioned by user. The user himself also belong to this type"}
]

# 也可以在graph_store的配置中直接设置，避免add指令过于复杂
custom_relations = [
    {"likes_to_eat": "Express user's preference for food"},
    {"has_a_pet": "Express the user has a pet"},
    {"with_health_condition": "Express user has a specific health condition"}
]

# 图数据库
neo4j_config = {
    "provider": "neo4j",
    "config": {
        "url": "neo4j://localhost:7687",
        "username": "neo4j",
        "password": "mo123456789"
    },
    # "llm": deepseek_config,
    # 针对图数据库的自定义提示词
    # "custom_prompt": custom_prompt_for_graph,
    "custom_node_types": custom_node_types,
    "custom_relations": custom_relations,
}

# 主配置
config = {
    "vector_store": qdrant_config,
    "graph_store": neo4j_config,
    "llm": aliyun_config,
    "embedder": siliconflow_config,
    "version": "v1.1",
}

# 加载自定义参数
client.configure(config)

# 配置测试消息
test_messages = [
    {"role": "user", "content": "I like to eat pizza, I have a dog named Pitter."}
]

# 添加记忆并打印返回消息
print(client.add(test_messages, user_id="morethan"))

# # 执行记忆搜索并打印返回消息
# print(client.search("What do I like to eat?", user_id='morethan'))

# # 查看存储到的所有记忆
# print(client.get_all(user_id="morethan"))

# # 删除某个用户的所有的记忆
# print(client.delete_all(user_id="morethan"))