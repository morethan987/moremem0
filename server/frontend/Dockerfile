FROM node:alpine

WORKDIR /app

# 复制package.json和package-lock.json（如果存在）
COPY package*.json ./
COPY *.tgz ./

# 安装依赖
RUN npm install

COPY . .

# 构建应用
RUN npm run build

# 使用Vite的预览服务器运行应用
CMD ["npm", "run", "preview", "--", "--host", "--port", "3000"]