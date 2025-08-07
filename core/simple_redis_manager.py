#!/usr/bin/env python3
"""
简化版Redis缓存管理器
只使用基础Redis功能，不依赖集群库
"""

import json
import time
import hashlib
import os
from typing import Any, Optional, Dict
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleRedisManager:
    """简化版Redis缓存管理器"""
    
    def __init__(self, host='192.168.73.130', port=7001, db=0):
        """初始化Redis连接"""
        self.redis_client = None
        self.host = host
        self.port = port
        self.db = db
        self._connect()
    
    def _connect(self):
        """连接到Redis"""
        try:
            import redis
            self.redis_client = redis.Redis(
                host=self.host, 
                port=self.port, 
                db=self.db, 
                decode_responses=True,
                socket_timeout=5,
                socket_connect_timeout=5
            )
            # 测试连接
            self.redis_client.ping()
            logger.info(f"✅ Redis连接成功: {self.host}:{self.port}")
        except ImportError:
            logger.error("❌ Redis库未安装，请运行: sudo apt install python3-redis")
            self.redis_client = None
        except Exception as e:
            logger.error(f"❌ Redis连接失败: {e}")
            self.redis_client = None
    
    def is_connected(self) -> bool:
        """检查Redis连接状态"""
        if not self.redis_client:
            return False
        try:
            self.redis_client.ping()
            return True
        except:
            return False
    
    def set(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """设置缓存"""
        if not self.is_connected():
            return False
        
        try:
            # 序列化数据
            if isinstance(value, (dict, list)):
                serialized_value = json.dumps(value, ensure_ascii=False)
            else:
                serialized_value = str(value)
            
            # 设置缓存
            if expire:
                result = self.redis_client.setex(key, expire, serialized_value)
            else:
                result = self.redis_client.set(key, serialized_value)
            
            return bool(result)
        except Exception as e:
            logger.error(f"设置缓存失败 {key}: {e}")
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        if not self.is_connected():
            return None
        
        try:
            value = self.redis_client.get(key)
            if value is None:
                return None
            
            # 尝试反序列化JSON
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        except Exception as e:
            logger.error(f"获取缓存失败 {key}: {e}")
            return None
    
    def delete(self, *keys: str) -> int:
        """删除缓存"""
        if not self.is_connected():
            return 0
        
        try:
            return self.redis_client.delete(*keys)
        except Exception as e:
            logger.error(f"删除缓存失败: {e}")
            return 0
    
    def exists(self, key: str) -> bool:
        """检查键是否存在"""
        if not self.is_connected():
            return False
        
        try:
            return bool(self.redis_client.exists(key))
        except Exception as e:
            logger.error(f"检查键存在失败 {key}: {e}")
            return False
    
    def expire(self, key: str, seconds: int) -> bool:
        """设置键过期时间"""
        if not self.is_connected():
            return False
        
        try:
            return bool(self.redis_client.expire(key, seconds))
        except Exception as e:
            logger.error(f"设置过期时间失败 {key}: {e}")
            return False
    
    def ttl(self, key: str) -> int:
        """获取键剩余生存时间"""
        if not self.is_connected():
            return -1
        
        try:
            return self.redis_client.ttl(key)
        except Exception as e:
            logger.error(f"获取TTL失败 {key}: {e}")
            return -1

class CryptoCacheManager:
    """加密货币缓存管理器"""
    
    def __init__(self):
        self.redis = SimpleRedisManager()
        self.default_expire = 300  # 5分钟默认过期时间
    
    def cache_price(self, symbol: str, price_data: Dict) -> bool:
        """缓存价格数据"""
        key = f"crypto:price:{symbol.upper()}"
        return self.redis.set(key, price_data, self.default_expire)
    
    def get_price(self, symbol: str) -> Optional[Dict]:
        """获取价格数据"""
        key = f"crypto:price:{symbol.upper()}"
        return self.redis.get(key)
    
    def cache_chart_data(self, symbol: str, timeframe: str, data: list) -> bool:
        """缓存图表数据"""
        key = f"crypto:chart:{symbol.upper()}:{timeframe}"
        # 图表数据缓存时间更长
        return self.redis.set(key, data, 600)  # 10分钟
    
    def get_chart_data(self, symbol: str, timeframe: str) -> Optional[list]:
        """获取图表数据"""
        key = f"crypto:chart:{symbol.upper()}:{timeframe}"
        return self.redis.get(key)
    
    def cache_latest_prices(self, prices: list) -> bool:
        """缓存最新价格列表"""
        key = "crypto:latest_prices"
        return self.redis.set(key, prices, 60)  # 1分钟
    
    def get_latest_prices(self) -> Optional[list]:
        """获取最新价格列表"""
        key = "crypto:latest_prices"
        return self.redis.get(key)
    
    def cache_realtime_prices(self, prices: list) -> bool:
        """缓存实时价格列表（与历史数据分离）"""
        key = "crypto:realtime_prices"
        return self.redis.set(key, prices, 30)  # 30秒过期，更短的缓存时间
    
    def get_realtime_prices(self) -> Optional[list]:
        """获取实时价格列表"""
        key = "crypto:realtime_prices"
        return self.redis.get(key)
    
    def cache_realtime_price(self, symbol: str, price_data: Dict) -> bool:
        """缓存单个币种的实时价格数据"""
        key = f"crypto:realtime:{symbol.upper()}"
        return self.redis.set(key, price_data, 30)  # 30秒过期
    
    def get_realtime_price(self, symbol: str) -> Optional[Dict]:
        """获取单个币种的实时价格数据"""
        key = f"crypto:realtime:{symbol.upper()}"
        return self.redis.get(key)
    
    def invalidate_symbol(self, symbol: str):
        """清除某个币种的所有缓存"""
        if not self.redis.is_connected():
            return
        
        try:
            # 由于是单节点Redis，使用keys命令查找
            pattern = f"crypto:*:{symbol.upper()}*"
            keys = self.redis.redis_client.keys(pattern)
            if keys:
                self.redis.delete(*keys)
                logger.info(f"清除 {symbol} 相关缓存: {len(keys)} 个键")
        except Exception as e:
            logger.error(f"清除缓存失败: {e}")
    
    def get_cache_stats(self) -> dict:
        """获取缓存统计信息"""
        if not self.redis.is_connected():
            return {
                'connected': False,
                'total_keys': 0,
                'price_keys': 0,
                'chart_keys': 0,
                'memory_usage': 'N/A'
            }
        
        try:
            # 获取所有crypto相关的键
            all_keys = self.redis.redis_client.keys("crypto:*")
            price_keys = self.redis.redis_client.keys("crypto:price:*")
            chart_keys = self.redis.redis_client.keys("crypto:chart:*")
            
            # 获取内存使用情况
            info = self.redis.redis_client.info('memory')
            memory_usage = info.get('used_memory_human', 'N/A')
            
            return {
                'connected': True,
                'total_keys': len(all_keys),
                'price_keys': len(price_keys),
                'chart_keys': len(chart_keys),
                'memory_usage': memory_usage,
                'redis_version': self.redis.redis_client.info('server').get('redis_version', 'Unknown')
            }
        except Exception as e:
            logger.error(f"获取缓存统计失败: {e}")
            return {
                'connected': False,
                'error': str(e)
            }
    
    def clear_price_cache(self) -> bool:
        """清除所有价格缓存"""
        if not self.redis.is_connected():
            return False
        
        try:
            keys = self.redis.redis_client.keys("crypto:price:*")
            keys.extend(self.redis.redis_client.keys("crypto:latest_prices"))
            if keys:
                deleted = self.redis.delete(*keys)
                logger.info(f"清除价格缓存: {deleted} 个键")
                return True
            return True
        except Exception as e:
            logger.error(f"清除价格缓存失败: {e}")
            return False
    
    def clear_chart_cache(self) -> bool:
        """清除所有图表缓存"""
        if not self.redis.is_connected():
            return False
        
        try:
            keys = self.redis.redis_client.keys("crypto:chart:*")
            if keys:
                deleted = self.redis.delete(*keys)
                logger.info(f"清除图表缓存: {deleted} 个键")
                return True
            return True
        except Exception as e:
            logger.error(f"清除图表缓存失败: {e}")
            return False
    
    def clear_all_cache(self) -> bool:
        """清除所有缓存"""
        if not self.redis.is_connected():
            return False
        
        try:
            keys = self.redis.redis_client.keys("crypto:*")
            if keys:
                deleted = self.redis.delete(*keys)
                logger.info(f"清除所有缓存: {deleted} 个键")
                return True
            return True
        except Exception as e:
            logger.error(f"清除所有缓存失败: {e}")
            return False

def cache_result(expire: int = 300):
    """缓存装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = f"func:{func.__name__}:{hashlib.md5(str(args + tuple(kwargs.items())).encode()).hexdigest()}"
            
            # 尝试从缓存获取
            cache_manager = SimpleRedisManager()
            cached_result = cache_manager.get(cache_key)
            
            if cached_result is not None:
                logger.info(f"缓存命中: {func.__name__}")
                return cached_result
            
            # 执行函数
            result = func(*args, **kwargs)
            
            # 缓存结果
            cache_manager.set(cache_key, result, expire)
            logger.info(f"缓存结果: {func.__name__}")
            
            return result
        return wrapper
    return decorator

# 全局缓存管理器实例
_cache_manager = None

def get_cache_manager() -> CryptoCacheManager:
    """获取全局缓存管理器实例"""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CryptoCacheManager()
    return _cache_manager

# 使用示例
if __name__ == "__main__":
    # 测试缓存管理器
    cache = CryptoCacheManager()
    
    # 测试价格缓存
    btc_data = {
        "price": 45000,
        "change_24h": 2.5,
        "volume": 1000000,
        "timestamp": time.time()
    }
    
    if cache.cache_price("BTC", btc_data):
        print("✅ BTC价格缓存成功")
    
    cached_btc = cache.get_price("BTC")
    if cached_btc:
        print(f"✅ 从缓存获取BTC价格: ${cached_btc['price']}")
    
    # 测试装饰器
    @cache_result(expire=60)
    def get_market_data(symbol):
        print(f"正在获取 {symbol} 市场数据...")
        return {"symbol": symbol, "data": "market_data", "timestamp": time.time()}
    
    # 第一次调用
    result1 = get_market_data("ETH")
    print(f"第一次调用结果: {result1}")
    
    # 第二次调用（应该从缓存获取）
    result2 = get_market_data("ETH")
    print(f"第二次调用结果: {result2}")