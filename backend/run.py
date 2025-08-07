#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
后端服务启动脚本
"""

import os
import sys
import argparse
import logging
from app import backend_app

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('backend.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='加密货币监控系统 - 后端API服务')
    
    parser.add_argument(
        '--host',
        type=str,
        default='0.0.0.0',
        help='服务器主机地址 (默认: 0.0.0.0)'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=5001,
        help='服务器端口 (默认: 5001)'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='启用调试模式'
    )
    
    return parser.parse_args()

def main():
    """主函数"""
    args = parse_arguments()
    
    try:
        # 启动后端API服务
        backend_app.run(
            host=args.host,
            port=args.port,
            debug=args.debug
        )
    except KeyboardInterrupt:
        logging.info("收到中断信号，正在停止服务...")
    except Exception as e:
        logging.error(f"服务启动失败: {str(e)}")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())