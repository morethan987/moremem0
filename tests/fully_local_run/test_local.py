import os
from dotenv import load_dotenv
from mem0 import Memory
from format_results import format_search_results

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

# 定制化提示词，优先级add级局部提示词>主配置中的custom_prompt>系统原生提示词:configs/prompts.py/FACT_RETRIEVAL_PROMPT
# 定制化全局提示词
custom_prompt = """
Please only extract entities containing customer support information, order details, and user information. 
Here are some few shot examples:

Input: Hi.
Output: {{"facts" : []}}

Input: The weather is nice today.
Output: {{"facts" : []}}

Input: My order #12345 hasn't arrived yet.
Output: {{"facts" : ["Order #12345 not received"]}}

Input: I'm John Doe, and I'd like to return the shoes I bought last week.
Output: {{"facts" : ["Customer name: John Doe", "Wants to return shoes", "Purchase made last week"]}}

Input: I ordered a red shirt, size medium, but received a blue one instead.
Output: {{"facts" : ["Ordered red shirt, size medium", "Received blue shirt instead"]}}

Return the facts and customer information in a json format as shown above.
"""

# 定制化局部提示词，作用在向量数据库上
add_prompt = """
这是一个局部提示词
"""

# 定制化局部提示词，作用在图数据库上
add_graph_prompt = """
这是一个局部提示词
"""

# 主配置
config = {
    "vector_store": qdrant_config,
    "graph_store": neo4j_config,
    "llm": aliyun_config,
    "embedder": siliconflow_config,
    # "custom_prompt": custom_prompt,
    "version": "v1.1",
}

# Initialize Memory with the configuration
m = Memory.from_config(config)

initial_messages = [
    {"role": "user", "content": "你好👋我叫Morethan，我很喜欢吃鱼"},
    {"role": "assistant", "content": "你好呀，Morethan！很高兴认识你。吃鱼是个很棒的选择呢，鱼肉不仅鲜美，还富含优质蛋白质、不饱和脂肪酸，对身体有很多好处。你最喜欢吃什么鱼，或者用什么方式烹饪鱼呢？"}
]

test_messages = [
    {"role": "user", "content": "我30分钟后要背15个单词，记得提醒我"},
    {"role": "assistant", "content": "好的，30分钟后我会提醒你。"}
]

# 较全的add命令
# m.add(initial_messages, user_id="morethan", prompt=add_prompt, graph_prompt=add_graph_prompt, metadata={"food": "fish"})

# print(m.add(initial_messages, user_id="morethan", metadata={"food": "fish"}))
# m.add("I like pizza", user_id="morethan")

# print(m.add(test_messages, user_id="morethan"))

results = m.search("What will I do next?", user_id='morethan')

print(format_search_results(results))
