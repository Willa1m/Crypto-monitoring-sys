// 图表管理类
class ChartManager {
    constructor() {
        this.charts = {};
        this.currentCrypto = APP_CONFIG.DEFAULT_CRYPTO;
        this.currentTimeframe = APP_CONFIG.DEFAULT_TIMEFRAME;
    }

    /**
     * 初始化主图表
     */
    initMainChart() {
        const ctx = document.getElementById('priceChart');
        if (!ctx) return;

        this.charts.main = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: '价格',
                    data: [],
                    borderColor: APP_CONFIG.COLORS.PRIMARY,
                    backgroundColor: APP_CONFIG.COLORS.PRIMARY + '20',
                    tension: 0.1,
                    fill: true
                }]
            },
            options: {
                ...APP_CONFIG.CHART_CONFIG,
                plugins: {
                    title: {
                        display: true,
                        text: `${this.currentCrypto} 价格走势`
                    },
                    legend: {
                        display: true
                    }
                }
            }
        });
    }

    /**
     * 初始化BTC详情图表
     */
    initBTCChart() {
        const ctx = document.getElementById('btcChart');
        if (!ctx) return;

        this.charts.btc = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'BTC价格',
                    data: [],
                    borderColor: APP_CONFIG.COLORS.BTC,
                    backgroundColor: APP_CONFIG.COLORS.BTC + '20',
                    tension: 0.1,
                    fill: true
                }]
            },
            options: {
                ...APP_CONFIG.CHART_CONFIG,
                plugins: {
                    title: {
                        display: true,
                        text: '比特币价格走势'
                    }
                }
            }
        });
    }

    /**
     * 初始化ETH详情图表
     */
    initETHChart() {
        const ctx = document.getElementById('ethChart');
        if (!ctx) return;

        this.charts.eth = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'ETH价格',
                    data: [],
                    borderColor: APP_CONFIG.COLORS.ETH,
                    backgroundColor: APP_CONFIG.COLORS.ETH + '20',
                    tension: 0.1,
                    fill: true
                }]
            },
            options: {
                ...APP_CONFIG.CHART_CONFIG,
                plugins: {
                    title: {
                        display: true,
                        text: '以太坊价格走势'
                    }
                }
            }
        });
    }

    /**
     * 初始化K线图表
     */
    initKlineChart() {
        const ctx = document.getElementById('klineChart');
        if (!ctx) return;

        this.charts.kline = new Chart(ctx, {
            type: 'candlestick',
            data: {
                datasets: [{
                    label: 'K线',
                    data: []
                }]
            },
            options: {
                ...APP_CONFIG.CHART_CONFIG,
                plugins: {
                    title: {
                        display: true,
                        text: 'K线图分析'
                    }
                }
            }
        });
    }

    /**
     * 更新主图表数据
     * @param {Array} data - 图表数据
     */
    updateMainChart(data) {
        if (!this.charts.main || !data || !data.price_data) return;

        const chart = this.charts.main;
        const priceData = data.price_data;

        // 更新数据
        chart.data.labels = priceData.map(item => new Date(item.date));
        chart.data.datasets[0].data = priceData.map(item => item.price);
        chart.data.datasets[0].label = `${this.currentCrypto} 价格`;
        
        // 更新颜色
        const color = this.currentCrypto === 'BTC' ? APP_CONFIG.COLORS.BTC : APP_CONFIG.COLORS.ETH;
        chart.data.datasets[0].borderColor = color;
        chart.data.datasets[0].backgroundColor = color + '20';

        // 更新标题
        chart.options.plugins.title.text = `${this.currentCrypto} 价格走势 (${this.currentTimeframe})`;

        chart.update();
    }

    /**
     * 更新BTC图表数据
     * @param {Array} data - 图表数据
     */
    updateBTCChart(data) {
        if (!this.charts.btc || !data || !data.price_data) return;

        const chart = this.charts.btc;
        const priceData = data.price_data;

        chart.data.labels = priceData.map(item => new Date(item.date));
        chart.data.datasets[0].data = priceData.map(item => item.price);

        chart.update();
    }

    /**
     * 更新ETH图表数据
     * @param {Array} data - 图表数据
     */
    updateETHChart(data) {
        if (!this.charts.eth || !data || !data.price_data) return;

        const chart = this.charts.eth;
        const priceData = data.price_data;

        chart.data.labels = priceData.map(item => new Date(item.date));
        chart.data.datasets[0].data = priceData.map(item => item.price);

        chart.update();
    }

    /**
     * 更新K线图表数据
     * @param {Array} data - K线数据
     */
    updateKlineChart(data) {
        if (!this.charts.kline || !data) return;

        const chart = this.charts.kline;
        
        // K线数据格式转换
        const klineData = data.map(item => ({
            x: new Date(item.date),
            o: item.open,
            h: item.high,
            l: item.low,
            c: item.close
        }));

        chart.data.datasets[0].data = klineData;
        chart.update();
    }

    /**
     * 显示加载状态
     * @param {string} chartId - 图表ID
     */
    showLoading(chartId) {
        const loadingElement = document.getElementById(`${chartId}Loading`);
        if (loadingElement) {
            loadingElement.style.display = 'block';
        }
    }

    /**
     * 隐藏加载状态
     * @param {string} chartId - 图表ID
     */
    hideLoading(chartId) {
        const loadingElement = document.getElementById(`${chartId}Loading`);
        if (loadingElement) {
            loadingElement.style.display = 'none';
        }
    }

    /**
     * 销毁图表
     * @param {string} chartName - 图表名称
     */
    destroyChart(chartName) {
        if (this.charts[chartName]) {
            this.charts[chartName].destroy();
            delete this.charts[chartName];
        }
    }

    /**
     * 销毁所有图表
     */
    destroyAllCharts() {
        Object.keys(this.charts).forEach(chartName => {
            this.destroyChart(chartName);
        });
    }

    /**
     * 设置当前加密货币
     * @param {string} crypto - 加密货币符号
     */
    setCurrentCrypto(crypto) {
        this.currentCrypto = crypto;
    }

    /**
     * 设置当前时间框架
     * @param {string} timeframe - 时间框架
     */
    setCurrentTimeframe(timeframe) {
        this.currentTimeframe = timeframe;
    }
}

// 创建图表管理器实例
const chartManager = new ChartManager();