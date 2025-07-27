#!/usr/bin/env python3
"""
简单的HTTP代理服务器
用于替代Nginx进行前后端分离部署
"""

import http.server
import socketserver
import urllib.request
import urllib.parse
import json
import os
import sys
from urllib.error import URLError

class ProxyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """自定义HTTP请求处理器，支持API代理"""
    
    def __init__(self, *args, **kwargs):
        # 设置前端静态文件目录
        self.frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend')
        super().__init__(*args, directory=self.frontend_dir, **kwargs)
    
    def do_GET(self):
        """处理GET请求"""
        if self.path.startswith('/api/') or self.path == '/health':
            self.proxy_to_backend()
        else:
            # 处理静态文件
            if self.path == '/':
                self.path = '/index.html'
            # 添加CORS头部到静态文件响应
            super().do_GET()
            
    def end_headers(self):
        """添加安全头部和CORS头部"""
        # 为所有响应添加CORS头部
        if not hasattr(self, '_cors_sent'):
            self.send_cors_headers()
            self._cors_sent = True
        
        self.send_header('X-Frame-Options', 'SAMEORIGIN')
        self.send_header('X-XSS-Protection', '1; mode=block')
        self.send_header('X-Content-Type-Options', 'nosniff')
        super().end_headers()
    
    def do_POST(self):
        """处理POST请求"""
        if self.path.startswith('/api/'):
            self.proxy_to_backend()
        else:
            self.send_error(404, "Not Found")
    
    def do_OPTIONS(self):
        """处理OPTIONS预检请求"""
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()
    
    def proxy_to_backend(self):
        """代理请求到后端API服务器"""
        backend_url = f"http://127.0.0.1:5000{self.path}"
        
        try:
            # 准备请求数据
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length) if content_length > 0 else None
            
            # 创建请求
            req = urllib.request.Request(backend_url, data=post_data)
            
            # 复制相关头部
            for header in ['Content-Type', 'Authorization']:
                if header in self.headers:
                    req.add_header(header, self.headers[header])
            
            # 发送请求到后端
            with urllib.request.urlopen(req, timeout=10) as response:
                # 发送响应状态
                self.send_response(response.getcode())
                
                # 发送CORS头部
                self.send_cors_headers()
                
                # 复制响应头部
                for header, value in response.headers.items():
                    if header.lower() not in ['server', 'date']:
                        self.send_header(header, value)
                
                self.end_headers()
                
                # 发送响应体
                self.wfile.write(response.read())
                
        except URLError as e:
            print(f"后端连接错误: {e}")
            self.send_error(502, "Backend connection failed")
        except Exception as e:
            print(f"代理错误: {e}")
            self.send_error(500, "Proxy error")
    
    def send_cors_headers(self):
        """发送CORS头部"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With')
        self.send_header('Access-Control-Max-Age', '86400')
    
    def log_message(self, format, *args):
        """自定义日志格式"""
        print(f"[{self.log_date_time_string()}] {format % args}")

def main():
    """主函数"""
    PORT = 80
    
    # 检查端口是否可用，如果不可用则使用8080
    try:
        with socketserver.TCPServer(("", PORT), ProxyHTTPRequestHandler) as httpd:
            pass
    except OSError:
        PORT = 8080
        print(f"端口80被占用，使用端口{PORT}")
    
    try:
        with socketserver.TCPServer(("", PORT), ProxyHTTPRequestHandler) as httpd:
            print(f"=== 加密货币监控系统代理服务器 ===")
            print(f"前端访问地址: http://localhost:{PORT}")
            print(f"API代理地址: http://localhost:{PORT}/api/")
            print(f"健康检查: http://localhost:{PORT}/health")
            print(f"按 Ctrl+C 停止服务器")
            print(f"=====================================")
            
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n服务器已停止")
    except Exception as e:
        print(f"服务器启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()