import requests
import pandas as pd
import time
import logging
from datetime import datetime
import os
import random

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('crypto_scraper.log'),
        logging.StreamHandler()
    ]
)

# 定义headers
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
}

# 重试参数
MAX_RETRIES = 3
RETRY_DELAY = 5  # 秒

# 速率限制配置
RATELIMIT_RETRY_MAX = 3
RATELIMIT_RETRY_DELAY = 2

# 加密货币列表
CRYPTOCURRENCIES = {
    "Bitcoin": "BTC",
    "Ethereum": "ETH"
}

# API配置
API_KEY = '6c2b58bddb3f3034bf717c67253b0e23cfe7472e35dd060edcbda20d169996d6'
COINDESK_API_BASE_URL = "https://data-api.coindesk.com/index/cc/v1"
COINDESK_API_ENDPOINTS = {
    'current': '/latest/tick',
    'day': '/historical/days',
    'hour': '/historical/hours',
    'minute': '/historical/minutes'
}

# API请求参数
COINDESK_API_PARAMS = {
    'market': 'cadli',
    'apply_mapping': 'true',
    'response_format': 'JSON',
    'limit': '100',  # 增加数据量
    'aggregate': '1',
    'fill': 'true'
}

def handle_ratelimit(response, retry_count=0):
    """处理API速率限制"""
    if response.status_code == 429:  # Too Many Requests
        if retry_count >= RATELIMIT_RETRY_MAX:
            logging.error(f"达到最大重试次数 ({RATELIMIT_RETRY_MAX})，放弃请求")
            return False
        
        wait_time = RATELIMIT_RETRY_DELAY * (2 ** retry_count)
        logging.warning(f"触发速率限制，等待{wait_time}秒后重试")
        time.sleep(wait_time)
        return True
    return False

def get_crypto_price_coindesk(symbol, name):
    """获取加密货币的当前价格数据"""
    retry_count = 0
    
    while retry_count < MAX_RETRIES:
        try:
            url = f"{COINDESK_API_BASE_URL}{COINDESK_API_ENDPOINTS['current']}"
            
            params = {
                'market': COINDESK_API_PARAMS['market'],
                'instruments': f"{symbol}-USD",
                'apply_mapping': COINDESK_API_PARAMS['apply_mapping']
            }
            
            logging.info(f"正在请求 {name} ({symbol}) 价格")
            time.sleep(random.uniform(0.5, 1))
            
            headers_with_auth = headers.copy()
            headers_with_auth['Authorization'] = f'Bearer {API_KEY}'
            
            response = requests.get(url, params=params, headers=headers_with_auth, timeout=10)
            
            if handle_ratelimit(response, retry_count):
                retry_count += 1
                continue
            
            response.raise_for_status()
            data = response.json()
            logging.debug(f"API响应数据: {data}")
            
            if not data or 'Data' not in data:
                logging.warning(f"API响应格式不符合预期: {data}")
                return None
            
            instrument_key = f"{symbol}-USD"
            if instrument_key not in data['Data']:
                logging.warning(f"未找到{symbol}的价格数据")
                return None
            
            latest_data = data['Data'][instrument_key]
            
            result = {
                'symbol': symbol,
                'name': name,
                'price': float(latest_data['VALUE']),
                'change_24h': float(latest_data['CURRENT_DAY_CHANGE_PERCENTAGE']),
                'timestamp': datetime.fromtimestamp(latest_data['VALUE_LAST_UPDATE_TS'])
            }
            
            logging.info(f"{name} ({symbol}) 当前价格: ${result['price']:,.2f}")
            return result
                
        except Exception as e:
            retry_count += 1
            wait_time = RETRY_DELAY * (2 ** retry_count)
            logging.error(f"请求异常: {str(e)}，等待 {wait_time} 秒后重试...")
            time.sleep(wait_time)
    
    logging.error(f"达到最大重试次数 ({MAX_RETRIES})，放弃获取 {name} ({symbol}) 价格")
    return None

def get_historical_data_coindesk(symbol, timeframe="day"):
    """获取加密货币的历史价格数据"""
    retry_count = 0
    
    while retry_count < MAX_RETRIES:
        try:
            if timeframe not in COINDESK_API_ENDPOINTS:
                logging.warning(f"不支持的时间范围: {timeframe}")
                return pd.DataFrame()
            
            url = f"{COINDESK_API_BASE_URL}{COINDESK_API_ENDPOINTS[timeframe]}"
            
            params = {
                'market': COINDESK_API_PARAMS['market'],
                'instrument': f"{symbol}-USD",
                'limit': COINDESK_API_PARAMS['limit'],
                'aggregate': COINDESK_API_PARAMS['aggregate'],
                'fill': COINDESK_API_PARAMS['fill'],
                'apply_mapping': COINDESK_API_PARAMS['apply_mapping'],
                'response_format': COINDESK_API_PARAMS['response_format']
            }
            
            logging.info(f"正在请求 {symbol} 历史数据，时间范围: {timeframe}")
            
            delay = {
                'minute': (0.5, 1),
                'hour': (1, 2),
                'day': (2, 3)
            }[timeframe]
            time.sleep(random.uniform(*delay))
            
            headers_with_auth = headers.copy()
            headers_with_auth['Authorization'] = f'Bearer {API_KEY}'
            
            response = requests.get(url, params=params, headers=headers_with_auth, timeout=10)
            
            if handle_ratelimit(response, retry_count):
                retry_count += 1
                continue
                
            response.raise_for_status()
            data = response.json()
            
            if not data or 'Data' not in data or not isinstance(data['Data'], list):
                logging.warning(f"历史数据API响应格式不符合预期")
                return pd.DataFrame()
            
            historical_data = []
            for entry in data['Data']:
                if entry.get('INSTRUMENT') != f"{symbol}-USD":
                    continue
                historical_data.append({
                    'symbol': symbol,
                    'date': datetime.fromtimestamp(entry['TIMESTAMP']),
                    'open': float(entry['OPEN']),
                    'high': float(entry['HIGH']),
                    'low': float(entry['LOW']),
                    'close': float(entry['CLOSE']),
                    'volume': float(entry.get('VOLUME', 0)),
                    'quote_volume': float(entry.get('QUOTE_VOLUME', 0)),
                    'timeframe': entry.get('UNIT', timeframe).lower()
                })
            
            df = pd.DataFrame(historical_data)
            logging.info(f"成功获取 {symbol} 历史数据，时间范围: {timeframe}，记录数: {len(df)}")
            return df
                
        except Exception as e:
            retry_count += 1
            wait_time = RETRY_DELAY * (2 ** retry_count)
            logging.error(f"请求异常: {str(e)}，等待 {wait_time} 秒后重试...")
            time.sleep(wait_time)
    
    logging.error(f"达到最大重试次数 ({MAX_RETRIES})，放弃获取 {symbol} 历史数据")
    return pd.DataFrame()

def scrape_realtime_crypto_data():
    """专门抓取实时加密货币价格数据（与历史数据分离）"""
    realtime_data = []
    
    for name, symbol in CRYPTOCURRENCIES.items():
        logging.info(f"开始抓取 {name} ({symbol}) 实时价格数据")
        
        # 获取当前价格
        current_data = get_crypto_price_coindesk(symbol, name)
        if current_data:
            realtime_data.append(current_data)
        
        # 在不同货币之间添加短暂延迟
        time.sleep(random.uniform(0.5, 1))
    
    return realtime_data

def scrape_all_crypto_data():
    """抓取所有加密货币的当前价格和历史数据"""
    all_current_data = []
    all_historical_data = {
        'minute': [],
        'hour': [],
        'day': []
    }
    
    for name, symbol in CRYPTOCURRENCIES.items():
        logging.info(f"开始抓取 {name} ({symbol}) 数据")
        
        # 获取当前价格
        current_data = get_crypto_price_coindesk(symbol, name)
        if current_data:
            all_current_data.append(current_data)
        
        # 获取历史数据
        for timeframe in ['minute', 'hour', 'day']:
            historical_df = get_historical_data_coindesk(symbol, timeframe)
            if not historical_df.empty:
                all_historical_data[timeframe].append(historical_df)
            
            # 在不同时间范围之间添加延迟
            time.sleep(random.uniform(1, 2))
        
        # 在不同货币之间添加延迟
        time.sleep(random.uniform(2, 4))
    
    # 合并历史数据
    combined_historical_data = {}
    for timeframe in ['minute', 'hour', 'day']:
        if all_historical_data[timeframe]:
            combined_historical_data[timeframe] = pd.concat(
                all_historical_data[timeframe], 
                ignore_index=True
            )
        else:
            combined_historical_data[timeframe] = pd.DataFrame()
    
    return all_current_data, combined_historical_data

if __name__ == "__main__":
    logging.info("开始抓取加密货币数据")
    current_data, historical_data = scrape_all_crypto_data()
    
    logging.info(f"抓取完成，当前价格数据: {len(current_data)} 条")
    for timeframe, df in historical_data.items():
        logging.info(f"历史数据 ({timeframe}): {len(df)} 条")
    
    # 输出示例数据
    if current_data:
        logging.info("当前价格数据示例:")
        for data in current_data:
            logging.info(f"  {data['name']}: ${data['price']:,.2f}")