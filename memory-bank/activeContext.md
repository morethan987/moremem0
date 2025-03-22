# Active Context

This file tracks the project's current status, including recent changes, current goals, and open questions.
2025-03-20 23:30:20 - Initial creation of Memory Bank

## Current Focus

* Memory Bank初始化
* 项目结构梳理与文档化
* 各子项目关系的明确定义


## Server Local实现分析 (2025-03-22 10:56:00)

1. 核心组件：
   * FastAPI REST API服务器
   * Docker容器化配置
   * Neo4j和Qdrant数据库集成
   * 环境变量配置管理

2. API功能：
   * 记忆的CRUD操作
   * 搜索功能
   * 配置管理
   * 记忆历史跟踪

3. 部署特性：
   * Docker Compose多容器编排
   * 等待脚本确保依赖服务就绪
   * 数据卷持久化
   * 网络隔离

4. 配置管理：
   * 多AI服务提供商支持
   * 环境变量驱动配置
   * 递归配置合并
   * 默认值处理


## Recent Changes

## 核心功能分析 (2025-03-20 23:35:40)

### Python SDK (mem0) 主要组件：

1. MemoryClient (同步客户端):
   * 提供完整的记忆管理API
   * 支持记忆的增删改查
   * 支持批量操作
   * 提供项目和webhook管理
   * 包含用户和实体管理

2. AsyncMemoryClient (异步客户端):
   * 异步版本的MemoryClient
   * 使用httpx.AsyncClient实现
   * 保持与同步客户端功能对齐

3. 主要API功能：
   * add - 添加新记忆
   * get/get_all - 获取记忆
   * search - 搜索记忆
   * update/batch_update - 更新记忆

### 服务器端实现分析 (2025-03-20 23:40:00):

1. 技术栈：
   * FastAPI框架
   * Pydantic数据验证
   * 环境变量配置
   * RESTful API设计

2. 核心功能：
   * 完整的CRUD API接口
   * 配置管理和动态更新
   * 内存检索和搜索
   * 历史记录追踪

3. 存储集成：
   * Qdrant向量数据库
   * Neo4j图数据库（可选）
   * SQLite历史记录

4. AI集成：
   * 阿里云Qwen大模型
   * Silicon Flow嵌入模型
   * 自定义提示词系统

### TypeScript SDK分析 (2025-03-20 23:38:20):

1. 核心实现特点：
   * 基于HTTP API实现的客户端
   * 使用axios和fetch处理请求
   * 支持浏览器和Node.js环境
   * TypeScript类型系统提供更好的开发体验

2. 主要功能对比：
   * 与Python SDK功能对齐
   * 完整的内存管理API支持
   * 支持批量操作
   * 包含项目和webhook管理

3. 独特设计：
   * 包装器模式用于遥测事件捕获
   * 组织和项目管理更完善
   * API版本控制更严格

4. 技术差异：
   * Python SDK: 完整的本地实现，包含向量存储和图存储
   * TypeScript SDK: 专注于API客户端，依赖服务端实现
   * Python SDK支持更多的本地功能（如自定义分类、关系推理）
   * TypeScript SDK提供更好的类型安全和API接口定义

### Memory类核心功能 (2025-03-20 23:36:30):

1. 多存储后端支持：
   * 向量存储 - 用于相似度搜索
   * 图存储 - 用于关系存储
   * SQLite - 用于历史记录

2. 高级功能：
   * 自动推理 (infer) - 使用LLM分析和处理输入数据
   * 分类系统 - 支持自定义分类标签
   * 并发处理 - 使用ThreadPoolExecutor处理向量和图操作

3. 可配置特性：
   * 自定义提示词
   * 自定义分类系统
   * 自定义关系类型
   * 可选的图存储功能

4. 集成功能：
   * 事件跟踪 (telemetry)
   * 版本控制 (v1.0/v1.1)
   * 完整的错误处理
   * delete/batch_delete - 删除记忆
   * history - 获取记忆历史
   * export - 导出记忆数据
* 2025-03-20 23:32:00 - Memory Bank全部核心文件创建完成
* 下一步需要深入分析各个子项目的具体实现

* 2025-03-20 23:30:20 - 创建Memory Bank
* 2025-03-20 23:30:20 - 完成productContext.md初始化

## Open Questions/Issues

* SDK之间的功能对齐程度如何？
* 前后端接口的标准化程度如何？
* 各个示例项目的完整性和可用性如何？
* 测试覆盖率是否充分？
* Docker部署的可靠性如何？