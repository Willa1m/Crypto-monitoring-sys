#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网络访问压力测试程序
用于测试系统防护能力和性能监控
"""

import asyncio
import aiohttp
import time
import threading
import statistics
from datetime import datetime
from typing import List, Dict, Any
import json
import logging
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import matplotlib.pyplot as plt
import numpy as np

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('stress_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class TestResult:
    """测试结果数据类"""
    timestamp: float
    response_time: float
    status_code: int
    success: bool
    error_message: str = ""

class NetworkStressTest:
    """网络压力测试类"""
    
    def __init__(self, target_url: str = "http://127.0.0.1:5000"):
        self.target_url = target_url
        self.results: List[TestResult] = []
        self.start_time = None
        self.end_time = None
        self.is_running = False
        
    async def single_request(self, session: aiohttp.ClientSession, request_id: int) -> TestResult:
        """执行单个HTTP请求"""
        start_time = time.time()
        try:
            async with session.get(self.target_url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                await response.text()  # 读取响应内容
                end_time = time.time()
                
                return TestResult(
                    timestamp=start_time,
                    response_time=(end_time - start_time) * 1000,  # 转换为毫秒
                    status_code=response.status,
                    success=response.status == 200
                )
        except asyncio.TimeoutError:
            return TestResult(
                timestamp=start_time,
                response_time=(time.time() - start_time) * 1000,
                status_code=408,
                success=False,
                error_message="请求超时"
            )
        except Exception as e:
            return TestResult(
                timestamp=start_time,
                response_time=(time.time() - start_time) * 1000,
                status_code=0,
                success=False,
                error_message=str(e)
            )
    
    async def burst_test(self, concurrent_requests: int, total_requests: int) -> List[TestResult]:
        """执行突发访问测试"""
        logger.info(f"开始突发测试: {concurrent_requests} 并发, 总计 {total_requests} 请求")
        
        connector = aiohttp.TCPConnector(limit=concurrent_requests * 2)
        async with aiohttp.ClientSession(connector=connector) as session:
            tasks = []
            for i in range(total_requests):
                task = asyncio.create_task(self.single_request(session, i))
                tasks.append(task)
                
                # 控制并发数量
                if len(tasks) >= concurrent_requests:
                    completed_tasks = await asyncio.gather(*tasks, return_exceptions=True)
                    for result in completed_tasks:
                        if isinstance(result, TestResult):
                            self.results.append(result)
                    tasks = []
            
            # 处理剩余任务
            if tasks:
                completed_tasks = await asyncio.gather(*tasks, return_exceptions=True)
                for result in completed_tasks:
                    if isinstance(result, TestResult):
                        self.results.append(result)
        
        return self.results
    
    async def sustained_test(self, requests_per_second: int, duration_seconds: int) -> List[TestResult]:
        """执行持续访问测试"""
        logger.info(f"开始持续测试: {requests_per_second} RPS, 持续 {duration_seconds} 秒")
        
        interval = 1.0 / requests_per_second
        end_time = time.time() + duration_seconds
        
        connector = aiohttp.TCPConnector(limit=100)
        async with aiohttp.ClientSession(connector=connector) as session:
            request_id = 0
            while time.time() < end_time:
                start = time.time()
                
                # 发送请求
                result = await self.single_request(session, request_id)
                self.results.append(result)
                request_id += 1
                
                # 控制请求频率
                elapsed = time.time() - start
                if elapsed < interval:
                    await asyncio.sleep(interval - elapsed)
        
        return self.results
    
    def analyze_results(self) -> Dict[str, Any]:
        """分析测试结果"""
        if not self.results:
            return {}
        
        successful_requests = [r for r in self.results if r.success]
        failed_requests = [r for r in self.results if not r.success]
        response_times = [r.response_time for r in successful_requests]
        
        analysis = {
            "总请求数": len(self.results),
            "成功请求数": len(successful_requests),
            "失败请求数": len(failed_requests),
            "成功率": len(successful_requests) / len(self.results) * 100 if self.results else 0,
            "平均响应时间(ms)": statistics.mean(response_times) if response_times else 0,
            "最小响应时间(ms)": min(response_times) if response_times else 0,
            "最大响应时间(ms)": max(response_times) if response_times else 0,
            "响应时间中位数(ms)": statistics.median(response_times) if response_times else 0,
            "95%分位响应时间(ms)": np.percentile(response_times, 95) if response_times else 0,
            "99%分位响应时间(ms)": np.percentile(response_times, 99) if response_times else 0,
        }
        
        # 统计错误类型
        error_types = {}
        for result in failed_requests:
            error_key = f"HTTP {result.status_code}" if result.status_code > 0 else "网络错误"
            error_types[error_key] = error_types.get(error_key, 0) + 1
        
        analysis["错误统计"] = error_types
        
        return analysis
    
    def generate_charts(self, save_path: str = "stress_test_results"):
        """生成测试结果图表"""
        if not self.results:
            logger.warning("没有测试结果可用于生成图表")
            return
        
        # 准备数据
        timestamps = [(r.timestamp - self.results[0].timestamp) for r in self.results]
        response_times = [r.response_time for r in self.results]
        success_flags = [1 if r.success else 0 for r in self.results]
        
        # 创建图表
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('网络压力测试结果分析', fontsize=16)
        
        # 1. 响应时间趋势图
        ax1.plot(timestamps, response_times, alpha=0.7, linewidth=0.5)
        ax1.set_title('响应时间趋势')
        ax1.set_xlabel('时间 (秒)')
        ax1.set_ylabel('响应时间 (毫秒)')
        ax1.grid(True, alpha=0.3)
        
        # 2. 响应时间分布直方图
        successful_times = [r.response_time for r in self.results if r.success]
        if successful_times:
            ax2.hist(successful_times, bins=50, alpha=0.7, edgecolor='black')
            ax2.set_title('响应时间分布')
            ax2.set_xlabel('响应时间 (毫秒)')
            ax2.set_ylabel('频次')
            ax2.grid(True, alpha=0.3)
        
        # 3. 成功率趋势图
        window_size = max(1, len(success_flags) // 100)
        success_rate_trend = []
        time_windows = []
        
        for i in range(0, len(success_flags), window_size):
            window = success_flags[i:i+window_size]
            success_rate = sum(window) / len(window) * 100
            success_rate_trend.append(success_rate)
            time_windows.append(timestamps[i])
        
        ax3.plot(time_windows, success_rate_trend, marker='o', markersize=2)
        ax3.set_title('成功率趋势')
        ax3.set_xlabel('时间 (秒)')
        ax3.set_ylabel('成功率 (%)')
        ax3.set_ylim(0, 105)
        ax3.grid(True, alpha=0.3)
        
        # 4. 状态码分布饼图
        status_codes = {}
        for result in self.results:
            code = result.status_code if result.status_code > 0 else "网络错误"
            status_codes[code] = status_codes.get(code, 0) + 1
        
        if status_codes:
            labels = list(status_codes.keys())
            sizes = list(status_codes.values())
            ax4.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
            ax4.set_title('HTTP状态码分布')
        
        plt.tight_layout()
        plt.savefig(f'{save_path}.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        logger.info(f"图表已保存到 {save_path}.png")
    
    def save_results(self, filename: str = "stress_test_results.json"):
        """保存测试结果到文件"""
        data = {
            "测试配置": {
                "目标URL": self.target_url,
                "开始时间": datetime.fromtimestamp(self.start_time).isoformat() if self.start_time else None,
                "结束时间": datetime.fromtimestamp(self.end_time).isoformat() if self.end_time else None,
                "测试持续时间": self.end_time - self.start_time if self.start_time and self.end_time else None
            },
            "测试结果": [
                {
                    "时间戳": r.timestamp,
                    "响应时间": r.response_time,
                    "状态码": r.status_code,
                    "成功": r.success,
                    "错误信息": r.error_message
                }
                for r in self.results
            ],
            "统计分析": self.analyze_results()
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"测试结果已保存到 {filename}")

class RealTimeMonitor:
    """实时监控类"""
    
    def __init__(self, stress_test: NetworkStressTest):
        self.stress_test = stress_test
        self.monitoring = False
    
    def start_monitoring(self):
        """开始实时监控"""
        self.monitoring = True
        monitor_thread = threading.Thread(target=self._monitor_loop)
        monitor_thread.daemon = True
        monitor_thread.start()
    
    def stop_monitoring(self):
        """停止实时监控"""
        self.monitoring = False
    
    def _monitor_loop(self):
        """监控循环"""
        while self.monitoring:
            if self.stress_test.results:
                recent_results = self.stress_test.results[-100:]  # 最近100个结果
                successful = [r for r in recent_results if r.success]
                
                if recent_results:
                    success_rate = len(successful) / len(recent_results) * 100
                    avg_response_time = statistics.mean([r.response_time for r in successful]) if successful else 0
                    
                    print(f"\r实时监控 - 总请求: {len(self.stress_test.results)}, "
                          f"成功率: {success_rate:.1f}%, "
                          f"平均响应时间: {avg_response_time:.1f}ms", end="")
            
            time.sleep(1)

async def main():
    """主函数"""
    print("=== 网络压力测试程序 ===")
    print("1. 突发访问测试")
    print("2. 持续访问测试")
    print("3. 自定义测试")
    
    choice = input("请选择测试类型 (1-3): ").strip()
    
    target_url = input("请输入目标URL (默认: http://127.0.0.1:5000): ").strip()
    if not target_url:
        target_url = "http://127.0.0.1:5000"
    
    stress_test = NetworkStressTest(target_url)
    monitor = RealTimeMonitor(stress_test)
    
    stress_test.start_time = time.time()
    
    try:
        if choice == "1":
            # 突发访问测试
            concurrent = int(input("并发请求数 (默认: 50): ") or "50")
            total = int(input("总请求数 (默认: 1000): ") or "1000")
            
            print(f"\n开始突发访问测试...")
            monitor.start_monitoring()
            await stress_test.burst_test(concurrent, total)
            
        elif choice == "2":
            # 持续访问测试
            rps = int(input("每秒请求数 (默认: 10): ") or "10")
            duration = int(input("持续时间(秒) (默认: 60): ") or "60")
            
            print(f"\n开始持续访问测试...")
            monitor.start_monitoring()
            await stress_test.sustained_test(rps, duration)
            
        elif choice == "3":
            # 自定义测试
            print("自定义测试模式 - 可以组合多种测试")
            # 这里可以添加更复杂的测试逻辑
            concurrent = int(input("并发请求数 (默认: 20): ") or "20")
            total = int(input("总请求数 (默认: 500): ") or "500")
            await stress_test.burst_test(concurrent, total)
        
        else:
            print("无效选择")
            return
            
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
    except Exception as e:
        logger.error(f"测试过程中发生错误: {e}")
    finally:
        monitor.stop_monitoring()
        stress_test.end_time = time.time()
    
    print("\n\n=== 测试完成 ===")
    
    # 分析结果
    analysis = stress_test.analyze_results()
    print("\n测试结果分析:")
    for key, value in analysis.items():
        if key != "错误统计":
            print(f"{key}: {value}")
    
    if "错误统计" in analysis and analysis["错误统计"]:
        print("\n错误统计:")
        for error_type, count in analysis["错误统计"].items():
            print(f"  {error_type}: {count}")
    
    # 保存结果
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    stress_test.save_results(f"stress_test_{timestamp}.json")
    
    # 生成图表
    if input("\n是否生成图表? (y/n): ").lower() == 'y':
        stress_test.generate_charts(f"stress_test_chart_{timestamp}")

if __name__ == "__main__":
    # 设置中文字体支持
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
    plt.rcParams['axes.unicode_minus'] = False
    
    asyncio.run(main())