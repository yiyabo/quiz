# 🚀 部署文档

本文档详细说明如何将蛋白质相互作用预测竞赛平台部署到生产服务器。

## 📋 目录

- [服务器要求](#服务器要求)
- [本地部署](#本地部署)
- [服务器部署](#服务器部署)
- [使用Nginx部署](#使用nginx部署)
- [安全配置](#安全配置)
- [性能优化](#性能优化)
- [监控和维护](#监控和维护)

## 服务器要求

### 最低配置
- **CPU**: 2核
- **内存**: 4GB
- **存储**: 20GB
- **操作系统**: Ubuntu 20.04+ / CentOS 7+ / macOS

### 软件要求
- Python 3.8+
- Node.js 16+
- Nginx (生产环境)
- Supervisor (可选，用于进程管理)

## 本地部署

### 快速启动

```bash
# 克隆或解压项目
cd /Users/apple/work/quiz

# 一键启动
./start.sh
```

访问: `http://localhost:3000`

### 手动启动

**启动后端:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 main.py
```

**启动前端:**
```bash
cd frontend
npm install
npm run dev
```

## 服务器部署

### 1. 准备服务器环境

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装Python 3.8+
sudo apt install python3 python3-pip python3-venv -y

# 安装Node.js 16+
curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -
sudo apt install nodejs -y

# 安装Nginx
sudo apt install nginx -y

# 安装Supervisor (可选)
sudo apt install supervisor -y
```

### 2. 上传项目文件

```bash
# 使用scp上传
scp -r /Users/apple/work/quiz user@server:/var/www/

# 或使用git
ssh user@server
cd /var/www
git clone <your-repo-url> quiz
```

### 3. 配置后端

```bash
cd /var/www/quiz/backend

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 安装生产服务器
pip install gunicorn

# 测试运行
python3 main.py
```

### 4. 配置前端

```bash
cd /var/www/quiz/frontend

# 安装依赖
npm install

# 构建生产版本
npm run build

# 构建完成后，dist目录包含所有静态文件
```

## 使用Nginx部署

### 1. 配置Nginx

创建配置文件: `/etc/nginx/sites-available/quiz-platform`

```nginx
server {
    listen 80;
    server_name your-domain.com;  # 替换为你的域名或IP

    # 客户端上传大小限制（CSV文件）
    client_max_body_size 10M;

    # 前端静态文件
    location / {
        root /var/www/quiz/frontend/dist;
        try_files $uri $uri/ /index.html;
        
        # 缓存静态资源
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }

    # 后端API代理
    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # 数据集下载
    location /api/download {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_buffering off;
    }
}
```

### 2. 启用Nginx配置

```bash
# 创建软链接
sudo ln -s /etc/nginx/sites-available/quiz-platform /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重启Nginx
sudo systemctl restart nginx
```

### 3. 使用Gunicorn运行后端

```bash
cd /var/www/quiz/backend
source venv/bin/activate

# 手动测试
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 127.0.0.1:8000

# 后台运行
nohup gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 127.0.0.1:8000 > gunicorn.log 2>&1 &
```

**参数说明:**
- `-w 4`: 4个worker进程（建议为CPU核心数的2-4倍）
- `-k uvicorn.workers.UvicornWorker`: 使用uvicorn worker
- `-b 127.0.0.1:8000`: 绑定到本地8000端口

## 使用Supervisor管理进程

### 1. 创建Supervisor配置

创建文件: `/etc/supervisor/conf.d/quiz-backend.conf`

```ini
[program:quiz-backend]
directory=/var/www/quiz/backend
command=/var/www/quiz/backend/venv/bin/gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 127.0.0.1:8000
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/quiz-backend.log
```

### 2. 启动服务

```bash
# 重新加载配置
sudo supervisorctl reread
sudo supervisorctl update

# 启动服务
sudo supervisorctl start quiz-backend

# 查看状态
sudo supervisorctl status

# 查看日志
sudo tail -f /var/log/quiz-backend.log
```

### 常用命令

```bash
sudo supervisorctl start quiz-backend    # 启动
sudo supervisorctl stop quiz-backend     # 停止
sudo supervisorctl restart quiz-backend  # 重启
sudo supervisorctl status quiz-backend   # 状态
```

## 安全配置

### 1. 使用HTTPS (推荐)

使用Let's Encrypt免费SSL证书:

```bash
# 安装certbot
sudo apt install certbot python3-certbot-nginx -y

# 获取证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo certbot renew --dry-run
```

### 2. 修改默认密钥

编辑 `backend/auth.py`:

```python
# 生成安全的密钥
import secrets
SECRET_KEY = secrets.token_urlsafe(32)
```

或使用环境变量:

```bash
export SECRET_KEY="your-super-secret-key-here"
```

### 3. 配置防火墙

```bash
# 允许HTTP和HTTPS
sudo ufw allow 'Nginx Full'

# 允许SSH
sudo ufw allow ssh

# 启用防火墙
sudo ufw enable
```

### 4. 数据库安全

如果使用PostgreSQL替代SQLite:

```bash
# 安装PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# 创建数据库和用户
sudo -u postgres psql
CREATE DATABASE quiz_platform;
CREATE USER quiz_user WITH PASSWORD 'strong_password';
GRANT ALL PRIVILEGES ON DATABASE quiz_platform TO quiz_user;
\q
```

修改 `backend/database.py`:

```python
SQLALCHEMY_DATABASE_URL = "postgresql://quiz_user:strong_password@localhost/quiz_platform"
```

## 性能优化

### 1. 后端优化

**使用Redis缓存 (可选):**

```bash
# 安装Redis
sudo apt install redis-server -y

# 安装Python Redis客户端
pip install redis
```

**增加Worker数量:**

```bash
# 根据CPU核心数调整
gunicorn main:app -w 8 -k uvicorn.workers.UvicornWorker -b 127.0.0.1:8000
```

### 2. 前端优化

**Nginx压缩:**

在Nginx配置中添加:

```nginx
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/json application/javascript;
```

**CDN加速 (可选):**

将静态资源上传到CDN，修改前端配置使用CDN地址。

### 3. 数据库优化

**定期清理:**

```bash
# 清理旧的提交记录（保留最近3个月）
# 创建清理脚本
```

**添加索引:**

在 `database.py` 中已经添加了必要的索引。

## 监控和维护

### 1. 日志管理

**后端日志:**
```bash
# 查看实时日志
tail -f /var/log/quiz-backend.log

# 日志轮转配置
sudo nano /etc/logrotate.d/quiz-backend
```

**Nginx日志:**
```bash
# 访问日志
tail -f /var/log/nginx/access.log

# 错误日志
tail -f /var/log/nginx/error.log
```

### 2. 性能监控

**系统资源:**
```bash
# 实时监控
htop

# CPU和内存
top

# 磁盘使用
df -h
```

**应用监控:**
```bash
# 查看进程
ps aux | grep gunicorn

# 端口监听
netstat -tlnp | grep 8000
```

### 3. 备份策略

**数据库备份:**
```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/var/backups/quiz"
mkdir -p $BACKUP_DIR

# 备份SQLite数据库
cp /var/www/quiz/backend/quiz_platform.db $BACKUP_DIR/db_$DATE.db

# 备份提交文件
tar -czf $BACKUP_DIR/submissions_$DATE.tar.gz /var/www/quiz/submissions

# 删除30天前的备份
find $BACKUP_DIR -mtime +30 -delete

echo "Backup completed: $DATE"
```

设置定时任务:
```bash
# 每天凌晨2点备份
crontab -e
0 2 * * * /path/to/backup.sh
```

### 4. 更新部署

```bash
#!/bin/bash
# deploy.sh - 更新部署脚本

echo "🔄 开始更新..."

# 停止后端服务
sudo supervisorctl stop quiz-backend

# 拉取最新代码
cd /var/www/quiz
git pull

# 更新后端
cd backend
source venv/bin/activate
pip install -r requirements.txt

# 更新前端
cd ../frontend
npm install
npm run build

# 重启服务
sudo supervisorctl start quiz-backend
sudo systemctl reload nginx

echo "✅ 更新完成！"
```

## 故障排除

### 常见问题

**1. 后端无法启动**
```bash
# 检查端口占用
lsof -i :8000

# 检查日志
tail -f /var/log/quiz-backend.log
```

**2. 前端页面空白**
```bash
# 检查Nginx配置
sudo nginx -t

# 检查静态文件
ls -la /var/www/quiz/frontend/dist
```

**3. 数据库错误**
```bash
# 检查数据库文件权限
ls -l /var/www/quiz/backend/quiz_platform.db

# 修改权限
sudo chown www-data:www-data /var/www/quiz/backend/quiz_platform.db
```

**4. 上传文件失败**
```bash
# 检查目录权限
sudo chown -R www-data:www-data /var/www/quiz/submissions
sudo chmod -R 755 /var/www/quiz/submissions
```

## 健康检查

创建健康检查脚本 `health_check.sh`:

```bash
#!/bin/bash

# 检查后端
if curl -f http://localhost:8000/api/health > /dev/null 2>&1; then
    echo "✅ Backend is healthy"
else
    echo "❌ Backend is down"
    sudo supervisorctl restart quiz-backend
fi

# 检查Nginx
if systemctl is-active --quiet nginx; then
    echo "✅ Nginx is running"
else
    echo "❌ Nginx is down"
    sudo systemctl start nginx
fi
```

设置定时检查:
```bash
# 每5分钟检查一次
crontab -e
*/5 * * * * /path/to/health_check.sh
```

## 扩展性考虑

### 数据库升级到PostgreSQL

当用户数超过100或需要更好的性能时：

```python
# requirements.txt 添加
psycopg2-binary==2.9.9

# database.py 修改
SQLALCHEMY_DATABASE_URL = "postgresql://user:password@localhost/dbname"
```

### 使用Redis缓存排行榜

```python
# 缓存排行榜结果，减少数据库查询
import redis
r = redis.Redis(host='localhost', port=6379, db=0)
```

### 负载均衡

当流量增大时，使用多个后端实例：

```nginx
upstream backend {
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
    server 127.0.0.1:8003;
}

location /api {
    proxy_pass http://backend;
}
```

---

**部署愉快！如有问题请查看日志或联系管理员。**

