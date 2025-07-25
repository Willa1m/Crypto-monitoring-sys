#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速网络轰炸测试脚本
用于快速测试系统防护能力
"""

import asyncio
import aiohttp
import time
import statistics
from datetime import datetime
import json

class QuickStressTest:
    """快速压力测试类"""
    
    def __init__(self, target_url="http://127.0.0.1:5000"):
        self.target_url = target_url
        self.results = []
    
    async def quick_bomb_test(self, concurrent=100, total=1000):
        """快速轰炸测试"""
        print(f"🚀 开始网络轰炸测试")
        print(f"📊 目标: {self.target_url}")
        print(f"⚡ 并发数: {concurrent}, 总请求: {total}")
        print("=" * 50)
        
        start_time = time.time()
        
        # 创建连接池
        connector = aiohttp.TCPConnector(limit=concurrent * 2)
        timeout = aiohttp.ClientTimeout(total=5)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            # 分批发送请求
            batch_size = concurrent
            for batch_start in range(0, total, batch_size):
                batch_end = min(batch_start + batch_size, total)
                batch_tasks = []
                
                # 创建当前批次的任务
                for i in range(batch_start, batch_end):
                    task = asyncio.create_task(self._single_request(session, i))
                    batch_tasks.append(task)
                
                # 等待当前批次完成
                batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
                
                # 处理结果
                for result in batch_results:
                    if isinstance(result, dict):
                        self.results.append(result)
                
                # 显示进度
                progress = len(self.results) / total * 100
                print(f"📈 进度: {progress:.1f}% ({len(self.results)}/{total})")
        
        end_time = time.time()
        duration = end_time - start_time
        
        print("=" * 50)
        print(f"⏱️  测试完成，耗时: {duration:.2f}秒")
        
        return self._analyze_results(duration)
    
    async def _single_request(self, session, request_id):
        """执行单个请求"""
        start_time = time.time()
        try:
            async with session.get(self.target_url) as response:
                await response.text()
                end_time = time.time()
                
                return {
                    'id': request_id,
                    'response_time': (end_time - start_time) * 1000,
                    'status_code': response.status,
                    'success': response.status == 200,
                    'timestamp': start_time
                }
        except asyncio.TimeoutError:
            return {
                'id': request_id,
                'response_time': (time.time() - start_time) * 1000,
                'status_code': 408,
                'success': False,
                'error': '超时',
                'timestamp': start_time
            }
        except Exception as e:
            return {
                'id': request_id,
                'response_time': (time.time() - start_time) * 1000,
                'status_code': 0,
                'success': False,
                'error': str(e),
                'timestamp': start_time
            }
    
    def _analyze_results(self, duration):
        """分析测试结果"""
        if not self.results:
            return {}
        
        successful = [r for r in self.results if r.get('success', False)]
        failed = [r for r in self.results if not r.get('success', False)]
        response_times = [r['response_time'] for r in successful]
        
        # 计算QPS
        qps = len(self.results) / duration if duration > 0 else 0
        
        analysis = {
            "🎯 测试概览": {
                "总请求数": len(self.results),
                "成功请求": len(successful),
                "失败请求": len(failed),
                "成功率": f"{len(successful) / len(self.results) * 100:.2f}%" if self.results else "0%",
                "测试时长": f"{duration:.2f}秒",
                "平均QPS": f"{qps:.2f}"
            }
        }
        
        if response_times:
            analysis["⚡ 性能指标"] = {
                "平均响应时间": f"{statistics.mean(response_times):.2f}ms",
                "最快响应": f"{min(response_times):.2f}ms",
                "最慢响应": f"{max(response_times):.2f}ms",
                "响应时间中位数": f"{statistics.median(response_times):.2f}ms"
            }
        
        # 错误统计
        if failed:
            error_stats = {}
            for result in failed:
                error_key = f"HTTP {result.get('status_code', 0)}"
                if result.get('error'):
                    error_key += f" ({result['error']})"
                error_stats[error_key] = error_stats.get(error_key, 0) + 1
            
            analysis["❌ 错误统计"] = error_stats
        
        # 系统防护评估
        analysis["🛡️ 系统防护评估"] = self._evaluate_protection()
        
        return analysis
    
    def _evaluate_protection(self):
        """评估系统防护效果"""
        if not self.results:
            return "无法评估"
        
        success_rate = len([r for r in self.results if r.get('success', False)]) / len(self.results)
        avg_response_time = statistics.mean([r['response_time'] for r in self.results if r.get('success', False)]) if any(r.get('success', False) for r in self.results) else 0
        
        protection_level = "未知"
        recommendations = []
        
        if success_rate > 0.95:
            if avg_response_time < 100:
                protection_level = "🟢 优秀 - 系统稳定，响应迅速"
            elif avg_response_time < 500:
                protection_level = "🟡 良好 - 系统稳定，响应稍慢"
                recommendations.append("考虑优化响应时间")
            else:
                protection_level = "🟠 一般 - 系统稳定但响应较慢"
                recommendations.append("需要优化系统性能")
        elif success_rate > 0.8:
            protection_level = "🟠 一般 - 部分请求失败"
            recommendations.append("检查系统负载均衡")
            recommendations.append("考虑增加服务器资源")
        elif success_rate > 0.5:
            protection_level = "🔴 较差 - 大量请求失败"
            recommendations.append("紧急检查系统状态")
            recommendations.append("可能需要限流保护")
        else:
            protection_level = "🚨 危险 - 系统可能过载"
            recommendations.append("立即检查系统状态")
            recommendations.append("建议启用紧急保护措施")
        
        return {
            "防护等级": protection_level,
            "建议措施": recommendations if recommendations else ["系统运行良好"]
        }
    
    def print_results(self, analysis):
        """打印测试结果"""
        print("\n" + "=" * 60)
        print("📊 网络轰炸测试结果报告")
        print("=" * 60)
        
        for category, data in analysis.items():
            print(f"\n{category}:")
            if isinstance(data, dict):
                for key, value in data.items():
                    if isinstance(value, list):
                        print(f"  {key}:")
                        for item in value:
                            print(f"    • {item}")
                    else:
                        print(f"  {key}: {value}")
            else:
                print(f"  {data}")
        
        print("\n" + "=" * 60)
    
    def save_report(self, analysis):
        """保存测试报告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"stress_test_report_{timestamp}.json"
        
        report = {
            "测试时间": datetime.now().isoformat(),
            "目标URL": self.target_url,
            "原始数据": self.results,
            "分析结果": analysis
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"📄 详细报告已保存到: {filename}")

async def main():
    """主函数"""
    print("🎯 快速网络轰炸测试工具")
    print("用于测试系统防护能力和性能表现")
    print("-" * 40)
    
    # 获取用户输入
    target = input("🌐 目标URL (默认: http://127.0.0.1:5000): ").strip()
    if not target:
        target = "http://127.0.0.1:5000"
    
    concurrent = input("⚡ 并发数 (默认: 100): ").strip()
    concurrent = int(concurrent) if concurrent.isdigit() else 100
    
    total = input("📊 总请求数 (默认: 1000): ").strip()
    total = int(total) if total.isdigit() else 1000
    
    # 确认测试
    print(f"\n⚠️  即将对 {target} 发起 {concurrent} 并发 {total} 次请求")
    confirm = input("确认开始测试? (y/n): ").lower()
    
    if confirm != 'y':
        print("❌ 测试已取消")
        return
    
    # 执行测试
    tester = QuickStressTest(target)
    
    try:
        analysis = await tester.quick_bomb_test(concurrent, total)
        tester.print_results(analysis)
        
        # 询问是否保存报告
        if input("\n💾 是否保存详细报告? (y/n): ").lower() == 'y':
            tester.save_report(analysis)
            
    except KeyboardInterrupt:
        print("\n\n⏹️  测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")

if __name__ == "__main__":
    asyncio.run(main())