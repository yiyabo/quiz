# 🚀 服务器部署指南

## 📋 前置准备

### 服务器要求
- **操作系统**: Ubuntu 20.04+ / CentOS 7+ / Debian 10+
- **Python**: 3.8+
- **Node.js**: 16+
- **内存**: 最低 2GB，推荐 4GB+
- **存储**: 最低 10GB

### 需要安装的软件
```bash
# Python 3
sudo apt update
sudo apt install python3 python3-pip python3-venv

# Node.js (使用 NodeSource)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Nginx (可选，用于反向代理)
sudo apt install nginx
```

## 📦 部署步骤

### 1. 克隆项目

```bash
cd /var/www  # 或其他你喜欢的目录
git clone https://github.com/yiyabo/quiz.git
cd quiz
```

### 2. 解压数据集

CCI 竞赛的大文件需要解压：

```bash
cd "cci test"
tar -xzf dataset.tar.gz
cd ..
```

### 3. 配置环境变量

```bash
# 复制配置模板
cp .env.example .env

# 编辑配置（生产环境）
nano .env
```

生产环境配置示例：
```bash
HOST=127.0.0.1  # 只监听本地，通过 Nginx 反向代理
PORT=8000
RELOAD=false    # 生产环境关闭热重载

# 设置允许的域名
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### 4. 安装后端依赖

```bash
cd backend

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 5. 安装前端依赖并构建

```bash
cd ../frontend

# 安装依赖
npm install

# 构建生产版本
npm run build
```

构建完成后，静态文件在 `frontend/dist/` 目录。

### 6. 使用 Systemd 管理后端服务

创建服务文件：

```bash
sudo nano /etc/systemd/system/quiz-backend.service
```

内容：
```ini
[Unit]
Description=Quiz Platform Backend
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/quiz/backend
Environment="PATH=/var/www/quiz/backend/venv/bin"
EnvironmentFile=/var/www/quiz/.env
ExecStart=/var/www/quiz/backend/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
sudo systemctl daemon-reload
sudo systemctl enable quiz-backend
sudo systemctl start quiz-backend
sudo systemctl status quiz-backend
```

### 7. 配置 Nginx

创建 Nginx 配置：

```bash
sudo nano /etc/nginx/sites-available/quiz
```

内容：
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    # 前端静态文件
    location / {
        root /var/www/quiz/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # 后端 API
    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 数据集下载（大文件）
    client_max_body_size 200M;
}
```

启用配置：
```bash
sudo ln -s /etc/nginx/sites-available/quiz /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 8. 配置 HTTPS (推荐)

使用 Let's Encrypt：

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

## 🔧 维护命令

### 查看后端日志
```bash
sudo journalctl -u quiz-backend -f
```

### 重启服务
```bash
sudo systemctl restart quiz-backend
sudo systemctl restart nginx
```

### 更新代码
```bash
cd /var/www/quiz
git pull

# 重新构建前端
cd frontend
npm run build

# 重启后端
sudo systemctl restart quiz-backend
```

## 📊 监控

### 检查服务状态
```bash
sudo systemctl status quiz-backend
sudo systemctl status nginx
```

### 检查端口
```bash
sudo netstat -tlnp | grep 8000  # 后端
sudo netstat -tlnp | grep 80    # Nginx
```

## 🔒 安全建议

1. **防火墙配置**
   ```bash
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw enable
   ```

2. **定期备份数据库**
   ```bash
   cp /var/www/quiz/backend/quiz_platform.db /backup/quiz_$(date +%Y%m%d).db
   ```

3. **限制文件上传大小** - 已在 Nginx 配置中设置为 200M

4. **使用 HTTPS** - 通过 Certbot 自动配置

## 🐛 故障排除

### 后端无法启动
```bash
# 检查日志
sudo journalctl -u quiz-backend -n 50

# 手动测试
cd /var/www/quiz/backend
source venv/bin/activate
python main.py
```

### 前端无法访问
```bash
# 检查 Nginx 配置
sudo nginx -t

# 检查文件权限
ls -la /var/www/quiz/frontend/dist
```

### 数据库错误
```bash
# 删除数据库重新初始化
rm /var/www/quiz/backend/quiz_platform.db
sudo systemctl restart quiz-backend
```

---

**部署完成后访问**: `http://yourdomain.com`
