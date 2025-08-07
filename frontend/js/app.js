// 主应用程序类
class CryptoApp {
    constructor() {
        this.apiService = new APIService();
        this.errorHandler = new ErrorHandler();
        this.chartManager = new ChartManager();
        this.currentPage = 'home';
        this.refreshInterval = null;
        this.isInitialized = false;
    }

    /**
     * 初始化应用程序
     */
    async init() {
        try {
            console.log('初始化加密货币监控应用...');
            
            // 检查API连接
            await this.checkAPIConnection();
            
            // 初始化页面
            this.initializePages();
            
            // 绑定事件
            this.bindEvents();
            
            // 加载初始数据
            await this.loadInitialData();
            
            // 启动自动刷新
            this.startAutoRefresh();
            
            this.isInitialized = true;
            console.log('应用程序初始化完成');
            
        } catch (error) {
            console.error('应用程序初始化失败:', error);
            this.errorHandler.showError('应用程序初始化失败，请检查网络连接');
        }
    }

    /**
     * 检查API连接
     */
    async checkAPIConnection() {
        try {
            const response = await this.apiService.healthCheck();
            if (response.status === 'healthy') {
                console.log('API连接正常');
                return true;
            }
        } catch (error) {
            console.error('API连接失败:', error);
            throw new Error('无法连接到后端服务');
        }
    }

    /**
     * 初始化页面
     */
    initializePages() {
        // 显示首页
        this.showPage('home');
        
        // 初始化图表
        this.chartManager.initMainChart();
    }

    /**
     * 绑定事件
     */
    bindEvents() {
        // 导航事件
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const page = e.target.getAttribute('data-page');
                this.showPage(page);
            });
        });

        // 刷新按钮事件
        const refreshBtn = document.getElementById('refreshBtn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.refreshData());
        }

        // 时间框架选择事件
        document.querySelectorAll('.timeframe-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const timeframe = e.target.getAttribute('data-timeframe');
                this.changeTimeframe(timeframe);
            });
        });

        // 加密货币选择事件
        document.querySelectorAll('.crypto-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const crypto = e.target.getAttribute('data-crypto');
                this.changeCrypto(crypto);
            });
        });
    }

    /**
     * 显示指定页面
     * @param {string} pageName - 页面名称
     */
    showPage(pageName) {
        // 隐藏所有页面
        document.querySelectorAll('.page').forEach(page => {
            page.style.display = 'none';
        });

        // 显示指定页面
        const targetPage = document.getElementById(`${pageName}Page`);
        if (targetPage) {
            targetPage.style.display = 'block';
            this.currentPage = pageName;
            
            // 更新导航状态
            this.updateNavigation(pageName);
            
            // 根据页面加载相应数据
            this.loadPageData(pageName);
        }
    }

    /**
     * 更新导航状态
     * @param {string} activePage - 当前活跃页面
     */
    updateNavigation(activePage) {
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('data-page') === activePage) {
                link.classList.add('active');
            }
        });
    }

    /**
     * 加载页面数据
     * @param {string} pageName - 页面名称
     */
    async loadPageData(pageName) {
        try {
            switch (pageName) {
                case 'home':
                    await this.loadHomeData();
                    break;
                case 'bitcoin':
                    await this.loadBitcoinData();
                    break;
                case 'ethereum':
                    await this.loadEthereumData();
                    break;
                case 'kline':
                    await this.loadKlineData();
                    break;
            }
        } catch (error) {
            console.error(`加载${pageName}页面数据失败:`, error);
            this.errorHandler.showError(`加载${pageName}页面数据失败`);
        }
    }

    /**
     * 加载首页数据
     */
    async loadHomeData() {
        try {
            // 加载最新价格
            const latestPrices = await this.apiService.getLatestPrices();
            this.updatePriceDisplay(latestPrices);

            // 加载主图表数据
            const chartData = await this.apiService.getChartData(
                this.chartManager.currentCrypto,
                this.chartManager.currentTimeframe
            );
            this.chartManager.updateMainChart(chartData);

        } catch (error) {
            console.error('加载首页数据失败:', error);
            throw error;
        }
    }

    /**
     * 加载比特币数据
     */
    async loadBitcoinData() {
        try {
            this.chartManager.initBTCChart();
            const btcData = await this.apiService.getBTCChartData();
            this.chartManager.updateBTCChart(btcData);
            
            // 加载BTC分析报告
            const analysis = await this.apiService.getAnalysisReport('BTC');
            this.updateAnalysisDisplay('bitcoin', analysis);
            
        } catch (error) {
            console.error('加载比特币数据失败:', error);
            throw error;
        }
    }

    /**
     * 加载以太坊数据
     */
    async loadEthereumData() {
        try {
            this.chartManager.initETHChart();
            const ethData = await this.apiService.getETHChartData();
            this.chartManager.updateETHChart(ethData);
            
            // 加载ETH分析报告
            const analysis = await this.apiService.getAnalysisReport('ETH');
            this.updateAnalysisDisplay('ethereum', analysis);
            
        } catch (error) {
            console.error('加载以太坊数据失败:', error);
            throw error;
        }
    }

    /**
     * 加载K线数据
     */
    async loadKlineData() {
        try {
            this.chartManager.initKlineChart();
            const klineData = await this.apiService.getKlineChartData();
            this.chartManager.updateKlineChart(klineData);
            
        } catch (error) {
            console.error('加载K线数据失败:', error);
            throw error;
        }
    }

    /**
     * 加载初始数据
     */
    async loadInitialData() {
        await this.loadHomeData();
    }

    /**
     * 更新价格显示
     * @param {Object} prices - 价格数据
     */
    updatePriceDisplay(prices) {
        if (!prices) return;

        // 更新BTC价格
        if (prices.BTC) {
            const btcPriceElement = document.getElementById('btcPrice');
            const btcChangeElement = document.getElementById('btcChange');
            
            if (btcPriceElement) {
                btcPriceElement.textContent = `$${prices.BTC.price.toLocaleString()}`;
            }
            
            if (btcChangeElement) {
                const change = prices.BTC.change_24h || 0;
                btcChangeElement.textContent = `${change >= 0 ? '+' : ''}${change.toFixed(2)}%`;
                btcChangeElement.className = `price-change ${change >= 0 ? 'positive' : 'negative'}`;
            }
        }

        // 更新ETH价格
        if (prices.ETH) {
            const ethPriceElement = document.getElementById('ethPrice');
            const ethChangeElement = document.getElementById('ethChange');
            
            if (ethPriceElement) {
                ethPriceElement.textContent = `$${prices.ETH.price.toLocaleString()}`;
            }
            
            if (ethChangeElement) {
                const change = prices.ETH.change_24h || 0;
                ethChangeElement.textContent = `${change >= 0 ? '+' : ''}${change.toFixed(2)}%`;
                ethChangeElement.className = `price-change ${change >= 0 ? 'positive' : 'negative'}`;
            }
        }

        // 更新最后更新时间
        const lastUpdateElement = document.getElementById('lastUpdate');
        if (lastUpdateElement) {
            lastUpdateElement.textContent = `最后更新: ${new Date().toLocaleTimeString()}`;
        }
    }

    /**
     * 更新分析显示
     * @param {string} page - 页面名称
     * @param {Object} analysis - 分析数据
     */
    updateAnalysisDisplay(page, analysis) {
        const analysisElement = document.getElementById(`${page}Analysis`);
        if (analysisElement && analysis) {
            analysisElement.innerHTML = `
                <h4>技术分析</h4>
                <p><strong>趋势:</strong> ${analysis.trend || '未知'}</p>
                <p><strong>支撑位:</strong> $${analysis.support || 'N/A'}</p>
                <p><strong>阻力位:</strong> $${analysis.resistance || 'N/A'}</p>
                <p><strong>建议:</strong> ${analysis.recommendation || '无'}</p>
            `;
        }
    }

    /**
     * 刷新数据
     */
    async refreshData() {
        try {
            const refreshBtn = document.getElementById('refreshBtn');
            if (refreshBtn) {
                refreshBtn.disabled = true;
                refreshBtn.textContent = '刷新中...';
            }

            await this.loadPageData(this.currentPage);
            this.errorHandler.showSuccess('数据刷新成功');

        } catch (error) {
            console.error('刷新数据失败:', error);
            this.errorHandler.showError('数据刷新失败');
        } finally {
            const refreshBtn = document.getElementById('refreshBtn');
            if (refreshBtn) {
                refreshBtn.disabled = false;
                refreshBtn.textContent = '刷新';
            }
        }
    }

    /**
     * 改变时间框架
     * @param {string} timeframe - 时间框架
     */
    async changeTimeframe(timeframe) {
        try {
            this.chartManager.setCurrentTimeframe(timeframe);
            
            // 更新按钮状态
            document.querySelectorAll('.timeframe-btn').forEach(btn => {
                btn.classList.remove('active');
                if (btn.getAttribute('data-timeframe') === timeframe) {
                    btn.classList.add('active');
                }
            });

            // 重新加载当前页面数据
            await this.loadPageData(this.currentPage);
            
        } catch (error) {
            console.error('改变时间框架失败:', error);
            this.errorHandler.showError('改变时间框架失败');
        }
    }

    /**
     * 改变加密货币
     * @param {string} crypto - 加密货币符号
     */
    async changeCrypto(crypto) {
        try {
            this.chartManager.setCurrentCrypto(crypto);
            
            // 更新按钮状态
            document.querySelectorAll('.crypto-btn').forEach(btn => {
                btn.classList.remove('active');
                if (btn.getAttribute('data-crypto') === crypto) {
                    btn.classList.add('active');
                }
            });

            // 重新加载主图表数据
            if (this.currentPage === 'home') {
                const chartData = await this.apiService.getChartData(crypto, this.chartManager.currentTimeframe);
                this.chartManager.updateMainChart(chartData);
            }
            
        } catch (error) {
            console.error('改变加密货币失败:', error);
            this.errorHandler.showError('改变加密货币失败');
        }
    }

    /**
     * 启动自动刷新
     */
    startAutoRefresh() {
        // 清除现有的定时器
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }

        // 设置新的定时器
        this.refreshInterval = setInterval(async () => {
            try {
                if (this.currentPage === 'home') {
                    const latestPrices = await this.apiService.getLatestPrices();
                    this.updatePriceDisplay(latestPrices);
                }
            } catch (error) {
                console.error('自动刷新失败:', error);
            }
        }, APP_CONFIG.REFRESH_INTERVAL);
    }

    /**
     * 停止自动刷新
     */
    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    }

    /**
     * 销毁应用程序
     */
    destroy() {
        this.stopAutoRefresh();
        this.chartManager.destroyAllCharts();
        this.isInitialized = false;
    }
}

// 应用程序入口
document.addEventListener('DOMContentLoaded', async () => {
    try {
        // 创建应用程序实例
        window.cryptoApp = new CryptoApp();
        
        // 初始化应用程序
        await window.cryptoApp.init();
        
    } catch (error) {
        console.error('应用程序启动失败:', error);
        
        // 显示错误信息
        const errorDiv = document.createElement('div');
        errorDiv.className = 'alert alert-danger';
        errorDiv.innerHTML = `
            <h4>应用程序启动失败</h4>
            <p>请检查网络连接和后端服务状态</p>
            <button onclick="location.reload()" class="btn btn-primary">重新加载</button>
        `;
        
        document.body.insertBefore(errorDiv, document.body.firstChild);
    }
});

// 页面卸载时清理资源
window.addEventListener('beforeunload', () => {
    if (window.cryptoApp) {
        window.cryptoApp.destroy();
    }
});