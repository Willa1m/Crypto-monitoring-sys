from flask import Flask, jsonify, request
import pandas as pd
import numpy as np
import json
import os
import glob
import logging
from datetime import datetime, timedelta

class KlineBackend:
    """K线数据后端处理类"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def generate_sample_data(self, days=100):
        """生成示例K线数据"""
        date_rng = pd.date_range(start='2023-01-01', periods=days, freq='D')
        data = []
        base_price = 100
        
        for i, dt in enumerate(date_rng):
            # 模拟价格波动
            change = np.random.normal(0, 2)  # 正态分布的价格变化
            base_price = max(base_price + change, 10)  # 确保价格不为负
            
            open_p = base_price + np.random.uniform(-1, 1)
            high_p = open_p + np.random.uniform(0, 5)
            low_p = open_p - np.random.uniform(0, 5)
            close_p = np.random.uniform(low_p, high_p)
            vol = np.random.uniform(100, 1000)
            
            data.append([
                int(dt.timestamp() * 1000),  # 时间戳（毫秒）
                round(open_p, 2),   # 开盘价
                round(high_p, 2),   # 最高价
                round(low_p, 2),    # 最低价
                round(close_p, 2),  # 收盘价
                round(vol, 2)       # 成交量
            ])
            base_price = close_p  # 下一根K线的基准价格
        
        return data
    
    def calculate_ma(self, data, period):
        """计算移动平均线"""
        close_prices = [d[4] for d in data]
        ma_values = []
        
        for i in range(len(close_prices)):
            if i < period - 1:
                ma_values.append(None)
            else:
                ma = sum(close_prices[i-period+1:i+1]) / period
                ma_values.append(round(ma, 2))
        
        return ma_values
    
    def calculate_rsi(self, data, period=14):
        """计算RSI相对强弱指数"""
        close_prices = np.array([d[4] for d in data])
        deltas = np.diff(close_prices)
        
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        rsi_values = [None] * period  # 前period个值为None
        
        # 计算初始平均收益和损失
        avg_gain = np.mean(gains[:period])
        avg_loss = np.mean(losses[:period])
        
        if avg_loss == 0:
            rsi_values.append(100)
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            rsi_values.append(round(rsi, 2))
        
        # 计算后续RSI值
        for i in range(period + 1, len(close_prices)):
            avg_gain = (avg_gain * (period - 1) + gains[i-1]) / period
            avg_loss = (avg_loss * (period - 1) + losses[i-1]) / period
            
            if avg_loss == 0:
                rsi_values.append(100)
            else:
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))
                rsi_values.append(round(rsi, 2))
        
        return rsi_values
    
    def calculate_macd(self, data, short_period=12, long_period=26, signal_period=9):
        """计算MACD指标"""
        close_prices = pd.Series([d[4] for d in data])
        
        # 计算EMA
        ema_short = close_prices.ewm(span=short_period, adjust=False).mean()
        ema_long = close_prices.ewm(span=long_period, adjust=False).mean()
        
        # MACD线
        macd_line = ema_short - ema_long
        
        # 信号线
        signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
        
        # MACD柱状图
        macd_hist = macd_line - signal_line
        
        return (
            [round(x, 4) for x in macd_line.tolist()],
            [round(x, 4) for x in signal_line.tolist()],
            [round(x, 4) for x in macd_hist.tolist()]
        )
    
    def calculate_bollinger_bands(self, data, period=20, std_dev=2):
        """计算布林带"""
        close_prices = pd.Series([d[4] for d in data])
        
        # 中轨（移动平均线）
        middle = close_prices.rolling(window=period).mean()
        
        # 标准差
        std = close_prices.rolling(window=period).std()
        
        # 上轨和下轨
        upper = middle + (std * std_dev)
        lower = middle - (std * std_dev)
        
        return {
            'upper': [round(x, 2) if not pd.isna(x) else None for x in upper.tolist()],
            'middle': [round(x, 2) if not pd.isna(x) else None for x in middle.tolist()],
            'lower': [round(x, 2) if not pd.isna(x) else None for x in lower.tolist()]
        }
    
    def calculate_kdj(self, data, period=9, k_period=3, d_period=3):
        """计算KDJ指标"""
        high_prices = [d[2] for d in data]
        low_prices = [d[3] for d in data]
        close_prices = [d[4] for d in data]
        
        k_values = []
        d_values = []
        j_values = []
        
        for i in range(len(data)):
            if i < period - 1:
                k_values.append(None)
                d_values.append(None)
                j_values.append(None)
            else:
                # 计算RSV
                period_high = max(high_prices[i-period+1:i+1])
                period_low = min(low_prices[i-period+1:i+1])
                
                if period_high == period_low:
                    rsv = 50
                else:
                    rsv = (close_prices[i] - period_low) / (period_high - period_low) * 100
                
                # 计算K值
                if i == period - 1:
                    k = rsv
                else:
                    k = (k_values[i-1] * (k_period - 1) + rsv) / k_period if k_values[i-1] is not None else rsv
                
                k_values.append(round(k, 2))
                
                # 计算D值
                if i == period - 1:
                    d = k
                else:
                    d = (d_values[i-1] * (d_period - 1) + k) / d_period if d_values[i-1] is not None else k
                
                d_values.append(round(d, 2))
                
                # 计算J值
                j = 3 * k - 2 * d
                j_values.append(round(j, 2))
        
        return {'k': k_values, 'd': d_values, 'j': j_values}
    
    def calculate_volatility(self, data, period=20):
        """计算波动率"""
        close_prices = pd.Series([d[4] for d in data])
        returns = close_prices.pct_change()
        volatility = returns.rolling(window=period).std() * np.sqrt(252) * 100  # 年化波动率
        
        return [round(x, 2) if not pd.isna(x) else None for x in volatility.tolist()]
    
    def get_kline_data_with_indicators(self, symbol='BTC', timeframe='hour', limit=100):
        """获取K线数据和技术指标"""
        try:
            # 尝试从文件读取数据
            pattern = f"kline_data/{symbol.upper()}_{timeframe}_kline_*.json"
            matching_files = glob.glob(pattern)
            
            if matching_files:
                # 使用最新的文件
                latest_file = sorted(matching_files)[-1]
                with open(latest_file, 'r', encoding='utf-8') as f:
                    file_data = json.load(f)
                
                # 转换为标准格式
                kline_data = []
                for item in file_data.get('kline_data', []):
                    if isinstance(item, dict):
                        # 如果是字典格式，转换为数组格式
                        timestamp = int(pd.to_datetime(item['date']).timestamp() * 1000)
                        kline_data.append([
                            timestamp,
                            item['open'],
                            item['high'],
                            item['low'],
                            item['close'],
                            item.get('volume', 0)
                        ])
                    else:
                        # 如果已经是数组格式，直接使用
                        kline_data.append(item)
            else:
                # 如果没有文件，生成示例数据
                self.logger.warning(f"未找到{symbol}的{timeframe}数据文件，使用示例数据")
                kline_data = self.generate_sample_data(limit)
            
            # 限制数据量
            if len(kline_data) > limit:
                kline_data = kline_data[-limit:]
            
            # 计算技术指标
            ma5 = self.calculate_ma(kline_data, 5)
            ma10 = self.calculate_ma(kline_data, 10)
            ma20 = self.calculate_ma(kline_data, 20)
            rsi = self.calculate_rsi(kline_data)
            macd_line, signal_line, macd_hist = self.calculate_macd(kline_data)
            bollinger = self.calculate_bollinger_bands(kline_data)
            volatility = self.calculate_volatility(kline_data)
            kdj = self.calculate_kdj(kline_data)
            
            return {
                'kline': kline_data,
                'indicators': {
                    'ma5': ma5,
                    'ma10': ma10,
                    'ma20': ma20,
                    'rsi': rsi,
                    'macd_line': macd_line,
                    'signal_line': signal_line,
                    'macd_hist': macd_hist,
                    'bollinger': bollinger,
                    'volatility': volatility,
                    'kdj': kdj
                }
            }
            
        except Exception as e:
            self.logger.error(f"获取K线数据时出错: {str(e)}")
            # 返回示例数据
            kline_data = self.generate_sample_data(limit)
            ma5 = self.calculate_ma(kline_data, 5)
            ma10 = self.calculate_ma(kline_data, 10)
            ma20 = self.calculate_ma(kline_data, 20)
            rsi = self.calculate_rsi(kline_data)
            macd_line, signal_line, macd_hist = self.calculate_macd(kline_data)
            bollinger = self.calculate_bollinger_bands(kline_data)
            volatility = self.calculate_volatility(kline_data)
            kdj = self.calculate_kdj(kline_data)
            
            return {
                'kline': kline_data,
                'indicators': {
                    'ma5': ma5,
                    'ma10': ma10,
                    'ma20': ma20,
                    'rsi': rsi,
                    'macd_line': macd_line,
                    'signal_line': signal_line,
                    'macd_hist': macd_hist,
                    'bollinger': bollinger,
                    'volatility': volatility,
                    'kdj': kdj
                }
            }

# 创建全局实例
kline_backend = KlineBackend()