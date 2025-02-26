# 更新日志

## 2025-02-26

### morethan987

- 实践证明`mem0\configs\vector_stores\qdrant.py`中的奇怪的命令确实是会影响服务器的启动：`QdrantClient: ClassVar[type] = QdrantClient`；并且暂时没有想到什么好的解决警告的方案

## 2025-02-25

### morethan987

- 配置服务器的外网端口

- 编写服务器使用指南`tests\test_server\readme.md`

## 2025-02-24

### morethan987

- 解决一个历史遗留警告`mem0\configs\vector_stores\qdrant.py`

## 2025-02-24

### morethan987

- 本地Docker部署，成功收到http响应

## 2025-02-23

### morethan987

- 官方更新#2247

## 2025-02-22

### morethan987

- 跟随官方更新：创建`server`文件夹
- 更新`vector_store`和`graph_store`的接口信息，支持传入定制化提示词、定制类别（向量数据库）、定制实体标签和关系（图数据库），避免`add`方法参数过于复杂
- 更新`README.md`

## 2025-02-21

### morethan987

- 原仓库更新#2235
- 在`vector_store`和`graph_store`中添加个性化提示词功能
- 在`add`中新增`custom_node_types`和`custom_relations`，用来严格调控图数据库的存储格式；如果不填的话会让AI自主创建，不会报错，但不便于控制
- **累计更新到现在**，从功能上实现了图数据库和向量数据库存储内容的可控分离，让传统的数据库设计的方法能够很好地在这个系统中执行；利用AI强大处理能力直接操控数据库的同时，也保留了传统方式访问数据库的可行性

## 2025-02-20

### morethan987

- 原仓库更新，支持opensearch；#2211
- 添加`categories`字段，并同时应用到两种数据库中；但是图数据库中实体的类别直接用偏好的类别来强行提取似乎不合适

## 2025-02-19

### morethan987

- 更新`mem0/memory/graph_memory.py`中的一些令人费解的命名，引入了`triple`三元组的概念
- 梳理图数据库存储信息流程
- 原仓库更新#2220和#2218，同步微调了`mem0/configs/prompts.py`的提示词；更多多模态模型的支持等待官方更新
- 更新接口参数，使用`**kwargs`便于后续添加新参数
- `add`方法中新增`includes`和`excludes`参数，用于调控AI提取的信息；并且向量数据库和图数据库的调控分开；语法详见`test_local.py`
- 官方更新#2225：Webhook 支持（虽然我不知道这是什么意思🤔）
- 更改`mem0\memory\graph_memory.py`中`_search_graph_db`函数的返回结果名称为`triples`

## 2025-02-18

### morethan987

- 原仓库issue#2165
- 解决结构化工具调用时json格式输出错误，原因是`graphs/tools.py/RELATIONS_STRUCT_TOOL`中的错误拼写
- 新增`graphs/utils.py/EXTRACT_ENTITIES_PROMPT`，将原本在`mem0/memory/graph_memory.py`中的提示词统一管理
- `mem0/memory/graph_memory.py`中新增`structured_output_provider`统一管理支持结构化输出的供应商
- 原仓库更新#2216和#2219

## 2025-02-17

### morethan987

- 原仓库更新#2217
- 加入了对于多语言分片的支持，即引入包`microtokenizer`
- 正在研究图数据数据提取相关度排序错误的问题

## 2025-02-16

### morethan987

- 感谢原mem0的PR：#1998；全局自定义提示词可以被add方法中的局部提示词覆盖
- 感谢原mem0的PR：#2179；改进了一些提示词和变量命名
- 阿里云支持工具调用，在graph_memory.py/_retrieve_nodes_from_data中新增了aliyun
- 改变模型的温度：温度设为0.0，top-p设置为0.1，防止AI作妖
- 分析图数据库查询不稳定的原因：实体的提取依赖用户查询和语言模型，用户查询可能不包含想要的实体，语言模型可能产生幻觉
- 查询结果人性化函数：`format_results.py`
- 更改`graph_memory`中的实体提取提示词，解决了图数据库search失败的问题
- 在系统提示词中注入当前具体时间信息
- 增加`test_local`中的多级提示词接口并说明覆盖规则

## 2025-02-15

### morethan987

- 更新Neo4j的Python包依赖，原依赖马上就要废弃了
- 更改Neo4j的配置，接入本地数据库
- 本地数据库配置详见：[Neo4j本地部署](https://morethan987.github.io/blog/neo4j-basics/#%E5%AE%89%E8%A3%85)
- 修改pyproject.toml中的项目名称
- 在.env.example中添加注释说明
- 针对图数据库专用语言模型配置产生API_KEY冲突问题进行说明；见test_local.py中的注释说明
- 解决graph_memory.py中图数据库存储专用模型与外部主配置模型冲突问题
- 更改包名为`moremem0`并同步修改一些文件

- 开发vercel-ai-sdk，接入新的模型供应商
- 同步更新了测试配置文件`config/test-config.ts`和`example/index.ts`
- 编写了说明文档

## 2025-02-14

### morethan987

- 删除docs文件夹中的文件，这些文件可以在官方文档网站中查看
- 添加一个`changelog.md`文档，用来记录相对于官方的更新细节
- 创建`test_local.py`文件，用来测试本地数据库连接情况
- 新增嵌入模型供应商：`siliconflow.py`；新增语言模型供应商：`zhipu.py`, `aliyun.py`

