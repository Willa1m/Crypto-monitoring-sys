from flask import Flask, render_template, jsonify, request
import logging
from datetime import datetime
import os
from crypto_db import CryptoDatabase
from crypto_analyzer import CryptoAnalyzer
from simple_redis_manager import CryptoCacheManager

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class CryptoWebApp:
    def __init__(self):
        # 获取项目根目录路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 在Docker环境中，使用绝对路径
        if os.path.exists('/app/templates'):
            template_folder = '/app/templates'
            static_folder = '/app/static'
        else:
            # 本地开发环境
            project_root = os.path.dirname(current_dir)
            template_folder = os.path.join(project_root, 'templates')
            static_folder = os.path.join(project_root, 'static')
        
        self.app = Flask(__name__, 
                        template_folder=template_folder,
                        static_folder=static_folder)
        self.db = CryptoDatabase()
        self.analyzer = CryptoAnalyzer()
        
        # 初始化Redis缓存管理器
        try:
            self.redis_manager = CryptoCacheManager()
            logging.info("Redis缓存管理器初始化成功")
        except Exception as e:
            logging.warning(f"Redis缓存管理器初始化失败: {e}")
            self.redis_manager = None
            
        self.setup_routes()
    
    def setup_routes(self):
        """设置路由"""
        self.app.route('/')(self.index)
        self.app.route('/bitcoin')(self.bitcoin)
        self.app.route('/ethereum')(self.ethereum)
        self.app.route('/kline')(self.kline)
        self.app.route('/api/latest_prices')(self.api_latest_prices)
        self.app.route('/api/chart_data')(self.api_chart_data)
        self.app.route('/api/btc_data')(self.api_btc_data)
        self.app.route('/api/eth_data')(self.api_eth_data)
        self.app.route('/api/kline_data')(self.api_kline_data)
        self.app.route('/api/refresh_charts', methods=['POST'])(self.api_refresh_charts)
        
        # 缓存管理API
        self.app.route('/api/cache/stats')(self.api_cache_stats)
        self.app.route('/api/cache/clear', methods=['POST'])(self.api_clear_cache)
    
    def process_chart_data(self, data, symbol):
        """处理图表数据，计算三条曲线：价格、成交量、波动率"""
        if not data:
            return {
                'price_data': [],
                'volume_data': [],
                'volatility_data': []
            }
        
        # 过滤指定symbol的数据
        filtered_data = [item for item in data if item['symbol'] == symbol]
        
        if not filtered_data:
            return {
                'price_data': [],
                'volume_data': [],
                'volatility_data': []
            }
        
        # 按时间排序
        filtered_data.sort(key=lambda x: x['date'])
        
        # 准备三条曲线的数据
        price_data = []
        volume_data = []
        volatility_data = []
        
        # 计算移动平均和波动率的窗口大小
        window_size = min(10, len(filtered_data))
        
        for i, item in enumerate(filtered_data):
            # 价格数据
            price_data.append({
                'date': item['date'],
                'price': item['close'],
                'high': item['high'],
                'low': item['low'],
                'open': item['open']
            })
            
            # 成交量数据
            volume_data.append({
                'date': item['date'],
                'volume': item['volume']
            })
            
            # 计算波动率（使用滑动窗口）
            if i >= window_size - 1:
                # 获取窗口内的价格数据
                window_prices = [filtered_data[j]['close'] for j in range(i - window_size + 1, i + 1)]
                
                # 计算标准差作为波动率
                mean_price = sum(window_prices) / len(window_prices)
                variance = sum((price - mean_price) ** 2 for price in window_prices) / len(window_prices)
                volatility = variance ** 0.5
                
                volatility_data.append({
                    'date': item['date'],
                    'volatility': volatility,
                    'volatility_percent': (volatility / mean_price) * 100 if mean_price > 0 else 0
                })
        
        return {
            'price_data': price_data,
            'volume_data': volume_data,
            'volatility_data': volatility_data
        }
    
    def get_latest_prices(self):
        """从缓存或数据库获取最新价格"""
        # 首先尝试从Redis缓存获取
        if self.redis_manager:
            try:
                cached_prices = self.redis_manager.get_latest_prices()
                if cached_prices:
                    logging.info("从Redis缓存获取最新价格数据")
                    return cached_prices
                else:
                    logging.info("Redis缓存中没有最新价格数据，从数据库获取")
            except Exception as e:
                logging.warning(f"从Redis缓存获取价格数据失败: {e}")
        
        # 从数据库获取数据
        connection = None
        try:
            # 从连接池获取连接
            connection = self.db.get_connection()
            if not connection:
                logging.error("数据库连接失败")
                return []
            
            # 使用连接获取数据
            data = self.db.get_latest_prices(connection=connection)
            
            if not data or len(data) == 0:
                logging.warning("数据库中没有价格数据")
                return []
            
            # 转换数据格式
            result = []
            for item in data:
                name, symbol, price, change_24h, timestamp = item
                result.append({
                    'name': name,
                    'symbol': symbol,
                    'price': float(price),
                    'change_24h': float(change_24h) if change_24h is not None else 0.0,
                    'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S') if hasattr(timestamp, 'strftime') else str(timestamp)
                })
            
            # 将数据缓存到Redis（缓存60秒）
            if self.redis_manager and result:
                try:
                    self.redis_manager.cache_latest_prices(result)
                    logging.info("最新价格数据已缓存到Redis")
                except Exception as e:
                    logging.warning(f"缓存价格数据到Redis失败: {e}")
            
            return result
        except Exception as e:
            logging.error(f"获取最新价格时出错: {str(e)}")
            return []
        finally:
            # 确保连接被正确释放回连接池
            if connection:
                try:
                    connection.close()
                except:
                    pass
    

    
    def get_chart_data(self, timeframe, symbol=None, limit=100):
        """从缓存或数据库获取图表数据"""
        # 首先尝试从Redis缓存获取
        if self.redis_manager and symbol:
            try:
                cached_data = self.redis_manager.get_chart_data(symbol, timeframe)
                if cached_data:
                    logging.info(f"从Redis缓存获取{symbol}的{timeframe}图表数据")
                    return cached_data
                else:
                    logging.info(f"Redis缓存中没有{symbol}的{timeframe}图表数据，从数据库获取")
            except Exception as e:
                logging.warning(f"从Redis缓存获取图表数据失败: {e}")
        
        # 从数据库获取数据
        connection = None
        try:
            # 从连接池获取连接
            connection = self.db.get_connection()
            if not connection:
                logging.error("数据库连接失败")
                return []
            
            # 获取历史数据
            data = self.db.get_historical_data(timeframe, symbol, limit, connection=connection)
            
            if not data or len(data) == 0:
                logging.warning(f"数据库中没有{timeframe}级数据")
                return []
            
            # 转换数据格式
            result = []
            for item in data:
                # 数据库返回的是tuple格式: (symbol, date, open_price, high_price, low_price, close_price, volume)
                symbol_name, date, open_price, high_price, low_price, close_price, volume = item
                result.append({
                    'symbol': symbol_name,
                    'date': date.strftime('%Y-%m-%d %H:%M:%S') if hasattr(date, 'strftime') else str(date),
                    'open': float(open_price),
                    'high': float(high_price),
                    'low': float(low_price),
                    'close': float(close_price),
                    'volume': float(volume) if volume is not None else 0.0
                })
            
            # 将数据缓存到Redis（缓存5分钟）
            if self.redis_manager and result and symbol:
                try:
                    self.redis_manager.cache_chart_data(symbol, timeframe, result)
                    logging.info(f"{symbol}的{timeframe}图表数据已缓存到Redis")
                except Exception as e:
                    logging.warning(f"缓存图表数据到Redis失败: {e}")
            
            return result
        except Exception as e:
            logging.error(f"获取图表数据时出错: {str(e)}")
            return []
        finally:
            # 确保连接被正确释放回连接池
            if connection:
                try:
                    connection.close()
                except:
                    pass
    
    def get_cache_stats(self):
        """获取缓存统计信息"""
        if not self.redis_manager:
            return {
                'status': 'disabled',
                'message': 'Redis缓存未启用'
            }
        
        try:
            stats = self.redis_manager.get_cache_stats()
            return {
                'status': 'active',
                'stats': stats
            }
        except Exception as e:
            logging.error(f"获取缓存统计信息失败: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def clear_cache(self, cache_type=None):
        """清理缓存"""
        if not self.redis_manager:
            return {
                'success': False,
                'message': 'Redis缓存未启用'
            }
        
        try:
            if cache_type == 'prices':
                # 清理价格缓存
                result = self.redis_manager.clear_price_cache()
            elif cache_type == 'charts':
                # 清理图表缓存
                result = self.redis_manager.clear_chart_cache()
            else:
                # 清理所有缓存
                result = self.redis_manager.clear_all_cache()
            
            return {
                'success': True,
                'cleared_keys': result,
                'message': f'成功清理{cache_type or "所有"}缓存'
            }
        except Exception as e:
            logging.error(f"清理缓存失败: {e}")
            return {
                'success': False,
                'message': str(e)
            }

    # 路由处理函数
    def index(self):
        """主页"""
        return render_template('index.html')
    
    def bitcoin(self):
        """比特币页面"""
        return render_template('bitcoin.html')
    
    def ethereum(self):
        """以太坊页面"""
        return render_template('ethereum.html')
    
    def kline(self):
        """K线图页面"""
        return render_template('kline.html')
    
    def api_latest_prices(self):
        """API: 获取最新价格"""
        try:
            prices = self.get_latest_prices()
            return jsonify({
                'success': True,
                'data': prices
            })
        except Exception as e:
            logging.error(f"API获取最新价格时出错: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    def api_chart_data(self):
        """API: 获取图表数据"""
        try:
            timeframe = request.args.get('timeframe', 'hour')
            symbol = request.args.get('symbol')
            limit = int(request.args.get('limit', 100))
            
            data = self.get_chart_data(timeframe, symbol, limit)
            return jsonify({
                'success': True,
                'data': data
            })
        except Exception as e:
            logging.error(f"API获取图表数据时出错: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    def api_btc_data(self):
        """API: 获取比特币数据（三条曲线）"""
        try:
            timeframe = request.args.get('timeframe', 'hour')
            limit = int(request.args.get('limit', 100))
            
            # 获取原始数据
            raw_data = self.get_chart_data(timeframe, 'BTC', limit)
            
            # 处理数据，生成三条曲线
            processed_data = self.process_chart_data(raw_data, 'BTC')
            
            return jsonify({
                'success': True,
                'data': processed_data
            })
        except Exception as e:
            logging.error(f"API获取比特币数据时出错: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    def api_eth_data(self):
        """API: 获取以太坊数据（三条曲线）"""
        try:
            timeframe = request.args.get('timeframe', 'hour')
            limit = int(request.args.get('limit', 100))
            
            # 获取原始数据
            raw_data = self.get_chart_data(timeframe, 'ETH', limit)
            
            # 处理数据，生成三条曲线
            processed_data = self.process_chart_data(raw_data, 'ETH')
            
            return jsonify({
                'success': True,
                'data': processed_data
            })
        except Exception as e:
            logging.error(f"API获取以太坊数据时出错: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    def api_refresh_charts(self):
        """API: 刷新图表"""
        try:
            # 运行分析器生成新的图表
            self.analyzer.run_analysis()
            
            return jsonify({
                'success': True,
                'message': '图表已刷新'
            })
        except Exception as e:
            logging.error(f"API刷新图表时出错: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    def api_cache_stats(self):
        """API: 获取缓存统计信息"""
        try:
            stats = self.get_cache_stats()
            return jsonify(stats)
        except Exception as e:
            logging.error(f"API获取缓存统计信息时出错: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500
    
    def api_clear_cache(self):
        """API: 清理缓存"""
        try:
            cache_type = request.json.get('type') if request.json else None
            result = self.clear_cache(cache_type)
            
            if result['success']:
                return jsonify(result)
            else:
                return jsonify(result), 400
        except Exception as e:
            logging.error(f"API清理缓存时出错: {str(e)}")
            return jsonify({
                'success': False,
                'message': str(e)
            }), 500
    
    def api_kline_data(self):
        """API: 获取K线数据"""
        try:
            from kline_backend import kline_backend
            
            symbol = request.args.get('symbol', 'BTC')
            timeframe = request.args.get('timeframe', 'hour')
            limit = int(request.args.get('limit', 100))
            
            # 使用新的后端处理模块获取数据
            data = kline_backend.get_kline_data_with_indicators(symbol, timeframe, limit)
            
            return jsonify({
                'success': True,
                'data': data
            })
        except Exception as e:
            logging.error(f"API获取K线数据时出错: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    def get_local_ip(self):
        """获取本机局域网IP地址"""
        try:
            import socket
            # 创建一个UDP socket
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # 连接到一个远程地址（不会真正发送数据）
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except Exception:
            return "127.0.0.1"
    
    def run(self, debug=True, host='0.0.0.0', port=5000):
        """运行应用"""
        local_ip = self.get_local_ip()
        
        print("\n" + "="*60)
        print("🚀 加密货币监控系统 - Web服务器已启动")
        print("="*60)
        print(f"📍 本地访问地址: http://127.0.0.1:{port}")
        print(f"🌐 局域网访问地址: http://{local_ip}:{port}")
        print(f"📱 手机访问地址: http://{local_ip}:{port}")
        print("\n💡 让其他人访问的方法:")
        print(f"   1. 同一局域网用户可直接访问: http://{local_ip}:{port}")
        print(f"   2. 手机连接同一WiFi后访问: http://{local_ip}:{port}")
        print("   3. 外网访问需要配置路由器端口转发")
        print("="*60)
        
        logging.info(f"启动Web应用，本地地址: http://127.0.0.1:{port}")
        logging.info(f"启动Web应用，局域网地址: http://{local_ip}:{port}")
        
        self.app.run(debug=debug, host=host, port=port)

# 创建全局应用实例，供其他模块导入
crypto_app = CryptoWebApp()
app = crypto_app.app  # Flask 应用对象

if __name__ == '__main__':
    crypto_app.run()