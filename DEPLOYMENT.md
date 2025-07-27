# 前后端分离项目部署指南

## 项目结构

```
Bit_test/
├── backend/                 # 后端API服务
│   ├── app.py              # Flask API应用
│   ├── run.py              # 后端启动脚本
│   └── requirements.txt    # 后端依赖
├── frontend/               # 前端静态文件
│   ├── index.html          # 主页面
│   ├── css/
│   │   └── style.css       # 样式文件
│   └── js/
│       ├── config.js       # 配置文件
│       ├── api.js          # API服务
│       ├── charts.js       # 图表管理
│       └── app.js          # 主应用
└── [原有文件...]           # 原有的业务逻辑文件

```

## 部署步骤

### 1. 后端部署

#### 安装依赖
```bash
cd backend
pip install -r requirements.txt
```

#### 启动后端服务
```bash
# 开发模式
python run.py --host 0.0.0.0 --port 5000 --debug

# 生产模式
python run.py --host 0.0.0.0 --port 5000
```

### 2. 前端部署

前端为静态文件，可以通过以下方式部署：

#### 方式1: 使用Python简单HTTP服务器
```bash
cd frontend
python -m http.server 8080
```

#### 方式2: 使用Node.js serve
```bash
cd frontend
npx serve -s . -l 8080
```

#### 方式3: 使用Nginx（推荐生产环境）
将frontend目录配置为Nginx静态文件服务

### 3. Nginx反向代理配置

创建Nginx配置文件 `/etc/nginx/sites-available/crypto-app`:

```nginx
server {
    listen 80;
    server_name your-domain.com;  # 替换为你的域名

    # 前端静态文件
    location / {
        root /path/to/frontend;  # 替换为frontend目录的绝对路径
        index index.html;
        try_files $uri $uri/ /index.html;
        
        # 缓存静态资源
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }

    # 后端API代理
    location /api/ {
        proxy_pass http://127.0.0.1:5000/;  # 后端服务地址
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # CORS处理
        add_header Access-Control-Allow-Origin *;
        add_header Access-Control-Allow-Methods "GET, POST, OPTIONS";
        add_header Access-Control-Allow-Headers "Content-Type, Authorization";
        
        # 处理OPTIONS请求
        if ($request_method = 'OPTIONS') {
            return 204;
        }
    }

    # 错误页面
    error_page 404 /index.html;
}
```

启用配置：
```bash
sudo ln -s /etc/nginx/sites-available/crypto-app /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 4. 系统服务配置

#### 后端服务配置
创建systemd服务文件 `/etc/systemd/system/crypto-backend.service`:

```ini
[Unit]
Description=Crypto Backend API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/backend
Environment=PATH=/path/to/venv/bin
ExecStart=/path/to/venv/bin/python run.py --host 0.0.0.0 --port 5000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启用服务：
```bash
sudo systemctl daemon-reload
sudo systemctl enable crypto-backend
sudo systemctl start crypto-backend
```

### 5. 环境变量配置

在backend目录创建 `.env` 文件：

```env
# 数据库配置
DB_HOST=localhost
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_NAME=crypto_db

# Redis配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# API配置
API_HOST=0.0.0.0
API_PORT=5000
DEBUG=False

# 安全配置
SECRET_KEY=your-secret-key-here
```

### 6. 防火墙配置

```bash
# 允许HTTP和HTTPS
sudo ufw allow 80
sudo ufw allow 443

# 如果需要直接访问后端（不推荐生产环境）
sudo ufw allow 5000
```

### 7. SSL证书配置（可选）

使用Let's Encrypt获取免费SSL证书：

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### 8. 监控和日志

#### 查看后端服务状态
```bash
sudo systemctl status crypto-backend
sudo journalctl -u crypto-backend -f
```

#### 查看Nginx日志
```bash
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

## 配置说明

### 前端配置
修改 `frontend/js/config.js` 中的API_BASE_URL：

```javascript
const API_CONFIG = {
    BASE_URL: 'http://your-domain.com/api',  // 生产环境
    // BASE_URL: 'http://localhost:5000',    // 开发环境
    // ...
};
```

### 后端配置
后端API已配置CORS，支持跨域请求。如需修改，编辑 `backend/app.py`。

## 故障排除

### 常见问题

1. **CORS错误**
   - 检查后端CORS配置
   - 确认前端API_BASE_URL正确

2. **API连接失败**
   - 检查后端服务是否运行
   - 检查防火墙设置
   - 验证Nginx代理配置

3. **静态文件404**
   - 检查Nginx静态文件路径
   - 确认文件权限正确

4. **数据库连接失败**
   - 检查数据库服务状态
   - 验证连接配置
   - 确认数据库用户权限

### 性能优化

1. **启用Gzip压缩**
2. **配置静态文件缓存**
3. **使用CDN加速**
4. **数据库连接池优化**
5. **Redis缓存策略调整**

## 安全建议

1. **定期更新依赖包**
2. **使用HTTPS**
3. **配置防火墙**
4. **定期备份数据**
5. **监控系统日志**