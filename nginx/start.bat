@echo off
REM 启动脚本 - 加密货币监控系统
REM 使用Python代理服务器替代Nginx

echo === 加密货币监控系统启动脚本 ===
echo.

REM 设置项目路径
set PROJECT_ROOT=d:\Learn\Computing skill\2025Internship\Codes\Bit_test
set BACKEND_DIR=%PROJECT_ROOT%\backend
set NGINX_DIR=%PROJECT_ROOT%\nginx

echo 1. 启动后端API服务器...
cd /d "%BACKEND_DIR%"
start "Backend API" python run.py --host 0.0.0.0 --port 5000

echo 等待后端服务启动...
timeout /t 5 /nobreak > nul

echo.
echo 2. 启动前端代理服务器...
cd /d "%NGINX_DIR%"
echo 前端访问地址: http://localhost
echo API代理地址: http://localhost/api/
echo 健康检查: http://localhost/health
echo.
echo 按 Ctrl+C 停止服务器
echo =====================================
python proxy_server.py

pause