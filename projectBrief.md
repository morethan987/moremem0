# Moremem0: Project Brief

这是一个非常复杂的AI记忆库项目，包含了众多的子项目，这些项目之间彼此相互关联；项目使用poetry进行依赖管理

## mem0

这个子项目是使用Python编写的AI记忆库主项目，包含了所有的记忆库的功能，也就是一个PythonSDK

## mem0-ts

这个子项目是使用Typescript编写的记忆库主项目，与PythonSDK类似，可以理解为一个TypescriptSDK，能够打包为一个npm包

## examples

这个子项目中存放着一些前端网页项目

## server

这个子项目将PythonSDK运行在服务器上，并为之配备了一个网页前端，网页前端源代码来源于：`examples/vercel-ai-sdk-chat-app`

服务器的主文件是`main.py`

## test

这个子项目主要存放各种测试文件

## vercel-ai-sdk

这是一个基于Vercel AI SDK的一个二次开发的npm包

Vercel AI SDK：一个专用于构建AI聊天界面的第三方前端工具包