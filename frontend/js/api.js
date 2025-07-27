// API服务类
class APIService {
    constructor() {
        this.baseURL = API_CONFIG.BASE_URL;
        this.endpoints = API_CONFIG.ENDPOINTS;
        this.requestConfig = API_CONFIG.REQUEST_CONFIG;
    }

    /**
     * 发送HTTP请求
     * @param {string} url - 请求URL
     * @param {object} options - 请求选项
     * @returns {Promise} 响应数据
     */
    async request(url, options = {}) {
        const config = {
            ...this.requestConfig,
            ...options
        };

        try {
            const response = await fetch(url, config);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('API请求失败:', error);
            throw error;
        }
    }

    /**
     * GET请求
     * @param {string} endpoint - API端点
     * @param {object} params - 查询参数
     * @returns {Promise} 响应数据
     */
    async get(endpoint, params = {}) {
        let url;
        
        // 如果baseURL为空，使用相对路径
        if (!this.baseURL) {
            url = new URL(endpoint, window.location.origin);
        } else {
            url = new URL(this.baseURL + endpoint);
        }
        
        // 添加查询参数
        Object.keys(params).forEach(key => {
            if (params[key] !== undefined && params[key] !== null) {
                url.searchParams.append(key, params[key]);
            }
        });

        return this.request(url.toString(), {
            method: 'GET'
        });
    }

    /**
     * POST请求
     * @param {string} endpoint - API端点
     * @param {object} data - 请求数据
     * @returns {Promise} 响应数据
     */
    async post(endpoint, data = {}) {
        const url = this.baseURL ? this.baseURL + endpoint : endpoint;
        return this.request(url, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    /**
     * 健康检查
     * @returns {Promise} 健康状态
     */
    async healthCheck() {
        return this.get(this.endpoints.HEALTH);
    }

    /**
     * 获取最新价格
     * @returns {Promise} 价格数据
     */
    async getLatestPrices() {
        return this.get(this.endpoints.LATEST_PRICES);
    }

    /**
     * 获取价格历史
     * @param {string} symbol - 币种符号
     * @param {string} timeframe - 时间框架
     * @param {number} limit - 数据条数
     * @returns {Promise} 历史价格数据
     */
    async getPriceHistory(symbol = 'BTC', timeframe = 'hour', limit = 100) {
        return this.get(this.endpoints.PRICE_HISTORY, {
            symbol,
            timeframe,
            limit
        });
    }

    /**
     * 获取BTC图表数据
     * @param {string} timeframe - 时间框架
     * @returns {Promise} BTC图表数据
     */
    async getBTCChartData(timeframe = 'hour') {
        return this.get(this.endpoints.CHART_DATA_BTC, { timeframe });
    }

    /**
     * 获取ETH图表数据
     * @param {string} timeframe - 时间框架
     * @returns {Promise} ETH图表数据
     */
    async getETHChartData(timeframe = 'hour') {
        return this.get(this.endpoints.CHART_DATA_ETH, { timeframe });
    }

    /**
     * 获取K线数据
     * @param {string} symbol - 币种符号
     * @param {string} timeframe - 时间框架
     * @returns {Promise} K线数据
     */
    async getKlineChartData(symbol = 'BTC', timeframe = 'hour') {
        return this.get(this.endpoints.CHART_DATA_KLINE, {
            symbol,
            timeframe
        });
    }

    /**
     * 获取分析报告
     * @param {string} symbol - 币种符号
     * @returns {Promise} 分析报告
     */
    async getAnalysisReport(symbol = 'BTC') {
        return this.get(this.endpoints.ANALYSIS_REPORT, { symbol });
    }

    /**
     * 获取缓存状态
     * @returns {Promise} 缓存状态
     */
    async getCacheStatus() {
        return this.get(this.endpoints.CACHE_STATUS);
    }

    /**
     * 清除缓存
     * @returns {Promise} 清除结果
     */
    async clearCache() {
        return this.post(this.endpoints.CACHE_CLEAR);
    }

    /**
     * 获取系统状态
     * @returns {Promise} 系统状态
     */
    async getSystemStatus() {
        return this.get(this.endpoints.SYSTEM_STATUS);
    }

    /**
     * 获取图表数据（通用方法）
     * @param {string} crypto - 加密货币类型
     * @param {string} timeframe - 时间框架
     * @returns {Promise} 图表数据
     */
    async getChartData(crypto = 'BTC', timeframe = 'hour') {
        if (crypto.toLowerCase() === 'btc') {
            return this.getBTCChartData(timeframe);
        } else if (crypto.toLowerCase() === 'eth') {
            return this.getETHChartData(timeframe);
        } else {
            return this.getKlineChartData(crypto, timeframe);
        }
    }
}

// 创建API服务实例
const apiService = new APIService();

// 错误处理工具
class ErrorHandler {
    handle(error, context = '') {
        console.error(`${context}错误:`, error);
        
        // 显示用户友好的错误信息
        let message = '操作失败，请稍后重试';
        
        if (error.message.includes('Failed to fetch')) {
            message = '网络连接失败，请检查网络连接';
        } else if (error.message.includes('HTTP 404')) {
            message = '请求的资源不存在';
        } else if (error.message.includes('HTTP 500')) {
            message = '服务器内部错误';
        }
        
        this.showError(message);
    }

    showError(message) {
        // 创建错误提示
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-toast';
        errorDiv.textContent = message;
        
        // 添加样式
        errorDiv.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #dc3545;
            color: white;
            padding: 12px 20px;
            border-radius: 4px;
            z-index: 9999;
            animation: slideIn 0.3s ease-out;
        `;
        
        document.body.appendChild(errorDiv);
        
        // 3秒后自动移除
        setTimeout(() => {
            if (errorDiv.parentNode) {
                errorDiv.parentNode.removeChild(errorDiv);
            }
        }, 3000);
    }

    showSuccess(message) {
        // 创建成功提示
        const successDiv = document.createElement('div');
        successDiv.className = 'success-toast';
        successDiv.textContent = message;
        
        // 添加样式
        successDiv.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #28a745;
            color: white;
            padding: 12px 20px;
            border-radius: 4px;
            z-index: 9999;
            animation: slideIn 0.3s ease-out;
        `;
        
        document.body.appendChild(successDiv);
        
        // 3秒后自动移除
        setTimeout(() => {
            if (successDiv.parentNode) {
                successDiv.parentNode.removeChild(successDiv);
            }
        }, 3000);
    }
}

// 添加CSS动画
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
`;
document.head.appendChild(style);