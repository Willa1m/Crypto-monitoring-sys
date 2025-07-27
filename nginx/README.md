# Nginx 部署指南

## 概述
本指南将帮助您使用 Nginx 部署加密货币监控系统的前端资源，并配置反向代理到后端 API。

## 前提条件

### 1. 安装 Nginx
**Windows 用户:**
1. 访问 [Nginx 官网](http://nginx.org/en/download.html)
2. 下载 Windows 版本的 Nginx
3. 解压到合适的目录（如 `C:\nginx`）
4. 将 Nginx 目录添加到系统 PATH 环境变量

**验证安装:**
```bash
nginx -v
```

### 2. 确保后端服务运行
确保后端 API 服务在 `http://127.0.0.1:5000` 上运行：
```bash
cd d:\Learn\Computing skill\2025Internship\Codes\Bit_test\backend
python run.py --host 0.0.0.0 --port 5000
```

## 部署方式

### 方式一：自动部署（推荐）

1. **运行部署脚本:**
```powershell
cd "d:\Learn\Computing skill\2025Internship\Codes\Bit_test\nginx"
.\deploy.ps1
```

2. **如果遇到执行策略限制:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\deploy.ps1
```

### 方式二：手动部署

1. **创建目录结构:**
```bash
mkdir d:\Learn\Computing skill\2025Internship\Codes\Bit_test\nginx\logs
mkdir d:\Learn\Computing skill\2025Internship\Codes\Bit_test\nginx\conf
```

2. **复制配置文件:**
```bash
copy "d:\Learn\Computing skill\2025Internship\Codes\Bit_test\nginx\crypto-app.conf" "d:\Learn\Computing skill\2025Internship\Codes\Bit_test\nginx\conf\crypto-app.conf"
```

3. **验证配置:**
```bash
nginx -t -c "d:\Learn\Computing skill\2025Internship\Codes\Bit_test\nginx\conf\crypto-app.conf"
```

4. **启动 Nginx:**
```bash
nginx -c "d:\Learn\Computing skill\2025Internship\Codes\Bit_test\nginx\conf\crypto-app.conf"
```

## 访问地址

部署成功后，您可以通过以下地址访问：

- **前端应用:** http://localhost
- **API 接口:** http://localhost/api/
- **健康检查:** http://localhost/health

## 管理命令

### 启动服务
```bash
nginx -c "d:\Learn\Computing skill\2025Internship\Codes\Bit_test\nginx\conf\crypto-app.conf"
```

### 停止服务
```bash
nginx -s stop
```

### 重新加载配置
```bash
nginx -s reload
```

### 重启服务
```bash
nginx -s stop
nginx -c "d:\Learn\Computing skill\2025Internship\Codes\Bit_test\nginx\conf\crypto-app.conf"
```

## 配置说明

### 主要功能
- **静态文件服务:** 直接提供前端静态资源
- **反向代理:** 将 `/api/` 请求代理到后端服务
- **CORS 支持:** 处理跨域请求
- **Gzip 压缩:** 优化传输性能
- **缓存策略:** 静态资源长期缓存
- **安全头:** 基本的安全防护

### 目录结构
```
nginx/
├── crypto-app.conf     # Nginx 配置文件
├── deploy.ps1          # 自动部署脚本
├── conf/               # 配置文件目录
│   └── crypto-app.conf # 实际使用的配置
└── logs/               # 日志目录
    ├── access.log      # 访问日志
    └── error.log       # 错误日志
```

## 故障排除

### 1. 端口冲突
如果 80 端口被占用，修改配置文件中的 `listen` 指令：
```nginx
listen 8080;  # 改为其他端口
```

### 2. 权限问题
确保 Nginx 有权限访问项目目录和日志目录。

### 3. 后端连接失败
- 确认后端服务正在运行
- 检查防火墙设置
- 验证后端服务地址和端口

### 4. 静态文件 404
- 检查前端文件路径是否正确
- 确认 `root` 指令指向正确的目录

### 5. CORS 错误
配置文件已包含 CORS 头设置，如果仍有问题，检查：
- 前端请求的域名
- API 端点路径
- 浏览器控制台错误信息

## 性能优化

### 1. 启用 HTTP/2
```nginx
listen 443 ssl http2;
```

### 2. 调整 Worker 进程
```nginx
worker_processes auto;
worker_connections 1024;
```

### 3. 缓存优化
```nginx
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

## 监控和日志

### 访问日志
```bash
tail -f "d:\Learn\Computing skill\2025Internship\Codes\Bit_test\nginx\logs\access.log"
```

### 错误日志
```bash
tail -f "d:\Learn\Computing skill\2025Internship\Codes\Bit_test\nginx\logs\error.log"
```

### 实时监控
可以使用工具如 `nginx-amplify` 或 `prometheus` 进行更详细的监控。

## 安全建议

1. **定期更新 Nginx**
2. **配置 SSL/TLS**（生产环境）
3. **限制请求频率**
4. **隐藏 Nginx 版本信息**
5. **配置防火墙规则**

## 生产环境部署

对于生产环境，建议：
1. 使用 HTTPS
2. 配置 SSL 证书
3. 设置适当的缓存策略
4. 启用访问日志分析
5. 配置负载均衡（如有多个后端实例）

## 支持

如果遇到问题，请检查：
1. Nginx 错误日志
2. 后端服务日志
3. 浏览器开发者工具
4. 网络连接状态