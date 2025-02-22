import os
from dotenv import load_dotenv
from mem0 import Memory
from format_results import format_search_results
from datetime import datetime

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
        "api_key": os.getenv('SILICONFLOW_API_KEY'),
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

# Initialize Memory with the configuration
m = Memory.from_config(config)

initial_messages = [
    {"role": "user", "content": "你好👋我叫Morethan，我很喜欢吃鱼"},
    {"role": "assistant", "content": "你好呀，Morethan！很高兴认识你。吃鱼是个很棒的选择呢，鱼肉不仅鲜美，还富含优质蛋白质、不饱和脂肪酸，对身体有很多好处。你最喜欢吃什么鱼，或者用什么方式烹饪鱼呢？"},
    {"role": "user", "content": "我喜欢吃披萨，我今年12岁，我经常感冒"}
]

excluded_info = {
    "vector": "1. 用户对于食物的偏好",
    "graph": "1. 用户对于食物的偏好\n2. 用户的年龄"
}

test_messages = [
    {"role": "user", "content": "I like to eat pizza, I have a dog named Pitter."}
]

# 较全的add命令
# m.add(initial_messages, user_id="morethan", prompt=add_prompt, graph_prompt=add_graph_prompt, metadata={"food": "fish"}, , includes=included_info, excludes=excluded_info, custom_categories=custom_categories, custom_node_types=custom_node_types, custom_relations=custom_relations)

print(m.add(test_messages, user_id="morethan"))
# m.add("I like pizza", user_id="morethan")

# print(m.add(test_messages, user_id="morethan", custom_categories=custom_categories))

# results = m.search("What do you know about me?", user_id='morethan')
# print(format_search_results(results))
