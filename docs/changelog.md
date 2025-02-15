# 更新日志

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

