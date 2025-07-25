#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cloudflare Tunnel 快速启动脚本
"""

import subprocess
import sys
import time
import os
from crypto_web_app import CryptoWebApp
import threading

class CloudflareTunnelManager:
    def __init__(self):
        self.tunnel_process = None
        self.public_url = None
        
    def start_quick_tunnel(self):
        """启动 Cloudflare 快速隧道（无需登录）"""
        print("🚀 正在启动 Cloudflare 快速隧道...")
        print("📝 注意：这是免费的临时隧道，无需注册账户")
        
        try:
            # 启动快速隧道
            cmd = ["./cloudflared.exe", "tunnel", "--url", "http://localhost:5000"]
            
            self.tunnel_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=os.path.dirname(os.path.abspath(__file__))
            )
            
            # 等待隧道启动并获取URL
            print("⏳ 正在建立隧道连接...")
            time.sleep(5)
            
            # 检查进程状态
            if self.tunnel_process.poll() is None:
                print("✅ Cloudflare 隧道启动成功！")
                print("🔍 正在获取公网地址...")
                
                # 启动线程监控输出
                self.monitor_tunnel_output()
                return True
            else:
                print("❌ 隧道启动失败")
                return False
                
        except Exception as e:
            print(f"❌ 启动失败: {e}")
            return False
    
    def monitor_tunnel_output(self):
        """监控隧道输出以获取公网URL"""
        def read_output():
            try:
                for line in iter(self.tunnel_process.stderr.readline, ''):
                    if line:
                        line = line.strip()
                        # 查找包含 trycloudflare.com 的行
                        if "trycloudflare.com" in line and "https://" in line:
                            # 提取URL
                            parts = line.split()
                            for part in parts:
                                if "https://" in part and "trycloudflare.com" in part:
                                    self.public_url = part
                                    print(f"🌍 公网地址: {self.public_url}")
                                    print("🎉 成功！现在任何人都可以访问你的网站了！")
                                    break
                        # 显示重要信息
                        if "INF" in line or "ERR" in line:
                            print(f"📡 {line}")
            except:
                pass
        
        # 在后台线程中监控输出
        monitor_thread = threading.Thread(target=read_output, daemon=True)
        monitor_thread.start()
    
    def stop_tunnel(self):
        """停止隧道"""
        if self.tunnel_process:
            self.tunnel_process.terminate()
            print("🛑 Cloudflare 隧道已停止")

def main():
    """主函数"""
    print("🌐 Cloudflare Tunnel 快速启动")
    print("="*50)
    print("✨ 特点：")
    print("   - 完全免费，无需注册")
    print("   - 自动提供 HTTPS")
    print("   - 全球访问")
    print("   - 无时间限制")
    print("="*50)
    
    # 检查 cloudflared 是否存在
    if not os.path.exists("cloudflared.exe"):
        print("❌ 未找到 cloudflared.exe")
        print("📥 正在下载...")
        try:
            import requests
            url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
            response = requests.get(url)
            with open("cloudflared.exe", "wb") as f:
                f.write(response.content)
            print("✅ 下载完成")
        except Exception as e:
            print(f"❌ 下载失败: {e}")
            return
    
    # 创建隧道管理器
    tunnel_manager = CloudflareTunnelManager()
    
    # 启动隧道
    if tunnel_manager.start_quick_tunnel():
        print("\n🔧 正在启动 Flask 应用...")
        
        # 创建并启动应用
        crypto_app = CryptoWebApp()
        local_ip = crypto_app.get_local_ip()
        
        print("\n" + "="*60)
        print("🎉 服务器启动成功！")
        print("="*60)
        print("📍 访问地址：")
        print(f"   本地访问: http://127.0.0.1:5000")
        print(f"   局域网访问: http://{local_ip}:5000")
        
        if tunnel_manager.public_url:
            print(f"   🌍 全球访问: {tunnel_manager.public_url}")
        else:
            print("   🌍 全球访问: 正在获取地址...")
        
        print("\n🔄 功能特性：")
        print("   - 实时价格更新（每5秒）")
        print("   - 价格变化动画效果")
        print("   - 移动端完美适配")
        print("   - 全球任何人都可访问")
        print("   - 自动 HTTPS 加密")
        print("="*60)
        
        try:
            # 启动 Flask 应用
            crypto_app.run(debug=False, host='127.0.0.1', port=5000)
        except KeyboardInterrupt:
            print("\n👋 正在关闭服务器...")
            tunnel_manager.stop_tunnel()
            print("✅ 服务器已关闭")
    else:
        print("❌ 隧道启动失败，请检查网络连接")

if __name__ == '__main__':
    main()