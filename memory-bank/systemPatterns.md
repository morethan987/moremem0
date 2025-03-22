# System Patterns

This file documents recurring patterns and standards used in the project.
2025-03-20 23:31:30 - Initial creation of Memory Bank

## Coding Patterns

1. 依赖管理模式：
   * Python项目使用poetry进行依赖管理
   * JavaScript项目使用pnpm进行依赖管理

2. SDK实现模式：
   * 双语言SDK实现（Python/TypeScript）
   * 保持功能对齐
   * 各自生态系统最佳实践

3. 服务部署模式：
   * Docker容器化部署
   * nginx反向代理
   * 环境变量配置

## Architectural Patterns

1. 分层架构：
   * 核心SDK层（mem0, mem0-ts）
   * 服务层（server）
   * 前端展示层（examples）
   * 测试验证层（tests）

2. 前后端分离：
   * 后端API服务
   * 独立前端项目
   * Vercel AI SDK集成

3. 模块化设计：
   * 独立的子项目
   * 清晰的职责划分
   * 松耦合架构

## Testing Patterns

1. 测试类型：
   * 单元测试
   * 集成测试
   * 部署测试


## 服务器架构模式 (2025-03-20 23:42:50)

1. API设计模式：
   * RESTful资源命名
   * 统一的错误处理
   * 请求参数验证
   * 响应格式标准化

2. 配置管理模式：
   * 环境变量驱动
   * 递归配置合并
   * 默认值处理
   * 运行时配置更新

3. 数据存储模式：
   * 多存储引擎集成
   * 存储层抽象
   * 可插拔的存储后端
   * 分布式存储支持

4. AI服务集成模式：
   * 模型服务抽象
   * 配置驱动的模型选择
   * 异步处理支持
   * 错误重试机制

5. 安全模式：
   * API密钥认证
   * 请求验证
   * 数据隔离

## 本地测试服务器模式 (2025-03-22 10:57:00)

1. 配置管理模式：
   * 示例配置文件 (.env.example)
   * 环境变量分离
   * 多AI服务商配置
   * 数据库连接配置

2. 容器编排模式：
   * 服务依赖管理
   * 数据卷映射
   * 网络隔离
   * 启动顺序控制

3. 服务健康检查模式：
   * 等待脚本 (wait-for-it.sh)
   * 超时控制
   * 依赖服务检查
   * 启动条件验证

4. API测试模式：
   * REST Client测试文件
   * 完整API覆盖
   * 测试数据模板
   * 环境变量支持


   * 错误信息保护

## 设计模式与系统架构 (2025-03-20 23:37:10)

1. 工厂模式：
   * EmbedderFactory - 创建嵌入模型实例
   * LlmFactory - 创建语言模型实例
   * VectorStoreFactory - 创建向量存储实例

2. 装饰器模式：
   * @api_error_handler - 统一的API错误处理

3. 策略模式：
   * 可插拔的存储后端
   * 可配置的嵌入模型
   * 可选的图存储功能

4. 并发模式：
   * 使用ThreadPoolExecutor
   * 向量存储和图存储的并行操作

5. 配置模式：
   * 基于Pydantic的配置管理
   * 环境变量集成
   * 默认值处理

6. 事件驱动：
   * 遥测事件捕获
   * 操作日志记录

7. 版本控制：
   * API版本管理 (v1.0/v1.1)
   * 废弃警告处理
2. 测试工具：
   * Python测试框架
   * TypeScript测试工具
   * Docker环境测试