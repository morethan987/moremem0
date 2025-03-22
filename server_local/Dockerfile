FROM python:3.12-slim

# 设置工作目录为/app/server_local，这样main.py就在正确的位置
WORKDIR /app/server_local

# 复制并安装requirements
COPY server_local/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件到正确的位置
COPY pyproject.toml /app/
COPY README.md /app/
COPY mem0 /app/mem0

# 安装本地包
WORKDIR /app
RUN pip install -e .[graph]

# 回到server_local目录
WORKDIR /app/server_local

# 复制服务器文件
COPY server_local/.env .
COPY server_local/main.py .

# 添加wait-for-it.sh并确保使用Unix格式的换行符
COPY server_local/wait-for-it.sh /usr/local/bin/
RUN sed -i 's/\r$//' /usr/local/bin/wait-for-it.sh && \
    chmod +x /usr/local/bin/wait-for-it.sh

EXPOSE 8000

ENV PYTHONUNBUFFERED=1

# 使用wait-for-it确保数据库服务就绪后再启动应用
CMD ["sh", "-c", "wait-for-it.sh neo4j:7687 -t 60 && wait-for-it.sh qdrant:6333 -t 60 && python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload"]