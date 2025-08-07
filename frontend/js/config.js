// API 配置
const API_CONFIG = {
    BASE_URL: '',  // 使用相对路径，通过Nginx代理
    ENDPOINTS: {
        HEALTH: '/health',
        LATEST_PRICES: '/api/latest-prices',
        PRICE_HISTORY: '/api/price-history',
        CHART_DATA_BTC: '/api/btc-chart',
        CHART_DATA_ETH: '/api/eth-chart',
        CHART_DATA_KLINE: '/api/kline-chart',
        ANALYSIS_REPORT: '/api/analysis',
        CACHE_CLEAR: '/api/cache/clear',
        CACHE_STATUS: '/api/cache/status',
        SYSTEM_STATUS: '/api/system/status'
    },
    REQUEST_CONFIG: {
        timeout: 10000,  // 请求超时时间（毫秒）
        headers: {
            'Content-Type': 'application/json'
        }
    },
    
    // 数据刷新间隔（毫秒）
    REFRESH_INTERVALS: {
        PRICES: 5000,    // 5秒
        CHARTS: 30000,   // 30秒
        STATUS: 60000    // 1分钟
    }
};

// 应用配置
const APP_CONFIG = {
    // 默认设置
    DEFAULT_CRYPTO: 'BTC',
    DEFAULT_TIMEFRAME: 'hour',
    
    // 自动刷新间隔（毫秒）
    REFRESH_INTERVAL: 5000,  // 5秒
    
    // 图表配置
    CHART_CONFIG: {
        responsive: true,
        maintainAspectRatio: false,
        animation: {
            duration: 1000
        },
        scales: {
            x: {
                type: 'time',
                time: {
                    displayFormats: {
                        minute: 'HH:mm',
                        hour: 'MM-DD HH:mm',
                        day: 'MM-DD'
                    }
                }
            },
            y: {
                beginAtZero: false
            }
        }
    },
    
    // 颜色主题
    COLORS: {
        PRIMARY: '#007bff',
        SUCCESS: '#28a745',
        DANGER: '#dc3545',
        WARNING: '#ffc107',
        INFO: '#17a2b8',
        BTC: '#f7931a',
        ETH: '#627eea'
    }
};