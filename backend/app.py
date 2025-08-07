import sys
import os
import logging
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
core_path = os.path.join(project_root, 'core')
sys.path.insert(0, project_root)
sys.path.insert(0, core_path)

from flask import Flask, jsonify, request
from flask_cors import CORS

# 导入业务模块
from core.crypto_db import CryptoDatabase
from core.cache_manager import CacheManager

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建Flask应用
backend_app = Flask(__name__)
CORS(backend_app)

# 初始化组件
db = CryptoDatabase()
cache_manager = CacheManager()

# 初始化模块
if db.connect():
    print("数据库连接成功")
    db.disconnect()
else:
    print("数据库连接失败")
    
if cache_manager.connect():
    print("缓存连接成功")
else:
    print("缓存连接失败")

print("业务模块初始化完成")

# API路由定义

@backend_app.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

@backend_app.route('/api/latest-prices', methods=['GET'])
def get_latest_prices():
    """获取最新价格"""
    try:
        # 先从缓存获取
        btc_price = cache_manager.get_latest_price('BTC')
        eth_price = cache_manager.get_latest_price('ETH')
        
        if not btc_price or not eth_price:
            # 从数据库获取
            btc_data = db.get_latest_price('BTC')
            eth_data = db.get_latest_price('ETH')
            
            result = {
                'BTC': btc_data if btc_data else None,
                'ETH': eth_data if eth_data else None
            }
        else:
            result = {
                'BTC': btc_price,
                'ETH': eth_price
            }
        
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
        
        # 从数据库获取价格历史
        history = db.get_price_history(crypto, timeframe)
        
        return jsonify(history if history else [])
    
    except Exception as e:
        logger.error(f"获取价格历史失败: {e}")
        return jsonify({'error': str(e)}), 500

@backend_app.route('/api/chart-data', methods=['GET'])
def get_chart_data():
    """获取图表数据"""
    try:
        crypto = request.args.get('crypto', 'BTC')
        timeframe = request.args.get('timeframe', '24h')
        
        # 从数据库获取图表数据
        chart_data = db.get_chart_data(crypto, timeframe)
        
        return jsonify(chart_data if chart_data else {})
    
    except Exception as e:
        logger.error(f"获取图表数据失败: {e}")
        return jsonify({'error': str(e)}), 500

@backend_app.route('/api/btc-chart', methods=['GET'])
def get_btc_chart():
    """获取BTC图表数据"""
    try:
        chart_data = db.get_chart_data('BTC', '24h')
        
        return jsonify(chart_data if chart_data else {})
    
    except Exception as e:
        logger.error(f"获取BTC图表数据失败: {e}")
        return jsonify({'error': str(e)}), 500

@backend_app.route('/api/eth-chart', methods=['GET'])
def get_eth_chart():
    """获取ETH图表数据"""
    try:
        chart_data = db.get_chart_data('ETH', '24h')
        
        return jsonify(chart_data if chart_data else {})
    
    except Exception as e:
        logger.error(f"获取ETH图表数据失败: {e}")
        return jsonify({'error': str(e)}), 500

@backend_app.route('/api/kline-chart', methods=['GET'])
def get_kline_chart():
    """获取K线图表数据"""
    try:
        crypto = request.args.get('crypto', 'BTC')
        
        kline_data = db.get_kline_data(crypto)
        
        return jsonify(kline_data if kline_data else [])
    
    except Exception as e:
        logger.error(f"获取K线数据失败: {e}")
        return jsonify({'error': str(e)}), 500

@backend_app.route('/api/analysis', methods=['GET'])
def get_analysis():
    """获取分析报告"""
    try:
        crypto = request.args.get('crypto', 'BTC')
        
        # 从数据库获取分析数据
        analysis = db.get_analysis_data(crypto)
        
        return jsonify(analysis if analysis else {})
    
    except Exception as e:
        logger.error(f"获取分析报告失败: {e}")
        return jsonify({'error': str(e)}), 500

@backend_app.route('/api/cache/clear', methods=['POST'])
def clear_cache():
    """清除缓存"""
    try:
        cache_manager.clear_all_cache()
        return jsonify({'message': '缓存已清除'})
    
    except Exception as e:
        logger.error(f"清除缓存失败: {e}")
        return jsonify({'error': str(e)}), 500

@backend_app.route('/api/system/status', methods=['GET'])
def get_system_status():
    """获取系统状态"""
    try:
        status = {
            'timestamp': datetime.now().isoformat(),
            'database_connected': False,
            'cache_connected': False
        }
        
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