#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统防护监控脚本
实时监控系统状态和防护效果
"""

import psutil
import time
import threading
import json
from datetime import datetime
from typing import Dict, List
import matplotlib.pyplot as plt
import numpy as np
from collections import deque
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('system_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SystemMonitor:
    """系统监控类"""
    
    def __init__(self, max_history=1000):
        self.max_history = max_history
        self.monitoring = False
        
        # 历史数据存储
        self.cpu_history = deque(maxlen=max_history)
        self.memory_history = deque(maxlen=max_history)
        self.network_history = deque(maxlen=max_history)
        self.disk_history = deque(maxlen=max_history)
        self.timestamp_history = deque(maxlen=max_history)
        
        # 网络统计
        self.network_stats = {
            'bytes_sent': 0,
            'bytes_recv': 0,
            'packets_sent': 0,
            'packets_recv': 0
        }
        
        # 进程监控
        self.process_monitor = {}
        
    def start_monitoring(self, interval=1):
        """开始监控"""
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, args=(interval,))
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        logger.info("系统监控已启动")
    
    def stop_monitoring(self):
        """停止监控"""
        self.monitoring = False
        logger.info("系统监控已停止")
    
    def _monitor_loop(self, interval):
        """监控循环"""
        last_network = psutil.net_io_counters()
        
        while self.monitoring:
            try:
                current_time = time.time()
                
                # CPU使用率
                cpu_percent = psutil.cpu_percent(interval=0.1)
                
                # 内存使用率
                memory = psutil.virtual_memory()
                memory_percent = memory.percent
                
                # 网络IO
                current_network = psutil.net_io_counters()
                network_speed = {
                    'bytes_sent_per_sec': (current_network.bytes_sent - last_network.bytes_sent) / interval,
                    'bytes_recv_per_sec': (current_network.bytes_recv - last_network.bytes_recv) / interval,
                    'packets_sent_per_sec': (current_network.packets_sent - last_network.packets_sent) / interval,
                    'packets_recv_per_sec': (current_network.packets_recv - last_network.packets_recv) / interval
                }
                last_network = current_network
                
                # 磁盘使用率
                disk = psutil.disk_usage('/')
                disk_percent = disk.percent
                
                # 存储历史数据
                self.cpu_history.append(cpu_percent)
                self.memory_history.append(memory_percent)
                self.network_history.append(network_speed)
                self.disk_history.append(disk_percent)
                self.timestamp_history.append(current_time)
                
                # 更新网络统计
                self.network_stats = {
                    'bytes_sent': current_network.bytes_sent,
                    'bytes_recv': current_network.bytes_recv,
                    'packets_sent': current_network.packets_sent,
                    'packets_recv': current_network.packets_recv
                }
                
                time.sleep(interval)
                
            except Exception as e:
                logger.error(f"监控过程中发生错误: {e}")
                time.sleep(interval)
    
    def get_current_status(self) -> Dict:
        """获取当前系统状态"""
        try:
            # 基本系统信息
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            network = psutil.net_io_counters()
            
            # 负载平均值 (仅Linux/Unix)
            try:
                load_avg = psutil.getloadavg()
            except AttributeError:
                load_avg = (0, 0, 0)  # Windows不支持
            
            # 进程数量
            process_count = len(psutil.pids())
            
            # 网络连接数
            try:
                connections = len(psutil.net_connections())
            except psutil.AccessDenied:
                connections = 0
            
            status = {
                "时间戳": datetime.now().isoformat(),
                "CPU": {
                    "使用率": f"{cpu_percent}%",
                    "核心数": psutil.cpu_count(),
                    "负载平均": load_avg
                },
                "内存": {
                    "使用率": f"{memory.percent}%",
                    "总内存": f"{memory.total / (1024**3):.2f}GB",
                    "已使用": f"{memory.used / (1024**3):.2f}GB",
                    "可用": f"{memory.available / (1024**3):.2f}GB"
                },
                "磁盘": {
                    "使用率": f"{disk.percent}%",
                    "总空间": f"{disk.total / (1024**3):.2f}GB",
                    "已使用": f"{disk.used / (1024**3):.2f}GB",
                    "可用": f"{disk.free / (1024**3):.2f}GB"
                },
                "网络": {
                    "发送字节": f"{network.bytes_sent / (1024**2):.2f}MB",
                    "接收字节": f"{network.bytes_recv / (1024**2):.2f}MB",
                    "发送包数": network.packets_sent,
                    "接收包数": network.packets_recv,
                    "连接数": connections
                },
                "系统": {
                    "进程数": process_count,
                    "启动时间": datetime.fromtimestamp(psutil.boot_time()).isoformat()
                }
            }
            
            return status
            
        except Exception as e:
            logger.error(f"获取系统状态时发生错误: {e}")
            return {}
    
    def analyze_performance(self) -> Dict:
        """分析系统性能"""
        if not self.cpu_history:
            return {"错误": "没有监控数据"}
        
        # 计算统计数据
        cpu_avg = np.mean(self.cpu_history)
        cpu_max = np.max(self.cpu_history)
        memory_avg = np.mean(self.memory_history)
        memory_max = np.max(self.memory_history)
        
        # 网络流量统计
        total_recv_speed = sum(net['bytes_recv_per_sec'] for net in self.network_history)
        total_sent_speed = sum(net['bytes_sent_per_sec'] for net in self.network_history)
        avg_recv_speed = total_recv_speed / len(self.network_history) if self.network_history else 0
        avg_sent_speed = total_sent_speed / len(self.network_history) if self.network_history else 0
        
        # 性能评估
        performance_score = self._calculate_performance_score(cpu_avg, memory_avg)
        
        analysis = {
            "监控时长": f"{len(self.cpu_history)}秒",
            "CPU性能": {
                "平均使用率": f"{cpu_avg:.2f}%",
                "最高使用率": f"{cpu_max:.2f}%",
                "状态": self._get_cpu_status(cpu_avg, cpu_max)
            },
            "内存性能": {
                "平均使用率": f"{memory_avg:.2f}%",
                "最高使用率": f"{memory_max:.2f}%",
                "状态": self._get_memory_status(memory_avg, memory_max)
            },
            "网络性能": {
                "平均接收速度": f"{avg_recv_speed / 1024:.2f}KB/s",
                "平均发送速度": f"{avg_sent_speed / 1024:.2f}KB/s",
                "状态": self._get_network_status(avg_recv_speed, avg_sent_speed)
            },
            "综合评分": f"{performance_score}/100",
            "系统状态": self._get_overall_status(performance_score)
        }
        
        return analysis
    
    def _calculate_performance_score(self, cpu_avg, memory_avg):
        """计算性能评分"""
        cpu_score = max(0, 100 - cpu_avg)
        memory_score = max(0, 100 - memory_avg)
        return int((cpu_score + memory_score) / 2)
    
    def _get_cpu_status(self, avg, max_val):
        """获取CPU状态"""
        if avg < 30:
            return "🟢 良好"
        elif avg < 60:
            return "🟡 中等"
        elif avg < 80:
            return "🟠 较高"
        else:
            return "🔴 过载"
    
    def _get_memory_status(self, avg, max_val):
        """获取内存状态"""
        if avg < 50:
            return "🟢 充足"
        elif avg < 70:
            return "🟡 适中"
        elif avg < 85:
            return "🟠 紧张"
        else:
            return "🔴 不足"
    
    def _get_network_status(self, recv_speed, sent_speed):
        """获取网络状态"""
        total_speed = (recv_speed + sent_speed) / 1024  # KB/s
        if total_speed < 100:
            return "🟢 正常"
        elif total_speed < 1000:
            return "🟡 活跃"
        elif total_speed < 10000:
            return "🟠 繁忙"
        else:
            return "🔴 拥堵"
    
    def _get_overall_status(self, score):
        """获取整体状态"""
        if score >= 80:
            return "🟢 优秀 - 系统运行良好"
        elif score >= 60:
            return "🟡 良好 - 系统运行正常"
        elif score >= 40:
            return "🟠 一般 - 需要关注"
        else:
            return "🔴 警告 - 系统负载过高"
    
    def generate_charts(self, save_path="system_monitor"):
        """生成监控图表"""
        if not self.cpu_history:
            logger.warning("没有监控数据可用于生成图表")
            return
        
        # 时间轴
        time_points = list(range(len(self.cpu_history)))
        
        # 创建图表
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('系统性能监控报告', fontsize=16)
        
        # 1. CPU使用率
        ax1.plot(time_points, list(self.cpu_history), color='red', linewidth=1)
        ax1.set_title('CPU使用率')
        ax1.set_xlabel('时间 (秒)')
        ax1.set_ylabel('使用率 (%)')
        ax1.grid(True, alpha=0.3)
        ax1.set_ylim(0, 100)
        
        # 2. 内存使用率
        ax2.plot(time_points, list(self.memory_history), color='blue', linewidth=1)
        ax2.set_title('内存使用率')
        ax2.set_xlabel('时间 (秒)')
        ax2.set_ylabel('使用率 (%)')
        ax2.grid(True, alpha=0.3)
        ax2.set_ylim(0, 100)
        
        # 3. 网络流量
        if self.network_history:
            recv_speeds = [net['bytes_recv_per_sec'] / 1024 for net in self.network_history]  # KB/s
            sent_speeds = [net['bytes_sent_per_sec'] / 1024 for net in self.network_history]  # KB/s
            
            ax3.plot(time_points, recv_speeds, label='接收', color='green', linewidth=1)
            ax3.plot(time_points, sent_speeds, label='发送', color='orange', linewidth=1)
            ax3.set_title('网络流量')
            ax3.set_xlabel('时间 (秒)')
            ax3.set_ylabel('速度 (KB/s)')
            ax3.legend()
            ax3.grid(True, alpha=0.3)
        
        # 4. 磁盘使用率
        ax4.plot(time_points, list(self.disk_history), color='purple', linewidth=1)
        ax4.set_title('磁盘使用率')
        ax4.set_xlabel('时间 (秒)')
        ax4.set_ylabel('使用率 (%)')
        ax4.grid(True, alpha=0.3)
        ax4.set_ylim(0, 100)
        
        plt.tight_layout()
        plt.savefig(f'{save_path}.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        logger.info(f"监控图表已保存到 {save_path}.png")
    
    def save_report(self, filename="system_monitor_report.json"):
        """保存监控报告"""
        report = {
            "报告生成时间": datetime.now().isoformat(),
            "当前系统状态": self.get_current_status(),
            "性能分析": self.analyze_performance(),
            "历史数据": {
                "CPU历史": list(self.cpu_history),
                "内存历史": list(self.memory_history),
                "磁盘历史": list(self.disk_history),
                "时间戳": [datetime.fromtimestamp(ts).isoformat() for ts in self.timestamp_history]
            }
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        logger.info(f"监控报告已保存到 {filename}")

def main():
    """主函数"""
    print("🖥️  系统防护监控工具")
    print("实时监控系统状态和性能指标")
    print("-" * 40)
    
    monitor = SystemMonitor()
    
    try:
        # 显示当前状态
        print("📊 当前系统状态:")
        current_status = monitor.get_current_status()
        for category, data in current_status.items():
            if category != "时间戳":
                print(f"\n{category}:")
                if isinstance(data, dict):
                    for key, value in data.items():
                        print(f"  {key}: {value}")
        
        # 询问是否开始监控
        print("\n" + "=" * 40)
        duration = input("🕐 监控时长(秒) (默认: 60): ").strip()
        duration = int(duration) if duration.isdigit() else 60
        
        print(f"\n🚀 开始监控 {duration} 秒...")
        monitor.start_monitoring(interval=1)
        
        # 实时显示监控信息
        for i in range(duration):
            if monitor.cpu_history:
                cpu_current = monitor.cpu_history[-1]
                memory_current = monitor.memory_history[-1]
                print(f"\r⏱️  {i+1:3d}s | CPU: {cpu_current:5.1f}% | 内存: {memory_current:5.1f}%", end="")
            time.sleep(1)
        
        monitor.stop_monitoring()
        print("\n\n✅ 监控完成!")
        
        # 分析结果
        print("\n📈 性能分析结果:")
        analysis = monitor.analyze_performance()
        for category, data in analysis.items():
            if isinstance(data, dict):
                print(f"\n{category}:")
                for key, value in data.items():
                    print(f"  {key}: {value}")
            else:
                print(f"{category}: {data}")
        
        # 保存报告
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if input("\n💾 是否保存监控报告? (y/n): ").lower() == 'y':
            monitor.save_report(f"system_monitor_{timestamp}.json")
        
        # 生成图表
        if input("📊 是否生成监控图表? (y/n): ").lower() == 'y':
            monitor.generate_charts(f"system_monitor_{timestamp}")
            
    except KeyboardInterrupt:
        print("\n\n⏹️  监控被用户中断")
        monitor.stop_monitoring()
    except Exception as e:
        print(f"\n❌ 监控过程中发生错误: {e}")
        monitor.stop_monitoring()

if __name__ == "__main__":
    # 设置中文字体支持
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
    plt.rcParams['axes.unicode_minus'] = False
    
    main()