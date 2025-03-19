# 构建阶段
FROM node:alpine AS builder

WORKDIR /app

# 复制package.json和package-lock.json（如果存在）
COPY package*.json ./
COPY *.tgz ./

# 安装依赖
RUN npm install

COPY . .

# 构建应用
RUN npm run build

# 生产阶段
FROM nginx:alpine

# 从构建阶段复制构建产物
COPY --from=builder /app/dist /usr/share/nginx/html

# nginx将在80端口监听
EXPOSE 3000

# 使用自定义nginx配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

CMD ["nginx", "-g", "daemon off;"]