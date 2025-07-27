# Nginx 部署脚本 (Windows PowerShell)
# 用于快速部署加密货币监控系统

# 设置变量
$PROJECT_ROOT = "d:\Learn\Computing skill\2025Internship\Codes\Bit_test"
$NGINX_DIR = "$PROJECT_ROOT\nginx"
$FRONTEND_DIR = "$PROJECT_ROOT\frontend"
$BACKEND_DIR = "$PROJECT_ROOT\backend"

Write-Host "=== 加密货币监控系统 Nginx 部署脚本 ===" -ForegroundColor Green

# 检查 Nginx 是否已安装
function Check-Nginx {
    try {
        $nginxVersion = nginx -v 2>&1
        Write-Host "检测到 Nginx: $nginxVersion" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "未检测到 Nginx，请先安装 Nginx" -ForegroundColor Red
        Write-Host "下载地址: http://nginx.org/en/download.html" -ForegroundColor Yellow
        return $false
    }
}

# 创建必要的目录
function Create-Directories {
    Write-Host "创建必要的目录..." -ForegroundColor Yellow
    
    if (!(Test-Path $NGINX_DIR)) {
        New-Item -ItemType Directory -Path $NGINX_DIR -Force
        Write-Host "创建目录: $NGINX_DIR" -ForegroundColor Green
    }
    
    if (!(Test-Path "$NGINX_DIR\logs")) {
        New-Item -ItemType Directory -Path "$NGINX_DIR\logs" -Force
        Write-Host "创建日志目录: $NGINX_DIR\logs" -ForegroundColor Green
    }
    
    if (!(Test-Path "$NGINX_DIR\conf")) {
        New-Item -ItemType Directory -Path "$NGINX_DIR\conf" -Force
        Write-Host "创建配置目录: $NGINX_DIR\conf" -ForegroundColor Green
    }
}

# 复制配置文件
function Copy-Config {
    Write-Host "复制 Nginx 配置文件..." -ForegroundColor Yellow
    
    if (Test-Path "$NGINX_DIR\crypto-app.conf") {
        Copy-Item "$NGINX_DIR\crypto-app.conf" "$NGINX_DIR\conf\crypto-app.conf" -Force
        Write-Host "配置文件已复制到: $NGINX_DIR\conf\crypto-app.conf" -ForegroundColor Green
    } else {
        Write-Host "错误: 找不到配置文件 $NGINX_DIR\crypto-app.conf" -ForegroundColor Red
        exit 1
    }
}

# 验证配置文件
function Test-Config {
    Write-Host "验证 Nginx 配置..." -ForegroundColor Yellow
    
    try {
        nginx -t -c "$NGINX_DIR\conf\crypto-app.conf"
        Write-Host "配置文件验证成功!" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "配置文件验证失败!" -ForegroundColor Red
        return $false
    }
}

# 启动服务
function Start-Services {
    Write-Host "启动服务..." -ForegroundColor Yellow
    
    # 启动后端服务
    Write-Host "启动后端 API 服务..." -ForegroundColor Cyan
    Start-Process -FilePath "python" -ArgumentList "$BACKEND_DIR\app.py" -WorkingDirectory $BACKEND_DIR -WindowStyle Minimized
    Start-Sleep -Seconds 3
    
    # 启动 Nginx
    Write-Host "启动 Nginx 服务..." -ForegroundColor Cyan
    try {
        Start-Process -FilePath "nginx" -ArgumentList "-c", "$NGINX_DIR\conf\crypto-app.conf" -WindowStyle Hidden
        Write-Host "Nginx 启动成功!" -ForegroundColor Green
    }
    catch {
        Write-Host "Nginx 启动失败!" -ForegroundColor Red
    }
}

# 显示访问信息
function Show-Info {
    Write-Host "`n=== 部署完成 ===" -ForegroundColor Green
    Write-Host "前端访问地址: http://localhost" -ForegroundColor Cyan
    Write-Host "后端 API 地址: http://localhost/api/" -ForegroundColor Cyan
    Write-Host "健康检查: http://localhost/health" -ForegroundColor Cyan
    Write-Host "`n日志文件位置:" -ForegroundColor Yellow
    Write-Host "  访问日志: $NGINX_DIR\logs\access.log" -ForegroundColor White
    Write-Host "  错误日志: $NGINX_DIR\logs\error.log" -ForegroundColor White
    Write-Host "`n停止服务命令:" -ForegroundColor Yellow
    Write-Host "  nginx -s stop" -ForegroundColor White
    Write-Host "  nginx -s reload  # 重新加载配置" -ForegroundColor White
}

# 主执行流程
if (Check-Nginx) {
    Create-Directories
    Copy-Config
    
    if (Test-Config) {
        Start-Services
        Show-Info
    } else {
        Write-Host "部署失败: 配置文件验证不通过" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "部署失败: 请先安装 Nginx" -ForegroundColor Red
    exit 1
}