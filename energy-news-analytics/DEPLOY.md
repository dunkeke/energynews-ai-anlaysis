# 能源化工新闻分析系统 - 部署指南

## 系统要求

### 最低配置
- CPU: 4核
- 内存: 8GB
- 磁盘: 50GB
- 网络: 稳定的外网连接

### 推荐配置
- CPU: 8核+
- 内存: 16GB+
- 磁盘: 100GB SSD
- 网络: 高速外网连接

## 部署方式

### 方式一：Docker Compose部署（推荐）

#### 1. 环境准备

安装Docker和Docker Compose：

```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### 2. 下载代码

```bash
git clone <repository-url>
cd energy-news-analytics
```

#### 3. 配置环境变量

```bash
cp .env.example .env
# 编辑.env文件，修改必要的配置
nano .env
```

#### 4. 启动服务

使用快速启动脚本：
```bash
./start.sh
```

或手动启动：
```bash
docker-compose up -d
```

#### 5. 验证部署

```bash
# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f backend
docker-compose logs -f frontend

# 测试API
curl http://localhost:8000/health
```

#### 6. 访问系统

- 前端界面：http://localhost
- API文档：http://localhost:8000/docs
- 后端API：http://localhost:8000

### 方式二：手动部署

#### 后端部署

1. 安装Python 3.10+
```bash
sudo apt update
sudo apt install python3.10 python3.10-venv python3-pip
```

2. 创建虚拟环境
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 配置数据库
- 安装PostgreSQL、MongoDB、Redis
- 创建数据库和用户
- 配置连接字符串

5. 启动服务
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

#### 前端部署

1. 安装Node.js 18+
```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
```

2. 安装依赖
```bash
cd frontend
npm install
```

3. 配置API地址
编辑 `package.json` 中的proxy字段，或创建 `.env` 文件：
```
REACT_APP_API_URL=http://localhost:8000
```

4. 构建应用
```bash
npm run build
```

5. 部署到Nginx
```bash
sudo cp -r build/* /var/www/html/
```

## 生产环境配置

### 1. Nginx配置

```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        root /var/www/html;
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 2. SSL证书

使用Let's Encrypt免费证书：
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### 3. 系统服务

创建systemd服务文件 `/etc/systemd/system/energy-news.service`：
```ini
[Unit]
Description=Energy News Analytics Backend
After=network.target

[Service]
Type=simple
User=energy
WorkingDirectory=/opt/energy-news-analytics/backend
Environment=PATH=/opt/energy-news-analytics/backend/venv/bin
ExecStart=/opt/energy-news-analytics/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

启用服务：
```bash
sudo systemctl enable energy-news
sudo systemctl start energy-news
```

### 4. 数据库备份

创建备份脚本 `/opt/backup/backup.sh`：
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR=/opt/backup

# PostgreSQL备份
docker exec energy-news-postgres pg_dump -U energy_user energy_news > $BACKUP_DIR/postgres_$DATE.sql

# MongoDB备份
docker exec energy-news-mongodb mongodump --out $BACKUP_DIR/mongodb_$DATE

# 压缩备份
tar -czf $BACKUP_DIR/backup_$DATE.tar.gz $BACKUP_DIR/postgres_$DATE.sql $BACKUP_DIR/mongodb_$DATE

# 删除7天前的备份
find $BACKUP_DIR -name "backup_*.tar.gz" -mtime +7 -delete
```

添加定时任务：
```bash
0 2 * * * /opt/backup/backup.sh
```

## 监控和日志

### 1. 查看日志

```bash
# 查看所有服务日志
docker-compose logs

# 查看特定服务日志
docker-compose logs -f backend

# 查看最近100行日志
docker-compose logs --tail=100 backend
```

### 2. 监控资源使用

```bash
# 查看容器资源使用
docker stats

# 查看系统资源使用
htop
```

### 3. 健康检查

```bash
# 检查后端健康状态
curl http://localhost:8000/health

# 检查数据库连接
docker exec energy-news-postgres pg_isready -U energy_user
```

## 故障排除

### 1. 服务无法启动

检查日志：
```bash
docker-compose logs backend
docker-compose logs frontend
```

常见问题：
- 端口被占用：修改docker-compose.yml中的端口映射
- 内存不足：增加系统内存或调整JVM参数
- 数据库连接失败：检查数据库配置和网络

### 2. 数据库连接错误

检查数据库服务状态：
```bash
docker-compose ps
docker-compose logs postgres
```

重置数据库：
```bash
docker-compose down -v
docker-compose up -d postgres
```

### 3. 性能问题

优化建议：
- 增加内存分配
- 调整NLP模型批处理大小
- 启用Redis缓存
- 优化数据库查询

## 更新部署

### 更新代码

```bash
git pull origin main
```

### 重启服务

```bash
docker-compose down
docker-compose up -d --build
```

### 数据库迁移

```bash
docker exec energy-news-backend alembic upgrade head
```

## 安全建议

1. **修改默认密码**：生产环境必须修改所有默认密码
2. **启用防火墙**：只开放必要的端口
3. **定期更新**：及时更新系统和依赖包
4. **访问控制**：配置IP白名单
5. **日志审计**：定期检查访问日志
6. **HTTPS**：生产环境必须使用HTTPS

## 技术支持

- 文档：https://docs.energy-news-analytics.com
- 问题反馈：https://github.com/yourusername/energy-news-analytics/issues
- 邮箱：support@energy-news-analytics.com
