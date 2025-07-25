#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
综合防护测试脚本
同时进行网络压力测试和系统监控，全面评估系统防护能力
"""

import asyncio
import threading
import time
import json
from datetime import datetime
from quick_stress_test import QuickStressTest
from system_monitor import SystemMonitor
import matplotlib.pyplot as plt
import numpy as np

class ComprehensiveProtectionTest:
    """综合防护测试类"""
    
    def __init__(self, target_url="http://127.0.0.1:5000"):
        self.target_url = target_url
        self.stress_tester = QuickStressTest(target_url)
        self.system_monitor = SystemMonitor()
        self.test_results = {}
        
    async def run_comprehensive_test(self, concurrent=100, total=1000, monitor_duration=None):
        """运行综合测试"""
        print("🎯 启动综合防护测试")
        print("=" * 50)
        
        # 如果没有指定监控时长，估算测试时间
        if monitor_duration is None:
            estimated_duration = max(60, total // concurrent * 2)  # 估算测试时间
            monitor_duration = estimated_duration + 30  # 额外30秒缓冲
        
        print(f"📊 测试配置:")
        print(f"  目标URL: {self.target_url}")
        print(f"  并发数: {concurrent}")
        print(f"  总请求: {total}")
        print(f"  监控时长: {monitor_duration}秒")
        print("=" * 50)
        
        # 记录测试开始时间
        test_start_time = time.time()
        
        # 获取测试前的系统状态
        print("📋 获取基线系统状态...")
        baseline_status = self.system_monitor.get_current_status()
        
        # 启动系统监控
        print("🖥️  启动系统监控...")
        self.system_monitor.start_monitoring(interval=1)
        
        # 等待2秒让监控稳定
        await asyncio.sleep(2)
        
        # 启动压力测试
        print("🚀 启动网络压力测试...")
        stress_start_time = time.time()
        
        # 创建压力测试任务
        stress_task = asyncio.create_task(
            self.stress_tester.quick_bomb_test(concurrent, total)
        )
        
        # 创建监控显示任务
        monitor_task = asyncio.create_task(
            self._monitor_display(monitor_duration)
        )
        
        try:
            # 等待压力测试完成
            stress_results = await stress_task
            stress_end_time = time.time()
            
            print(f"\n✅ 压力测试完成，耗时: {stress_end_time - stress_start_time:.2f}秒")
            
            # 继续监控一段时间观察系统恢复
            remaining_time = monitor_duration - (time.time() - test_start_time)
            if remaining_time > 0:
                print(f"⏳ 继续监控系统恢复状态 {remaining_time:.0f}秒...")
                await asyncio.sleep(remaining_time)
            
            # 取消监控显示任务
            monitor_task.cancel()
            
        except Exception as e:
            print(f"❌ 测试过程中发生错误: {e}")
            monitor_task.cancel()
            raise
        finally:
            # 停止系统监控
            self.system_monitor.stop_monitoring()
        
        # 获取测试后的系统状态
        print("\n📋 获取测试后系统状态...")
        final_status = self.system_monitor.get_current_status()
        
        # 分析结果
        print("\n📊 分析测试结果...")
        comprehensive_analysis = self._analyze_comprehensive_results(
            baseline_status, final_status, stress_results
        )
        
        # 保存结果
        self.test_results = {
            "测试配置": {
                "目标URL": self.target_url,
                "并发数": concurrent,
                "总请求数": total,
                "监控时长": monitor_duration,
                "测试开始时间": datetime.fromtimestamp(test_start_time).isoformat(),
                "测试结束时间": datetime.now().isoformat()
            },
            "基线状态": baseline_status,
            "最终状态": final_status,
            "压力测试结果": stress_results,
            "系统监控结果": self.system_monitor.analyze_performance(),
            "综合分析": comprehensive_analysis
        }
        
        return self.test_results
    
    async def _monitor_display(self, duration):
        """监控显示任务"""
        start_time = time.time()
        try:
            while time.time() - start_time < duration:
                if (self.system_monitor.cpu_history and 
                    self.stress_tester.results):
                    
                    # 系统状态
                    cpu_current = self.system_monitor.cpu_history[-1]
                    memory_current = self.system_monitor.memory_history[-1]
                    
                    # 压力测试状态
                    total_requests = len(self.stress_tester.results)
                    successful_requests = len([r for r in self.stress_tester.results if r.get('success', False)])
                    success_rate = successful_requests / total_requests * 100 if total_requests > 0 else 0
                    
                    elapsed = time.time() - start_time
                    print(f"\r⏱️  {elapsed:5.1f}s | CPU: {cpu_current:5.1f}% | 内存: {memory_current:5.1f}% | "
                          f"请求: {total_requests:4d} | 成功率: {success_rate:5.1f}%", end="")
                
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            pass
    
    def _analyze_comprehensive_results(self, baseline, final, stress_results):
        """综合分析测试结果"""
        analysis = {
            "🛡️ 系统防护评估": {},
            "📈 性能影响分析": {},
            "🔍 详细指标对比": {},
            "💡 优化建议": []
        }
        
        # 系统防护评估
        if stress_results and "🛡️ 系统防护评估" in stress_results:
            analysis["🛡️ 系统防护评估"] = stress_results["🛡️ 系统防护评估"]
        
        # 性能影响分析
        try:
            baseline_cpu = float(baseline["CPU"]["使用率"].replace("%", ""))
            final_cpu = float(final["CPU"]["使用率"].replace("%", ""))
            cpu_impact = final_cpu - baseline_cpu
            
            baseline_memory = float(baseline["内存"]["使用率"].replace("%", ""))
            final_memory = float(final["内存"]["使用率"].replace("%", ""))
            memory_impact = final_memory - baseline_memory
            
            analysis["📈 性能影响分析"] = {
                "CPU影响": f"{cpu_impact:+.2f}%",
                "内存影响": f"{memory_impact:+.2f}%",
                "系统恢复状态": self._evaluate_recovery(cpu_impact, memory_impact)
            }
        except (KeyError, ValueError) as e:
            analysis["📈 性能影响分析"] = {"错误": f"无法分析性能影响: {e}"}
        
        # 详细指标对比
        analysis["🔍 详细指标对比"] = {
            "测试前后CPU对比": {
                "测试前": baseline.get("CPU", {}).get("使用率", "未知"),
                "测试后": final.get("CPU", {}).get("使用率", "未知")
            },
            "测试前后内存对比": {
                "测试前": baseline.get("内存", {}).get("使用率", "未知"),
                "测试后": final.get("内存", {}).get("使用率", "未知")
            },
            "网络连接数对比": {
                "测试前": baseline.get("网络", {}).get("连接数", "未知"),
                "测试后": final.get("网络", {}).get("连接数", "未知")
            }
        }
        
        # 生成优化建议
        analysis["💡 优化建议"] = self._generate_recommendations(stress_results, baseline, final)
        
        return analysis
    
    def _evaluate_recovery(self, cpu_impact, memory_impact):
        """评估系统恢复状态"""
        if abs(cpu_impact) < 5 and abs(memory_impact) < 5:
            return "🟢 优秀 - 系统完全恢复"
        elif abs(cpu_impact) < 15 and abs(memory_impact) < 15:
            return "🟡 良好 - 系统基本恢复"
        elif abs(cpu_impact) < 30 and abs(memory_impact) < 30:
            return "🟠 一般 - 系统部分恢复"
        else:
            return "🔴 较差 - 系统恢复缓慢"
    
    def _generate_recommendations(self, stress_results, baseline, final):
        """生成优化建议"""
        recommendations = []
        
        # 基于压力测试结果的建议
        if stress_results and "🎯 测试概览" in stress_results:
            success_rate = float(stress_results["🎯 测试概览"]["成功率"].replace("%", ""))
            
            if success_rate < 50:
                recommendations.append("🚨 紧急: 成功率过低，建议立即检查服务器配置和负载均衡")
            elif success_rate < 80:
                recommendations.append("⚠️ 警告: 成功率偏低，建议优化服务器性能或增加限流保护")
            elif success_rate < 95:
                recommendations.append("💡 建议: 可以进一步优化响应时间和错误处理")
        
        # 基于系统监控的建议
        if self.system_monitor.cpu_history:
            max_cpu = max(self.system_monitor.cpu_history)
            avg_cpu = np.mean(self.system_monitor.cpu_history)
            
            if max_cpu > 90:
                recommendations.append("🔥 CPU: 峰值使用率过高，建议增加CPU资源或优化代码")
            elif avg_cpu > 70:
                recommendations.append("⚡ CPU: 平均使用率较高，建议监控CPU密集型操作")
        
        if self.system_monitor.memory_history:
            max_memory = max(self.system_monitor.memory_history)
            
            if max_memory > 85:
                recommendations.append("💾 内存: 使用率过高，建议增加内存或优化内存使用")
        
        # 通用建议
        recommendations.extend([
            "🔧 建议定期进行压力测试以监控系统性能",
            "📊 建议设置实时监控和告警机制",
            "🛡️ 建议实施适当的限流和防护策略"
        ])
        
        return recommendations
    
    def print_comprehensive_results(self):
        """打印综合测试结果"""
        if not self.test_results:
            print("❌ 没有测试结果可显示")
            return
        
        print("\n" + "=" * 80)
        print("📊 综合防护测试报告")
        print("=" * 80)
        
        # 测试配置
        print("\n🎯 测试配置:")
        config = self.test_results["测试配置"]
        for key, value in config.items():
            print(f"  {key}: {value}")
        
        # 压力测试结果
        if "压力测试结果" in self.test_results:
            print("\n🚀 压力测试结果:")
            stress_results = self.test_results["压力测试结果"]
            for category, data in stress_results.items():
                if isinstance(data, dict):
                    print(f"\n  {category}:")
                    for key, value in data.items():
                        if isinstance(value, list):
                            print(f"    {key}:")
                            for item in value:
                                print(f"      • {item}")
                        else:
                            print(f"    {key}: {value}")
        
        # 系统监控结果
        if "系统监控结果" in self.test_results:
            print("\n🖥️  系统监控结果:")
            monitor_results = self.test_results["系统监控结果"]
            for category, data in monitor_results.items():
                if isinstance(data, dict):
                    print(f"\n  {category}:")
                    for key, value in data.items():
                        print(f"    {key}: {value}")
                else:
                    print(f"  {category}: {data}")
        
        # 综合分析
        if "综合分析" in self.test_results:
            print("\n🔍 综合分析:")
            analysis = self.test_results["综合分析"]
            for category, data in analysis.items():
                print(f"\n  {category}:")
                if isinstance(data, dict):
                    for key, value in data.items():
                        if isinstance(value, dict):
                            print(f"    {key}:")
                            for k, v in value.items():
                                print(f"      {k}: {v}")
                        else:
                            print(f"    {key}: {value}")
                elif isinstance(data, list):
                    for item in data:
                        print(f"    • {item}")
                else:
                    print(f"    {data}")
        
        print("\n" + "=" * 80)
    
    def save_comprehensive_report(self, filename=None):
        """保存综合测试报告"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"comprehensive_test_report_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, ensure_ascii=False, indent=2)
        
        print(f"📄 综合测试报告已保存到: {filename}")
    
    def generate_comprehensive_charts(self, save_path=None):
        """生成综合测试图表"""
        if not save_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_path = f"comprehensive_test_{timestamp}"
        
        # 生成系统监控图表
        self.system_monitor.generate_charts(f"{save_path}_system")
        
        # 如果有压力测试的时间序列数据，生成压力测试图表
        if hasattr(self.stress_tester, 'results') and self.stress_tester.results:
            self._generate_stress_timeline_chart(f"{save_path}_stress")
    
    def _generate_stress_timeline_chart(self, save_path):
        """生成压力测试时间线图表"""
        if not self.stress_tester.results:
            return
        
        # 准备数据
        timestamps = [r.get('timestamp', 0) for r in self.stress_tester.results]
        response_times = [r.get('response_time', 0) for r in self.stress_tester.results]
        success_flags = [1 if r.get('success', False) else 0 for r in self.stress_tester.results]
        
        if not timestamps:
            return
        
        # 转换为相对时间
        start_time = min(timestamps)
        relative_times = [(t - start_time) for t in timestamps]
        
        # 创建图表
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        fig.suptitle('压力测试时间线分析', fontsize=16)
        
        # 响应时间时间线
        ax1.scatter(relative_times, response_times, alpha=0.6, s=1)
        ax1.set_title('响应时间时间线')
        ax1.set_xlabel('时间 (秒)')
        ax1.set_ylabel('响应时间 (毫秒)')
        ax1.grid(True, alpha=0.3)
        
        # 成功率时间线（滑动窗口）
        window_size = max(1, len(success_flags) // 50)
        success_rate_timeline = []
        time_windows = []
        
        for i in range(0, len(success_flags), window_size):
            window = success_flags[i:i+window_size]
            if window:
                success_rate = sum(window) / len(window) * 100
                success_rate_timeline.append(success_rate)
                time_windows.append(relative_times[i])
        
        ax2.plot(time_windows, success_rate_timeline, marker='o', markersize=2)
        ax2.set_title('成功率时间线')
        ax2.set_xlabel('时间 (秒)')
        ax2.set_ylabel('成功率 (%)')
        ax2.set_ylim(0, 105)
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f'{save_path}.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        print(f"压力测试图表已保存到 {save_path}.png")

async def main():
    """主函数"""
    print("🎯 综合防护测试工具")
    print("同时进行网络压力测试和系统监控")
    print("-" * 50)
    
    # 获取用户输入
    target = input("🌐 目标URL (默认: http://127.0.0.1:5000): ").strip()
    if not target:
        target = "http://127.0.0.1:5000"
    
    concurrent = input("⚡ 并发数 (默认: 50): ").strip()
    concurrent = int(concurrent) if concurrent.isdigit() else 50
    
    total = input("📊 总请求数 (默认: 500): ").strip()
    total = int(total) if total.isdigit() else 500
    
    duration = input("🕐 监控时长(秒) (默认: 自动): ").strip()
    duration = int(duration) if duration.isdigit() else None
    
    # 确认测试
    print(f"\n⚠️  即将启动综合测试:")
    print(f"  目标: {target}")
    print(f"  压力测试: {concurrent} 并发 {total} 次请求")
    print(f"  系统监控: {duration if duration else '自动'} 秒")
    
    confirm = input("\n确认开始测试? (y/n): ").lower()
    if confirm != 'y':
        print("❌ 测试已取消")
        return
    
    # 执行综合测试
    tester = ComprehensiveProtectionTest(target)
    
    try:
        results = await tester.run_comprehensive_test(concurrent, total, duration)
        
        # 显示结果
        tester.print_comprehensive_results()
        
        # 保存报告
        if input("\n💾 是否保存综合报告? (y/n): ").lower() == 'y':
            tester.save_comprehensive_report()
        
        # 生成图表
        if input("📊 是否生成图表? (y/n): ").lower() == 'y':
            tester.generate_comprehensive_charts()
            
    except KeyboardInterrupt:
        print("\n\n⏹️  测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")

if __name__ == "__main__":
    # 设置中文字体支持
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
    plt.rcParams['axes.unicode_minus'] = False
    
    asyncio.run(main())