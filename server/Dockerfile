FROM python:3.12-slim

# 设置工作目录为/app/server，这样main.py就在正确的位置
WORKDIR /app/server

# 配置pip源
# 使用腾讯云镜像源，注意这里是内网域名
RUN pip config set global.index-url https://mirrors.tencentyun.com/pypi/simple && pip config set global.trusted-host mirrors.tencentyun.com

# 复制并安装requirements
COPY server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件到正确的位置
COPY pyproject.toml /app/
COPY README.md /app/
COPY mem0 /app/mem0
COPY robots /app/robots/

# 安装本地包
WORKDIR /app
RUN pip install -e .[graph]

# 回到server目录
WORKDIR /app/server

# 复制服务器文件
COPY server/.env .
COPY server/main.py .

EXPOSE 8000

ENV PYTHONUNBUFFERED=1

# 等待数据库服务准备就绪
COPY server/wait-for-it.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/wait-for-it.sh

# 使用wait-for-it确保数据库服务就绪后再启动应用
CMD ["sh", "-c", "wait-for-it.sh neo4j:7687 -t 60 && wait-for-it.sh qdrant:6333 -t 60 && python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload"]