import sys
import os
import logging
from datetime import datetime, timedelta
import random

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from flask import Flask, jsonify, request
from flask_cors import CORS

# 尝试导入业务模块，如果失败则使用模拟数据
try:
    from crypto_db import CryptoDatabase
    from crypto_analyzer import CryptoAnalyzer
    from crypto_cache_manager import CryptoCacheManager
    MODULES_AVAILABLE = True
except ImportError as e:
    print(f"警告: 无法导入业务模块 ({e})，将使用模拟数据")
    MODULES_AVAILABLE = False

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建Flask应用
backend_app = Flask(__name__)
CORS(backend_app)

# 初始化组件（如果模块可用）
if MODULES_AVAILABLE:
    try:
        db = CryptoDatabase()
        analyzer = CryptoAnalyzer()
        cache_manager = CryptoCacheManager()
        print("业务模块初始化成功")
    except Exception as e:
        print(f"业务模块初始化失败: {e}")
        MODULES_AVAILABLE = False

# 模拟数据生成器
def get_mock_data():
    base_price_btc = 45000
    base_price_eth = 3000
    
    return {
        'latest_prices': {
            'BTC': {
                'price': base_price_btc + random.randint(-2000, 2000),
                'change_24h': random.uniform(-5, 5),
                'volume': random.randint(1000000, 5000000)
            },
            'ETH': {
                'price': base_price_eth + random.randint(-200, 200),
                'change_24h': random.uniform(-5, 5),
                'volume': random.randint(500000, 2000000)
            }
        },
        'chart_data': {
            'price_data': [
                {
                    'date': (datetime.now() - timedelta(hours=i)).isoformat(),
                    'price': base_price_btc + random.randint(-1000, 1000)
                } for i in range(24, 0, -1)
            ]
        },
        'kline_data': [
            {
                'date': (datetime.now() - timedelta(hours=i)).isoformat(),
                'open': base_price_btc + random.randint(-500, 500),
                'high': base_price_btc + random.randint(0, 1000),
                'low': base_price_btc + random.randint(-1000, 0),
                'close': base_price_btc + random.randint(-500, 500),
                'volume': random.randint(100, 1000)
            } for i in range(24, 0, -1)
        ],
        'analysis': {
            'trend': '上涨',
            'support': 44000,
            'resistance': 47000,
            'recommendation': '持有'
        }
    }

# API路由定义

@backend_app.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'modules_available': MODULES_AVAILABLE
    })

@backend_app.route('/api/latest-prices', methods=['GET'])
def get_latest_prices():
    """获取最新价格"""
    try:
        if MODULES_AVAILABLE:
            # 使用真实数据
            btc_price = cache_manager.get_latest_price('BTC')
            eth_price = cache_manager.get_latest_price('ETH')
            
            if not btc_price or not eth_price:
                # 从数据库获取
                btc_data = db.get_latest_price('BTC')
                eth_data = db.get_latest_price('ETH')
                
                result = {
                    'BTC': btc_data if btc_data else {'price': 45000, 'change_24h': 0},
                    'ETH': eth_data if eth_data else {'price': 3000, 'change_24h': 0}
                }
            else:
                result = {
                    'BTC': btc_price,
                    'ETH': eth_price
                }
        else:
            # 使用模拟数据
            mock_data = get_mock_data()
            result = mock_data['latest_prices']
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"获取最新价格失败: {e}")
        return jsonify({'error': str(e)}), 500

@backend_app.route('/api/price-history', methods=['GET'])
def get_price_history():
    """获取价格历史"""
    try:
        crypto = request.args.get('crypto', 'BTC')
        timeframe = request.args.get('timeframe', '24h')
        
        if MODULES_AVAILABLE:
            # 使用真实数据
            history = db.get_price_history(crypto, timeframe)
            if not history:
                # 如果没有数据，返回模拟数据
                mock_data = get_mock_data()
                history = mock_data['chart_data']['price_data']
        else:
            # 使用模拟数据
            mock_data = get_mock_data()
            history = mock_data['chart_data']['price_data']
        
        return jsonify(history)
    
    except Exception as e:
        logger.error(f"获取价格历史失败: {e}")
        return jsonify({'error': str(e)}), 500

@backend_app.route('/api/chart-data', methods=['GET'])
def get_chart_data():
    """获取图表数据"""
    try:
        crypto = request.args.get('crypto', 'BTC')
        timeframe = request.args.get('timeframe', '24h')
        
        if MODULES_AVAILABLE:
            # 使用真实数据
            chart_data = db.get_chart_data(crypto, timeframe)
            if not chart_data:
                mock_data = get_mock_data()
                chart_data = mock_data['chart_data']
        else:
            # 使用模拟数据
            mock_data = get_mock_data()
            chart_data = mock_data['chart_data']
        
        return jsonify(chart_data)
    
    except Exception as e:
        logger.error(f"获取图表数据失败: {e}")
        return jsonify({'error': str(e)}), 500

@backend_app.route('/api/btc-chart', methods=['GET'])
def get_btc_chart():
    """获取BTC图表数据"""
    try:
        if MODULES_AVAILABLE:
            chart_data = db.get_chart_data('BTC', '24h')
            if not chart_data:
                mock_data = get_mock_data()
                chart_data = mock_data['chart_data']
        else:
            mock_data = get_mock_data()
            chart_data = mock_data['chart_data']
        
        return jsonify(chart_data)
    
    except Exception as e:
        logger.error(f"获取BTC图表数据失败: {e}")
        return jsonify({'error': str(e)}), 500

@backend_app.route('/api/eth-chart', methods=['GET'])
def get_eth_chart():
    """获取ETH图表数据"""
    try:
        if MODULES_AVAILABLE:
            chart_data = db.get_chart_data('ETH', '24h')
            if not chart_data:
                mock_data = get_mock_data()
                chart_data = mock_data['chart_data']
        else:
            mock_data = get_mock_data()
            chart_data = mock_data['chart_data']
        
        return jsonify(chart_data)
    
    except Exception as e:
        logger.error(f"获取ETH图表数据失败: {e}")
        return jsonify({'error': str(e)}), 500

@backend_app.route('/api/kline-chart', methods=['GET'])
def get_kline_chart():
    """获取K线图表数据"""
    try:
        crypto = request.args.get('crypto', 'BTC')
        
        if MODULES_AVAILABLE:
            kline_data = db.get_kline_data(crypto)
            if not kline_data:
                mock_data = get_mock_data()
                kline_data = mock_data['kline_data']
        else:
            mock_data = get_mock_data()
            kline_data = mock_data['kline_data']
        
        return jsonify(kline_data)
    
    except Exception as e:
        logger.error(f"获取K线数据失败: {e}")
        return jsonify({'error': str(e)}), 500

@backend_app.route('/api/analysis', methods=['GET'])
def get_analysis():
    """获取分析报告"""
    try:
        crypto = request.args.get('crypto', 'BTC')
        
        if MODULES_AVAILABLE:
            analysis = analyzer.get_analysis_report(crypto)
            if not analysis:
                mock_data = get_mock_data()
                analysis = mock_data['analysis']
        else:
            mock_data = get_mock_data()
            analysis = mock_data['analysis']
        
        return jsonify(analysis)
    
    except Exception as e:
        logger.error(f"获取分析报告失败: {e}")
        return jsonify({'error': str(e)}), 500

@backend_app.route('/api/cache/clear', methods=['POST'])
def clear_cache():
    """清除缓存"""
    try:
        if MODULES_AVAILABLE and cache_manager:
            cache_manager.clear_all_cache()
            return jsonify({'message': '缓存已清除'})
        else:
            return jsonify({'message': '缓存功能不可用'})
    
    except Exception as e:
        logger.error(f"清除缓存失败: {e}")
        return jsonify({'error': str(e)}), 500

@backend_app.route('/api/system/status', methods=['GET'])
def get_system_status():
    """获取系统状态"""
    try:
        status = {
            'timestamp': datetime.now().isoformat(),
            'modules_available': MODULES_AVAILABLE,
            'database_connected': False,
            'cache_connected': False
        }
        
        if MODULES_AVAILABLE:
            try:
                # 检查数据库连接
                db.get_latest_price('BTC')
                status['database_connected'] = True
            except:
                pass
            
            try:
                # 检查缓存连接
                cache_manager.get_latest_price('BTC')
                status['cache_connected'] = True
            except:
                pass
        
        return jsonify(status)
    
    except Exception as e:
        logger.error(f"获取系统状态失败: {e}")
        return jsonify({'error': str(e)}), 500

# 错误处理
@backend_app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'API端点未找到'}), 404

@backend_app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': '内部服务器错误'}), 500

if __name__ == '__main__':
    backend_app.run(debug=True, host='0.0.0.0', port=5000)