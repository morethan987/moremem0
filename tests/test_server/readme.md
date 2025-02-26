# 服务器使用指南

## 基本用法

### 添加记忆
```python
from mem0.client_simplified.main import MemoryClient # 引入客户端文件

client = MemoryClient(host="http://...") # 实例化客户端

# 配置测试消息
test_messages = [
    {"role": "user", "content": "I like to eat pizza, I have a dog named Pitter."}
]

# 添加记忆并打印返回消息
print(client.add(test_messages, user_id="xxx")) # 自己拟定一个user_id
```

### 返回的消息说明

直接运行上面的代码之后，你的终端会收到类似下面的http响应：
```json
{
  "results": [
    {
      "id": "4e737279-653f-4395-858f-7e1385c7444a",
      "memory": "Likes to eat pizza",
      "event": "ADD",
      "categories": [
        "food"
      ]
    },
    {
      "id": "8e531993-d958-4e4d-9d2c-bdeacb02b6d3",
      "memory": "Has a dog named Pitter",
      "event": "ADD",
      "categories": [
        "family",
        "misc"
      ]
    }
  ],
  "relations": {
    "deleted_relations": [],
    "added_triples": [
      [
        {
          "source": "morethan",
          "source_labels": [
            "person"
          ],
          "relationship": "likes_to_eat",
          "target": "pizza",
          "target_labels": [
            "food"
          ]
        }
      ],
      [
        {
          "source": "morethan",
          "source_labels": [
            "person"
          ],
          "relationship": "has_a_dog_named",
          "target": "pitter",
          "target_labels": [
            "pet",
            "dog"
          ]
        }
      ]
    ]
  }
}
```

这里做一下参数说明：
1. 整个JSON包括两个部分："results"和"relations"；"results"内部的数据表示向量数据库返回的信息；"relations"内部的数据表示图数据库返回的信息；类型是一个字典构成的列表
2. "results"中返回的信息相对简洁明了，不做过多解释
3. "relations"中返回的信息有："deleted_relations"表示被删除的旧有数据；"added_triples"表示新增的`三元组`；三元组是图数据库里面的一个术语，不清楚的自行搜索🔍

### 记忆搜索
```python
# 执行记忆搜索并打印返回消息
print(client.search("What do I like to eat?", user_id='xxx')) # 填你自己的用户名
```

http响应的格式如上👆

### 查看存储的所有记忆
```python
# 查看存储到的所有记忆
print(client.get_all(user_id="xxx")) # 填你自己的用户名
```

### 删除所有的记忆
```python
# 删除某个用户的所有的记忆
print(client.delete_all(user_id="xxx")) # 填你自己的用户名，别把别人的给删了
```

## 进阶用法--数据库设计

### 向量数据库

针对向量数据库有一个专门的控制字段`categories`，让AI提取的记忆的类别只包含你设置的类别；注意不要**强AI所难**，如果你写的类别和你的消息完全不匹配，只有两种情况会发生：
1. AI生成了一个你没有定义的类别
2. AI直接用自然语言回应请求，导致参数解析失败

如果你不写，默认的类别如下：
- personal_details: Information about the individual, such as name, age, and contact details.
- family: Details regarding family members and relationships.
- professional_details: Work-related information, including career, job title, and workplace.
- sports: Involvement in physical activities, games, and fitness.
- travel: Travel experiences, destinations, and trip preferences.
- food: Preferences and experiences related to food, cooking, and dining.
- music: Musical tastes, genres, artists, and listening habits.
- health: Physical and mental health status, medical history, and wellness routines.
- technology: Interest in tech, gadgets, software, and innovations.
- hobbies: Recreational activities and interests pursued in free time.
- fashion: Clothing, style preferences, and trends.
- entertainment: Interests in movies, shows, books, and other media.
- milestones: Important life events, achievements, and significant moments.
- user_preferences: Individual preferences for various aspects of life, like routine, activities, and choices.
- misc: Other miscellaneous information not covered by other categories.

如果你要对类别进行控制，请参照一下例子：
```python
from mem0.client_simplified.main import MemoryClient # 引入客户端文件

client = MemoryClient(host="http://...") # 实例化客户端

# 自定义类别
custom_categories = [
    {"personal_information": "Basic information about the user including name, preferences, and personality traits"},
    {"health": "Physical and mental health status, medical history, and wellness routines"}
]

# 主配置；你只改了向量数据库的参数，所以其他的都不用改
config = {
    "vector_store": {
        "custom_categories": custom_categories,
    },
}

# 加载自定义参数
client.configure(config)

# 其他操作
```

### 图数据库

图数据库有两个控制参数`custom_node_types`和`custom_relations`，分别控制图数据库中的实体结点的标签和图数据库中的关系类别
```python
from mem0.client_simplified.main import MemoryClient # 引入客户端文件

client = MemoryClient(host="http://...") # 实例化客户端

custom_node_types = [
    {"food_preference": "User's preference for food"},
    {"pet": "stands for the all kinds of pets"},
    {"health_condition": "Physical and mental health status, medical history, and wellness routines"},
    {"person": "The person mentioned by user. The user himself also belong to this type"}
]

custom_relations = [
    {"likes_to_eat": "Express user's preference for food"},
    {"has_a_pet": "Express the user has a pet"},
    {"with_health_condition": "Express user has a specific health condition"}
]

config = {
    "graph_store": {
        "custom_node_types": custom_node_types,
        "custom_relations": custom_relations,
    },
}

# 加载自定义参数
client.configure(config)

# 其他操作
```

### ADD级控制

你可以在命令`client.add()`中填入更多的参数，用来实现更强的控制；比如上面提及的👆
ADD级参数的优先级更高，会默认覆盖config参数中的设置

ADD独有的控制参数`includes`和`excludes`
```python
from mem0.client_simplified.main import MemoryClient # 引入客户端文件

client = MemoryClient(host="http://...") # 实例化客户端

# 我这里只写excludes, includes 的格式类似
excluded_info = {
    "vector": "1. 用户对于食物的偏好",
    "graph": "1. 用户对于食物的偏好\n2. 用户的年龄"
}

test_messages = [
    {"role": "user", "content": "I like to eat pizza, I have a dog named Pitter."}
]

print(m.add(test_messages, user_id="morethan", excludes="excluded_info"))
```

通过这些硬性的控制参数，我们就可以把传统数据库的设计融入到这个AI驱动的数据库里面，让数据库的可控性更好，并且能够让一般的工具能够像访问传统数据库一样访问这个AI数据库。

例如，经过精心设计，给出了一个存储日程数据的图数据库的方案：结点类型有xxx，关系类型有xxx；由于经过精心设计，用户的输入大部分情况下都应该存在正确的逻辑来存储，因此AI就能够按照我们的设计去操作数据库：存储、更新、删除、提取等

当正常的应用想要访问这个AI数据库的时候，我们也能够根据自己的设计，来过滤出想要的数据，比如经过精心设计的类别中有food这个类，那么我就可以绕开AI，直接对数据库发送命令，返回所有food类的记忆

### 自定义提示词

自定提示词的格式请参考项目根目录中的`README.md`

提示词注入的方式与上面的`categories`和`custom_relations`类似

为什么要开放这个参数？因为目前的提示词好没有经过[SPO](https://github.com/geekan/MetaGPT/tree/main/examples/spo)进行强化微调，后期可能会优化