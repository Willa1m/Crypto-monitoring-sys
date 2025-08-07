import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import logging
import os
from crypto_db import CryptoDatabase
import json

# 配置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('crypto_analyzer.log'),
        logging.StreamHandler()
    ]
)

class CryptoAnalyzer:
    def __init__(self):
        self.db = CryptoDatabase()
        
        # 获取项目根目录路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        self.output_dir = os.path.join(project_root, "static", "charts")
        
        self.ensure_output_dir()
        
        # 配置matplotlib中文字体
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
        plt.rcParams['axes.unicode_minus'] = False
    
    def ensure_output_dir(self):
        """确保输出目录存在"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir, exist_ok=True)
            logging.info(f"创建输出目录: {self.output_dir}")
    
    def get_price_data(self, timeframe, symbol=None, limit=100):
        """从数据库获取价格数据"""
        if not self.db.connect():
            return pd.DataFrame()
        
        try:
            data = self.db.get_historical_data(timeframe, symbol, limit)
            if not data:
                return pd.DataFrame()
            
            # 转换为DataFrame
            columns = ['symbol', 'date', 'open_price', 'high_price', 'low_price', 'close_price', 'volume']
            df = pd.DataFrame(data, columns=columns)
            
            # 转换数据类型
            df['date'] = pd.to_datetime(df['date'])
            for col in ['open_price', 'high_price', 'low_price', 'close_price', 'volume']:
                df[col] = pd.to_numeric(df[col])
            
            # 按日期排序
            df = df.sort_values('date')
            
            return df
            
        finally:
            self.db.disconnect()
    
    def get_latest_prices(self):
        """获取最新价格数据"""
        if not self.db.connect():
            return []
        
        try:
            data = self.db.get_latest_prices()
            return data if data else []
        finally:
            self.db.disconnect()
    
    def create_price_chart(self, timeframe, symbols=['BTC', 'ETH'], limit=100):
        """创建价格图表"""
        plt.figure(figsize=(12, 8))
        
        colors = {'BTC': '#f7931a', 'ETH': '#627eea'}
        has_data = False
        
        for symbol in symbols:
            df = self.get_price_data(timeframe, symbol, limit)
            if not df.empty:
                plt.plot(df['date'], df['close_price'], 
                        label=f'{symbol}', 
                        color=colors.get(symbol, 'blue'),
                        linewidth=2)
                has_data = True
        
        plt.title(f'加密货币价格走势 ({timeframe}级)', fontsize=16, fontweight='bold')
        plt.xlabel('时间', fontsize=12)
        plt.ylabel('价格 (USD)', fontsize=12)
        
        # 只有在有数据时才显示图例
        if has_data:
            plt.legend(fontsize=12)
        else:
            plt.text(0.5, 0.5, '暂无数据', ha='center', va='center', 
                    transform=plt.gca().transAxes, fontsize=14)
        
        plt.grid(True, alpha=0.3)
        
        # 格式化x轴
        if has_data:
            if timeframe == 'minute':
                plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
                plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=1))
            elif timeframe == 'hour':
                plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
                plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=6))
            else:  # day
                plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
                plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=1))
            
            plt.xticks(rotation=45)
        
        plt.tight_layout()
        
        # 保存图表
        filename = f"price_chart_{timeframe}.png"
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        logging.info(f"价格图表已保存: {filepath}")
        return filename
    
    def create_comparison_chart(self, symbols=['BTC', 'ETH'], timeframe='hour', limit=24):
        """创建对比图表"""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        colors = {'BTC': '#f7931a', 'ETH': '#627eea'}
        has_price_data = False
        has_volume_data = False
        
        # 价格对比
        for symbol in symbols:
            df = self.get_price_data(timeframe, symbol, limit)
            if not df.empty:
                ax1.plot(df['date'], df['close_price'], 
                        label=f'{symbol} 价格', 
                        color=colors.get(symbol, 'blue'),
                        linewidth=2)
                has_price_data = True
        
        ax1.set_title('价格对比', fontsize=14, fontweight='bold')
        ax1.set_ylabel('价格 (USD)', fontsize=12)
        if has_price_data:
            ax1.legend(fontsize=10)
        else:
            ax1.text(0.5, 0.5, '暂无价格数据', ha='center', va='center', 
                    transform=ax1.transAxes, fontsize=12)
        ax1.grid(True, alpha=0.3)
        
        # 成交量对比
        for symbol in symbols:
            df = self.get_price_data(timeframe, symbol, limit)
            if not df.empty:
                ax2.bar(df['date'], df['volume'], 
                       label=f'{symbol} 成交量', 
                       color=colors.get(symbol, 'blue'),
                       alpha=0.7)
                has_volume_data = True
        
        ax2.set_title('成交量对比', fontsize=14, fontweight='bold')
        ax2.set_xlabel('时间', fontsize=12)
        ax2.set_ylabel('成交量', fontsize=12)
        if has_volume_data:
            ax2.legend(fontsize=10)
        else:
            ax2.text(0.5, 0.5, '暂无成交量数据', ha='center', va='center', 
                    transform=ax2.transAxes, fontsize=12)
        ax2.grid(True, alpha=0.3)
        
        # 格式化x轴
        if has_price_data or has_volume_data:
            for ax in [ax1, ax2]:
                if timeframe == 'minute':
                    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
                    ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
                elif timeframe == 'hour':
                    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
                    ax.xaxis.set_major_locator(mdates.HourLocator(interval=6))
                else:  # day
                    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
                    ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
                
                ax.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        
        # 保存图表
        filename = f"comparison_chart_{timeframe}.png"
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        logging.info(f"对比图表已保存: {filepath}")
        return filename
    
    def calculate_statistics(self, timeframe, symbol, limit=100):
        """计算统计数据"""
        df = self.get_price_data(timeframe, symbol, limit)
        if df.empty:
            return None
        
        stats = {
            'symbol': symbol,
            'timeframe': timeframe,
            'current_price': float(df['close_price'].iloc[-1]),
            'highest_price': float(df['high_price'].max()),
            'lowest_price': float(df['low_price'].min()),
            'average_price': float(df['close_price'].mean()),
            'price_change': float(df['close_price'].iloc[-1] - df['close_price'].iloc[0]),
            'price_change_percent': float((df['close_price'].iloc[-1] / df['close_price'].iloc[0] - 1) * 100),
            'volatility': float(df['close_price'].std()),
            'total_volume': float(df['volume'].sum()),
            'data_points': len(df)
        }
        
        return stats
    
    def generate_analysis_report(self):
        """生成分析报告"""
        report = {
            'generated_at': datetime.now().isoformat(),
            'latest_prices': [],
            'statistics': {},
            'charts': {}
        }
        
        # 获取最新价格
        latest_prices = self.get_latest_prices()
        for price_data in latest_prices:
            name, symbol, price, change_24h, timestamp = price_data
            report['latest_prices'].append({
                'name': name,
                'symbol': symbol,
                'price': float(price),
                'change_24h': float(change_24h),
                'timestamp': timestamp.isoformat() if hasattr(timestamp, 'isoformat') else str(timestamp)
            })
        
        # 生成统计数据和图表
        symbols = ['BTC', 'ETH']
        timeframes = ['minute', 'hour', 'day']
        
        for timeframe in timeframes:
            # 创建图表
            price_chart = self.create_price_chart(timeframe, symbols)
            comparison_chart = self.create_comparison_chart(symbols, timeframe)
            
            report['charts'][timeframe] = {
                'price_chart': price_chart,
                'comparison_chart': comparison_chart
            }
            
            # 计算统计数据
            report['statistics'][timeframe] = {}
            for symbol in symbols:
                stats = self.calculate_statistics(timeframe, symbol)
                if stats:
                    report['statistics'][timeframe][symbol] = stats
        
        # 保存报告
        report_file = os.path.join(self.output_dir, 'analysis_report.json')
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        logging.info(f"分析报告已保存: {report_file}")
        return report

def run_analysis():
    """运行分析程序"""
    logging.info("开始加密货币数据分析")
    
    analyzer = CryptoAnalyzer()
    report = analyzer.generate_analysis_report()
    
    if report:
        logging.info("=== 分析报告摘要 ===")
        
        # 显示最新价格
        if report['latest_prices']:
            logging.info("最新价格:")
            for price_info in report['latest_prices']:
                logging.info(f"  {price_info['name']}: ${price_info['price']:,.2f} "
                           f"(24h: {price_info['change_24h']:+.2f}%)")
        
        # 显示统计摘要
        for timeframe in ['minute', 'hour', 'day']:
            if timeframe in report['statistics']:
                logging.info(f"\n{timeframe}级数据统计:")
                for symbol, stats in report['statistics'][timeframe].items():
                    logging.info(f"  {symbol}: 当前${stats['current_price']:,.2f}, "
                               f"变化{stats['price_change_percent']:+.2f}%, "
                               f"数据点{stats['data_points']}个")
        
        logging.info("数据分析完成")
        return True
    else:
        logging.error("数据分析失败")
        return False

if __name__ == "__main__":
    run_analysis()