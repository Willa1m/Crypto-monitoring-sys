import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import os
import json
from crypto_db import CryptoDatabase

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('kline_processor.log'),
        logging.StreamHandler()
    ]
)

class KlineProcessor:
    """K线数据处理器"""
    
    def __init__(self):
        self.db = CryptoDatabase()
        
        # 获取项目根目录路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        self.output_dir = os.path.join(project_root, "data", "kline_data")
        
        self.ensure_output_dir()
    
    def ensure_output_dir(self):
        """确保输出目录存在"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            logging.info(f"创建K线数据输出目录: {self.output_dir}")
    
    def get_kline_data(self, symbol, timeframe, limit=100):
        """获取K线数据"""
        if not self.db.connect():
            logging.error("数据库连接失败")
            return []
        
        try:
            # 从数据库获取历史数据
            data = self.db.get_historical_data(timeframe, symbol, limit)
            if not data:
                logging.warning(f"没有找到 {symbol} 的 {timeframe} 级数据")
                return []
            
            # 转换为K线格式
            kline_data = []
            for item in data:
                symbol_db, date, open_price, high_price, low_price, close_price, volume = item
                kline_data.append({
                    'symbol': symbol_db,
                    'date': date.isoformat() if hasattr(date, 'isoformat') else str(date),
                    'open': float(open_price),
                    'high': float(high_price),
                    'low': float(low_price),
                    'close': float(close_price),
                    'volume': float(volume)
                })
            
            # 按时间排序
            kline_data.sort(key=lambda x: x['date'])
            
            logging.info(f"成功获取 {symbol} 的 {timeframe} 级K线数据，共 {len(kline_data)} 条")
            return kline_data
            
        except Exception as e:
            logging.error(f"获取K线数据时出错: {str(e)}")
            return []
        finally:
            self.db.disconnect()
    
    def calculate_technical_indicators(self, kline_data):
        """计算技术指标"""
        if not kline_data or len(kline_data) < 20:
            return {}
        
        # 提取收盘价
        closes = [item['close'] for item in kline_data]
        highs = [item['high'] for item in kline_data]
        lows = [item['low'] for item in kline_data]
        volumes = [item['volume'] for item in kline_data]
        
        indicators = {}
        
        try:
            # 移动平均线
            indicators['ma5'] = self.calculate_ma(closes, 5)
            indicators['ma10'] = self.calculate_ma(closes, 10)
            indicators['ma20'] = self.calculate_ma(closes, 20)
            indicators['ma50'] = self.calculate_ma(closes, 50)
            
            # RSI
            indicators['rsi'] = self.calculate_rsi(closes, 14)
            
            # MACD
            macd_data = self.calculate_macd(closes)
            indicators.update(macd_data)
            
            # 布林带
            bollinger_data = self.calculate_bollinger_bands(closes, 20, 2)
            indicators.update(bollinger_data)
            
            # 成交量指标
            indicators['volume_ma'] = self.calculate_ma(volumes, 20)
            
            # 波动率
            indicators['volatility'] = self.calculate_volatility(closes, 20)
            
            # KDJ指标
            kdj_data = self.calculate_kdj(highs, lows, closes, 9, 3, 3)
            indicators.update(kdj_data)
            
            logging.info("技术指标计算完成")
            
        except Exception as e:
            logging.error(f"计算技术指标时出错: {str(e)}")
        
        return indicators
    
    def calculate_ma(self, data, period):
        """计算移动平均线"""
        if len(data) < period:
            return None
        
        ma_values = []
        for i in range(len(data)):
            if i < period - 1:
                ma_values.append(None)
            else:
                ma = sum(data[i-period+1:i+1]) / period
                ma_values.append(ma)
        
        return ma_values
    
    def calculate_rsi(self, data, period=14):
        """计算RSI指标"""
        if len(data) < period + 1:
            return None
        
        deltas = [data[i] - data[i-1] for i in range(1, len(data))]
        gains = [delta if delta > 0 else 0 for delta in deltas]
        losses = [-delta if delta < 0 else 0 for delta in deltas]
        
        rsi_values = [None] * period
        
        # 计算初始RSI
        avg_gain = sum(gains[:period]) / period
        avg_loss = sum(losses[:period]) / period
        
        if avg_loss == 0:
            rsi_values.append(100)
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            rsi_values.append(rsi)
        
        # 计算后续RSI
        for i in range(period + 1, len(data)):
            avg_gain = (avg_gain * (period - 1) + gains[i-1]) / period
            avg_loss = (avg_loss * (period - 1) + losses[i-1]) / period
            
            if avg_loss == 0:
                rsi_values.append(100)
            else:
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))
                rsi_values.append(rsi)
        
        return rsi_values
    
    def calculate_macd(self, data, fast=12, slow=26, signal=9):
        """计算MACD指标"""
        if len(data) < slow:
            return {'macd': None, 'signal': None, 'histogram': None}
        
        # 计算EMA
        ema_fast = self.calculate_ema(data, fast)
        ema_slow = self.calculate_ema(data, slow)
        
        # 计算MACD线
        macd_line = []
        for i in range(len(data)):
            if ema_fast[i] is not None and ema_slow[i] is not None:
                macd_line.append(ema_fast[i] - ema_slow[i])
            else:
                macd_line.append(None)
        
        # 计算信号线
        signal_line = self.calculate_ema([x for x in macd_line if x is not None], signal)
        
        # 补齐信号线长度
        signal_full = [None] * (len(macd_line) - len(signal_line)) + signal_line
        
        # 计算柱状图
        histogram = []
        for i in range(len(macd_line)):
            if macd_line[i] is not None and signal_full[i] is not None:
                histogram.append(macd_line[i] - signal_full[i])
            else:
                histogram.append(None)
        
        return {
            'macd': macd_line,
            'signal': signal_full,
            'histogram': histogram
        }
    
    def calculate_ema(self, data, period):
        """计算指数移动平均线"""
        if len(data) < period:
            return [None] * len(data)
        
        multiplier = 2 / (period + 1)
        ema_values = [None] * (period - 1)
        
        # 初始EMA使用SMA
        sma = sum(data[:period]) / period
        ema_values.append(sma)
        
        # 计算后续EMA
        for i in range(period, len(data)):
            ema = (data[i] * multiplier) + (ema_values[-1] * (1 - multiplier))
            ema_values.append(ema)
        
        return ema_values
    
    def calculate_bollinger_bands(self, data, period=20, std_dev=2):
        """计算布林带"""
        if len(data) < period:
            return {'bb_upper': None, 'bb_middle': None, 'bb_lower': None}
        
        ma_values = self.calculate_ma(data, period)
        
        bb_upper = []
        bb_lower = []
        
        for i in range(len(data)):
            if i < period - 1:
                bb_upper.append(None)
                bb_lower.append(None)
            else:
                # 计算标准差
                window_data = data[i-period+1:i+1]
                std = np.std(window_data)
                
                bb_upper.append(ma_values[i] + (std * std_dev))
                bb_lower.append(ma_values[i] - (std * std_dev))
        
        return {
            'bb_upper': bb_upper,
            'bb_middle': ma_values,
            'bb_lower': bb_lower
        }
    
    def calculate_volatility(self, data, period=20):
        """计算波动率"""
        if len(data) < period:
            return None
        
        volatility_values = []
        
        for i in range(len(data)):
            if i < period - 1:
                volatility_values.append(None)
            else:
                window_data = data[i-period+1:i+1]
                returns = [(window_data[j] - window_data[j-1]) / window_data[j-1] 
                          for j in range(1, len(window_data))]
                volatility = np.std(returns) * np.sqrt(252)  # 年化波动率
                volatility_values.append(volatility)
        
        return volatility_values
    
    def calculate_kdj(self, highs, lows, closes, k_period=9, k_smooth=3, d_smooth=3):
        """计算KDJ指标"""
        if len(closes) < k_period:
            return {'k': None, 'd': None, 'j': None}
        
        rsv_values = []
        
        # 计算RSV
        for i in range(len(closes)):
            if i < k_period - 1:
                rsv_values.append(None)
            else:
                window_highs = highs[i-k_period+1:i+1]
                window_lows = lows[i-k_period+1:i+1]
                
                highest = max(window_highs)
                lowest = min(window_lows)
                
                if highest == lowest:
                    rsv = 50
                else:
                    rsv = (closes[i] - lowest) / (highest - lowest) * 100
                
                rsv_values.append(rsv)
        
        # 计算K值
        k_values = [None] * (k_period - 1)
        k_values.append(50)  # 初始K值
        
        for i in range(k_period, len(rsv_values)):
            if rsv_values[i] is not None:
                k = (k_values[-1] * (k_smooth - 1) + rsv_values[i]) / k_smooth
                k_values.append(k)
            else:
                k_values.append(None)
        
        # 计算D值
        d_values = [None] * (k_period - 1)
        d_values.append(50)  # 初始D值
        
        for i in range(k_period, len(k_values)):
            if k_values[i] is not None:
                d = (d_values[-1] * (d_smooth - 1) + k_values[i]) / d_smooth
                d_values.append(d)
            else:
                d_values.append(None)
        
        # 计算J值
        j_values = []
        for i in range(len(k_values)):
            if k_values[i] is not None and d_values[i] is not None:
                j = 3 * k_values[i] - 2 * d_values[i]
                j_values.append(j)
            else:
                j_values.append(None)
        
        return {
            'k': k_values,
            'd': d_values,
            'j': j_values
        }
    
    def save_kline_data(self, symbol, timeframe, kline_data, indicators=None):
        """保存K线数据到文件"""
        try:
            # 创建文件名
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{symbol}_{timeframe}_kline_{timestamp}.json"
            filepath = os.path.join(self.output_dir, filename)
            
            # 准备保存的数据
            save_data = {
                'symbol': symbol,
                'timeframe': timeframe,
                'timestamp': timestamp,
                'data_count': len(kline_data),
                'kline_data': kline_data,
                'technical_indicators': indicators or {}
            }
            
            # 保存到JSON文件
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            
            logging.info(f"K线数据已保存到: {filepath}")
            return filepath
            
        except Exception as e:
            logging.error(f"保存K线数据时出错: {str(e)}")
            return None
    
    def process_and_save_kline(self, symbol, timeframe, limit=100):
        """处理并保存K线数据"""
        logging.info(f"开始处理 {symbol} 的 {timeframe} 级K线数据")
        
        # 获取K线数据
        kline_data = self.get_kline_data(symbol, timeframe, limit)
        if not kline_data:
            logging.warning(f"没有获取到 {symbol} 的K线数据")
            return None
        
        # 计算技术指标
        indicators = self.calculate_technical_indicators(kline_data)
        
        # 保存数据
        filepath = self.save_kline_data(symbol, timeframe, kline_data, indicators)
        
        return {
            'symbol': symbol,
            'timeframe': timeframe,
            'data_count': len(kline_data),
            'filepath': filepath,
            'kline_data': kline_data,
            'indicators': indicators
        }

def run_kline_processing():
    """运行K线数据处理"""
    processor = KlineProcessor()
    
    symbols = ['BTC', 'ETH']
    timeframes = ['minute', 'hour', 'day']
    
    results = []
    
    for symbol in symbols:
        for timeframe in timeframes:
            try:
                result = processor.process_and_save_kline(symbol, timeframe, 100)
                if result:
                    results.append(result)
                    logging.info(f"成功处理 {symbol} {timeframe} 级K线数据")
                else:
                    logging.warning(f"处理 {symbol} {timeframe} 级K线数据失败")
            except Exception as e:
                logging.error(f"处理 {symbol} {timeframe} 级K线数据时出错: {str(e)}")
    
    logging.info(f"K线数据处理完成，共处理 {len(results)} 个数据集")
    return results

if __name__ == "__main__":
    logging.info("启动K线数据处理程序")
    results = run_kline_processing()
    logging.info("K线数据处理程序执行完成")