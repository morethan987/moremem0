# Product Context

This file provides a high-level overview of the project and the expected product that will be created. Initially it is based upon projectBrief.md and all other available project-related information in the working directory. This file is intended to be updated as the project evolves, and should be used to inform all other modes of the project's goals and context.
2025-03-20 23:29:30 - Initial creation of Memory Bank

## Project Goal

Moremem0是一个复杂的AI记忆库项目，旨在提供全面的AI记忆管理解决方案。该项目通过多个相互关联的组件，为不同的开发环境和应用场景提供AI记忆库功能。

## Key Features

1. 多语言SDK支持：
   - Python SDK (mem0)：完整的AI记忆库功能实现
   - TypeScript SDK (mem0-ts)：JavaScript生态系统的集成方案

2. 服务端部署：
   - 完整的服务器端实现
   - 集成的Web前端界面
   - Docker支持

3. AI聊天界面：
   - 基于Vercel AI SDK的定制开发
   - 用户友好的交互界面

4. 示例实现：
   - 多个前端网页项目示例
   - 完整的部署示例

## Overall Architecture

1. 核心SDK层：
   - mem0 (Python)：核心功能实现
   - mem0-ts (TypeScript)：JavaScript生态系统适配

2. 服务层：
   - server模块：将Python SDK包装为Web服务
   - nginx配置：处理Web请求
   - Docker支持：容器化部署

3. 前端层：
   - vercel-ai-sdk：定制的AI聊天界面框架
   - examples：多个示例实现

4. 测试层：
   - tests模块：包含各组件的测试用例

## 项目依赖管理
- 使用poetry管理Python项目依赖
- 使用pnpm管理JavaScript项目依赖

*2025-03-20 23:29:30 - 初始文档基于projectBrief.md创建