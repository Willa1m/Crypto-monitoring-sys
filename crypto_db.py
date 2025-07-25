import mysql.connector
from mysql.connector import pooling
import logging
from datetime import datetime
import pandas as pd
import time

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('crypto_db.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class CryptoDatabase:
    def __init__(self):
        """初始化数据库连接池"""
        self.pool_config = {
            'pool_name': 'crypto_pool',
            'pool_size': 3,  # 进一步减少连接池大小
            'pool_reset_session': True,
            'host': '192.168.73.130',
            'user': 'k1ll',
            'password': '654',
            'database': 'Scraping1',
            'port': 3306,
            'charset': 'utf8mb4',
            'autocommit': True,  # 启用自动提交减少锁定
            'connection_timeout': 30,  # 增加连接超时时间
            'connect_timeout': 30,  # 连接建立超时
            'read_timeout': 30,  # 读取超时
            'write_timeout': 30,  # 写入超时
            'sql_mode': 'TRADITIONAL',
            'use_unicode': True,
            'raise_on_warnings': False,  # 关闭警告异常
            'get_warnings': False,  # 不获取警告
            'buffered': True,  # 启用缓冲
            'consume_results': True  # 自动消费结果
        }
        
        self.connection_pool = None
        self.connection = None
        self.cursor = None
        
        # 初始化连接池
        self._init_connection_pool()
    
    def _init_connection_pool(self):
        """初始化连接池"""
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                # 先尝试关闭现有连接池
                if self.connection_pool:
                    try:
                        # 关闭连接池中的所有连接
                        for _ in range(self.pool_config['pool_size']):
                            try:
                                conn = self.connection_pool.get_connection()
                                if conn.is_connected():
                                    conn.close()
                            except:
                                pass
                    except:
                        pass
                    self.connection_pool = None
                
                # 创建新的连接池
                self.connection_pool = mysql.connector.pooling.MySQLConnectionPool(**self.pool_config)
                logging.info("数据库连接池初始化成功")
                return True
                
            except mysql.connector.Error as err:
                logging.error(f"连接池初始化失败 (尝试 {attempt + 1}/{max_retries}): {err}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    retry_delay *= 2  # 指数退避
                else:
                    self.connection_pool = None
                    return False
            except Exception as e:
                logging.error(f"连接池初始化异常 (尝试 {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    self.connection_pool = None
                    return False
        
        return False
            # 不抛出异常，允许应用程序继续运行
    
    def get_connection(self):
        """从连接池获取连接，带重试机制"""
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                if not self.connection_pool:
                    logging.warning("连接池未初始化，尝试重新初始化")
                    if not self._init_connection_pool():
                        logging.error("连接池重新初始化失败")
                        return None
                
                connection = self.connection_pool.get_connection()
                
                # 健康检查
                if connection and connection.is_connected():
                    try:
                        connection.ping(reconnect=True, attempts=3, delay=1)
                        return connection
                    except mysql.connector.Error:
                        if connection:
                            connection.close()
                        continue
                else:
                    if connection:
                        connection.close()
                    continue
                        
            except mysql.connector.Error as err:
                logging.warning(f"获取连接失败 (尝试 {attempt + 1}/{max_retries}): {err}")
                if "Too many connections" in str(err):
                    # 如果是连接过多错误，等待更长时间
                    time.sleep(retry_delay * 3)
                    # 尝试重新初始化连接池
                    if attempt == max_retries - 1:
                        logging.info("尝试重新初始化连接池以解决连接过多问题")
                        self._init_connection_pool()
                else:
                    time.sleep(retry_delay)
                
                if attempt < max_retries - 1:
                    retry_delay *= 2
                    
            except Exception as e:
                logging.warning(f"获取连接异常 (尝试 {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    retry_delay *= 2
        
        logging.error("无法获取数据库连接")
        return None
    
    def connect(self):
        """建立数据库连接"""
        try:
            self.connection = self.get_connection()
            if self.connection is None:
                logging.error("无法获取数据库连接")
                return False
            self.cursor = self.connection.cursor(buffered=True)
            logging.info("成功连接到 MariaDB 数据库")
            return True
        except mysql.connector.Error as err:
            logging.error(f"数据库连接错误: {err}")
            self.connection = None
            self.cursor = None
            return False
        except Exception as e:
            logging.error(f"连接过程中发生未知错误: {e}")
            self.connection = None
            self.cursor = None
            return False
    
    def disconnect(self):
        """断开数据库连接"""
        if self.cursor:
            self.cursor.close()
        if self.connection and self.connection.is_connected():
            self.connection.close()
            logging.info("数据库连接已关闭")
    
    def execute_query(self, query, params=None, fetch=False):
        """执行SQL查询，带重试机制"""
        max_retries = 3
        retry_delay = 0.5
        
        for attempt in range(max_retries):
            try:
                # 检查连接状态
                if not self.connection or not self.connection.is_connected():
                    if not self.connect():
                        logging.warning(f"重连失败 (尝试 {attempt + 1}/{max_retries})")
                        if attempt < max_retries - 1:
                            time.sleep(retry_delay)
                            retry_delay *= 2
                            continue
                        else:
                            return False
                
                # 确保cursor存在
                if not self.cursor:
                    logging.error("数据库游标未初始化")
                    return False
                
                if params:
                    self.cursor.execute(query, params)
                else:
                    self.cursor.execute(query)
                
                if fetch:
                    result = self.cursor.fetchall()
                    return result
                else:
                    self.connection.commit()
                    return True
                    
            except mysql.connector.Error as err:
                error_code = err.errno if hasattr(err, 'errno') else None
                
                # 连接相关错误，尝试重连
                if error_code in (2006, 2013, 2027):  # 连接丢失、服务器断开、数据包错误
                    logging.warning(f"连接错误 (尝试 {attempt + 1}/{max_retries}): {err}")
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        retry_delay *= 2
                        try:
                            self.connect()
                        except:
                            pass
                        continue
                
                logging.error(f"SQL执行错误: {err}")
                if self.connection:
                    self.connection.rollback()
                return False
            except Exception as e:
                logging.error(f"未知错误: {e}")
                return False
        
        logging.error(f"查询执行失败，已重试 {max_retries} 次")
        return False
    
    def clear_database(self):
        """清空数据库中的所有表"""
        try:
            # 获取所有表名
            self.cursor.execute("SHOW TABLES")
            tables = self.cursor.fetchall()
            
            # 禁用外键检查
            self.cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
            
            # 删除所有表
            for table in tables:
                table_name = table[0]
                self.cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
                logging.info(f"删除表: {table_name}")
            
            # 重新启用外键检查
            self.cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
            self.connection.commit()
            
            logging.info("数据库清空完成")
            return True
        except mysql.connector.Error as err:
            logging.error(f"清空数据库错误: {err}")
            return False
    
    def create_tables(self):
        """创建数据库表结构"""
        
        # 创建加密货币基本信息表
        crypto_info_table = """
        CREATE TABLE IF NOT EXISTS crypto_info (
            id INT AUTO_INCREMENT PRIMARY KEY,
            symbol VARCHAR(10) NOT NULL UNIQUE,
            name VARCHAR(50) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
        """
        
        # 创建当前价格表
        current_prices_table = """
        CREATE TABLE IF NOT EXISTS current_prices (
            id INT AUTO_INCREMENT PRIMARY KEY,
            symbol VARCHAR(10) NOT NULL,
            price DECIMAL(30, 15) NOT NULL,
            change_24h DECIMAL(30, 15),
            timestamp TIMESTAMP NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_symbol (symbol),
            INDEX idx_timestamp (timestamp),
            FOREIGN KEY (symbol) REFERENCES crypto_info(symbol) ON DELETE CASCADE
        )
        """
        
        # 创建分钟级历史数据表
        minute_data_table = """
        CREATE TABLE IF NOT EXISTS minute_data (
            id INT AUTO_INCREMENT PRIMARY KEY,
            symbol VARCHAR(10) NOT NULL,
            date TIMESTAMP NOT NULL,
            open_price DECIMAL(30, 15) NOT NULL,
            high_price DECIMAL(30, 15) NOT NULL,
            low_price DECIMAL(30, 15) NOT NULL,
            close_price DECIMAL(30, 15) NOT NULL,
            volume DECIMAL(30, 15) DEFAULT 0,
            quote_volume DECIMAL(30, 15) DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE KEY unique_symbol_date (symbol, date),
            INDEX idx_symbol (symbol),
            INDEX idx_date (date),
            FOREIGN KEY (symbol) REFERENCES crypto_info(symbol) ON DELETE CASCADE
        )
        """
        
        # 创建小时级历史数据表
        hour_data_table = """
        CREATE TABLE IF NOT EXISTS hour_data (
            id INT AUTO_INCREMENT PRIMARY KEY,
            symbol VARCHAR(10) NOT NULL,
            date TIMESTAMP NOT NULL,
            open_price DECIMAL(30, 15) NOT NULL,
            high_price DECIMAL(30, 15) NOT NULL,
            low_price DECIMAL(30, 15) NOT NULL,
            close_price DECIMAL(30, 15) NOT NULL,
            volume DECIMAL(30, 15) DEFAULT 0,
            quote_volume DECIMAL(30, 15) DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE KEY unique_symbol_date (symbol, date),
            INDEX idx_symbol (symbol),
            INDEX idx_date (date),
            FOREIGN KEY (symbol) REFERENCES crypto_info(symbol) ON DELETE CASCADE
        )
        """
        
        # 创建天级历史数据表
        day_data_table = """
        CREATE TABLE IF NOT EXISTS day_data (
            id INT AUTO_INCREMENT PRIMARY KEY,
            symbol VARCHAR(10) NOT NULL,
            date TIMESTAMP NOT NULL,
            open_price DECIMAL(30, 15) NOT NULL,
            high_price DECIMAL(30, 15) NOT NULL,
            low_price DECIMAL(30, 15) NOT NULL,
            close_price DECIMAL(30, 15) NOT NULL,
            volume DECIMAL(30, 15) DEFAULT 0,
            quote_volume DECIMAL(30, 15) DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE KEY unique_symbol_date (symbol, date),
            INDEX idx_symbol (symbol),
            INDEX idx_date (date),
            FOREIGN KEY (symbol) REFERENCES crypto_info(symbol) ON DELETE CASCADE
        )
        """
        
        tables = [
            ("crypto_info", crypto_info_table),
            ("current_prices", current_prices_table),
            ("minute_data", minute_data_table),
            ("hour_data", hour_data_table),
            ("day_data", day_data_table)
        ]
        
        for table_name, table_sql in tables:
            if self.execute_query(table_sql):
                logging.info(f"成功创建表: {table_name}")
            else:
                logging.error(f"创建表失败: {table_name}")
                return False
        
        return True
    
    def insert_crypto_info(self, symbol, name):
        """插入加密货币基本信息"""
        query = """
        INSERT INTO crypto_info (symbol, name) 
        VALUES (%s, %s) 
        ON DUPLICATE KEY UPDATE name = VALUES(name), updated_at = CURRENT_TIMESTAMP
        """
        return self.execute_query(query, (symbol, name))
    
    def insert_current_price(self, symbol, price, change_24h, timestamp):
        """插入当前价格数据"""
        query = """
        INSERT INTO current_prices (symbol, price, change_24h, timestamp) 
        VALUES (%s, %s, %s, %s)
        """
        return self.execute_query(query, (symbol, price, change_24h, timestamp))
    
    def insert_historical_data(self, timeframe, symbol, date, open_price, high_price, 
                             low_price, close_price, volume=0, quote_volume=0):
        """插入历史数据"""
        table_map = {
            'minute': 'minute_data',
            'hour': 'hour_data',
            'day': 'day_data'
        }
        
        if timeframe not in table_map:
            logging.error(f"不支持的时间范围: {timeframe}")
            return False
        
        table_name = table_map[timeframe]
        query = f"""
        INSERT INTO {table_name} 
        (symbol, date, open_price, high_price, low_price, close_price, volume, quote_volume) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE 
        open_price = VALUES(open_price),
        high_price = VALUES(high_price),
        low_price = VALUES(low_price),
        close_price = VALUES(close_price),
        volume = VALUES(volume),
        quote_volume = VALUES(quote_volume)
        """
        
        return self.execute_query(query, (symbol, date, open_price, high_price, 
                                        low_price, close_price, volume, quote_volume))
    
    def get_latest_prices(self, connection=None):
        """获取最新价格数据"""
        query = """
        SELECT ci.name, cp.symbol, cp.price, cp.change_24h, cp.timestamp
        FROM current_prices cp
        JOIN crypto_info ci ON cp.symbol = ci.symbol
        WHERE cp.id IN (
            SELECT MAX(id) FROM current_prices GROUP BY symbol
        )
        ORDER BY cp.timestamp DESC
        """
        
        if connection:
            # 使用传入的连接
            try:
                cursor = connection.cursor()
                cursor.execute(query)
                result = cursor.fetchall()
                cursor.close()
                return result
            except Exception as e:
                logging.error(f"使用连接池执行查询失败: {str(e)}")
                return []
        else:
            # 使用原有的execute_query方法（向后兼容）
            return self.execute_query(query, fetch=True)
    
    def get_historical_data(self, timeframe, symbol=None, limit=100, connection=None):
        """获取历史数据"""
        table_map = {
            'minute': 'minute_data',
            'hour': 'hour_data',
            'day': 'day_data'
        }
        
        if timeframe not in table_map:
            return []
        
        table_name = table_map[timeframe]
        
        if symbol:
            query = f"""
            SELECT symbol, date, open_price, high_price, low_price, close_price, volume
            FROM {table_name}
            WHERE symbol = %s
            ORDER BY date DESC
            LIMIT %s
            """
            params = (symbol, limit)
        else:
            query = f"""
            SELECT symbol, date, open_price, high_price, low_price, close_price, volume
            FROM {table_name}
            ORDER BY date DESC
            LIMIT %s
            """
            params = (limit,)
        
        if connection:
            # 使用传入的连接
            try:
                cursor = connection.cursor()
                cursor.execute(query, params)
                result = cursor.fetchall()
                cursor.close()
                return result
            except Exception as e:
                logging.error(f"使用连接池执行查询失败: {str(e)}")
                return []
        else:
            # 使用原有的execute_query方法（向后兼容）
            return self.execute_query(query, params, fetch=True)

def rebuild_database():
    """重建数据库结构"""
    db = CryptoDatabase()
    
    if not db.connect():
        return False
    
    try:
        # 清空数据库
        logging.info("开始清空数据库...")
        if not db.clear_database():
            return False
        
        # 创建表结构
        logging.info("开始创建表结构...")
        if not db.create_tables():
            return False
        
        # 插入基本的加密货币信息
        cryptocurrencies = {
            "BTC": "Bitcoin",
            "ETH": "Ethereum"
        }
        
        for symbol, name in cryptocurrencies.items():
            if not db.insert_crypto_info(symbol, name):
                logging.error(f"插入加密货币信息失败: {symbol}")
                return False
            logging.info(f"成功插入加密货币信息: {name} ({symbol})")
        
        logging.info("数据库重建完成")
        return True
        
    finally:
        db.disconnect()

if __name__ == "__main__":
    logging.info("开始重建数据库")
    if rebuild_database():
        logging.info("数据库重建成功")
    else:
        logging.error("数据库重建失败")