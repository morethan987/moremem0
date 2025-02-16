This is a modified version of mem0.

moremem0是一个mem0的魔改版本，更加适应日程管理项目的体质。官方参考文档见：[Guide - Mem0.ai](https://docs.qq.com/aio/DTXFOaWVTa0tWV2JL?p=uXPWnMkrkZBipuFh4rclLh&client_hint=0#BssDTCwbPaVbrlDJCjpuA2)

具体的更新改动建docs/changelog.md文件

目前（2025-02-14）向量数据库本地使用方案如下：
1. 参考[Qdrant](https://docs.qq.com/aio/DTXFOaWVTa0tWV2JL?p=uXPWnMkrkZBipuFh4rclLh&client_hint=0#8DQLs9okS2JGY8las8Bpxd)进行本地向量数据库部署，然后启动浏览器UI
2. 克隆仓库，并在项目根目录中修改.env.example文件，并重命名为.env
3. 适当修改并运行test_local.py（注意暂时先注释掉和图数据库相关的代码）
4. 在浏览器UI中查看存储的记忆信息

目前（2025-02-15）图数据库本地话方案如下：
1. 参考[Neo4j基础 · Morethan 小站](https://docs.qq.com/aio/DTXFOaWVTa0tWV2JL?p=uXPWnMkrkZBipuFh4rclLh&client_hint=0#eAur97QLgJRKSePZhx4W60)进行本地化部署Neo4j
2. 然后把test_local.py中的相关代码解除注释，然后运行文件
3. 在浏览器UI中查看新的记忆信息