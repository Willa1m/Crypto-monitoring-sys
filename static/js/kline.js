// K线图页面JavaScript - 基于ECharts实现
let currentSymbol = 'BTC';
let currentTimeframe = 'hour';
let klineChart = null;
let rsiChart = null;
let macdChart = null;
let isFullscreen = false;

// 初始化页面
document.addEventListener('DOMContentLoaded', function() {
    console.log('K线图页面初始化');
    initializeCharts();
    loadKlineData();
    
    // 每30秒自动刷新数据
    setInterval(loadKlineData, 30000);
});

// 初始化图表
function initializeCharts() {
    // 初始化K线主图
    klineChart = echarts.init(document.getElementById('klineChart'));
    
    // 初始化RSI指标图
    rsiChart = echarts.init(document.getElementById('rsiChart'));
    
    // 初始化MACD指标图
    macdChart = echarts.init(document.getElementById('macdChart'));
    
    // 监听窗口大小变化
    window.addEventListener('resize', function() {
        klineChart && klineChart.resize();
        rsiChart && rsiChart.resize();
        macdChart && macdChart.resize();
    });
}

// 加载K线数据
async function loadKlineData() {
    try {
        showLoading(true);
        
        const response = await fetch(`/api/kline_data?symbol=${currentSymbol}&timeframe=${currentTimeframe}&limit=100`);
        const result = await response.json();
        
        if (result.success && result.data) {
            updateCharts(result.data);
            updateIndicators(result.data.indicators);
            updatePriceInfo(result.data.kline);
        } else {
            console.error('获取K线数据失败:', result.error);
            showError('获取K线数据失败: ' + (result.error || '未知错误'));
        }
    } catch (error) {
        console.error('加载K线数据时出错:', error);
        showError('网络错误，请检查连接');
    } finally {
        showLoading(false);
    }
}

// 更新图表
function updateCharts(data) {
    if (!data.kline || !Array.isArray(data.kline)) {
        console.warn('K线数据格式不正确');
        return;
    }
    
    // 处理K线数据
    const klineData = data.kline.map(item => [
        item[0], // 时间戳
        item[1], // 开盘价
        item[4], // 收盘价
        item[3], // 最低价
        item[2], // 最高价
        item[5]  // 成交量
    ]);
    
    // 处理时间轴数据
    const timeData = data.kline.map(item => new Date(item[0]));
    
    // 处理MA数据
    const ma5Data = data.indicators.ma5.map((value, index) => 
        value !== null ? [timeData[index], value] : null
    ).filter(item => item !== null);
    
    const ma10Data = data.indicators.ma10.map((value, index) => 
        value !== null ? [timeData[index], value] : null
    ).filter(item => item !== null);
    
    const ma20Data = data.indicators.ma20.map((value, index) => 
        value !== null ? [timeData[index], value] : null
    ).filter(item => item !== null);
    
    // 处理布林带数据
    const bollingerUpper = data.indicators.bollinger.upper.map((value, index) => 
        value !== null ? [timeData[index], value] : null
    ).filter(item => item !== null);
    
    const bollingerLower = data.indicators.bollinger.lower.map((value, index) => 
        value !== null ? [timeData[index], value] : null
    ).filter(item => item !== null);
    
    // 更新K线主图
    updateKlineChart(timeData, klineData, ma5Data, ma10Data, ma20Data, bollingerUpper, bollingerLower);
    
    // 更新RSI图
    updateRSIChart(timeData, data.indicators.rsi);
    
    // 更新MACD图
    updateMACDChart(timeData, data.indicators);
}

// 更新K线主图
function updateKlineChart(timeData, klineData, ma5Data, ma10Data, ma20Data, bollingerUpper, bollingerLower) {
    const option = {
        title: {
            text: `${currentSymbol}/USDT K线图`,
            left: 'center',
            textStyle: {
                color: '#333',
                fontSize: 16
            }
        },
        tooltip: {
            trigger: 'axis',
            axisPointer: {
                type: 'cross'
            },
            backgroundColor: 'rgba(255, 255, 255, 0.95)',
            borderColor: '#ccc',
            borderWidth: 1,
            textStyle: {
                color: '#333'
            },
            formatter: function(params) {
                let result = params[0].axisValueLabel + '<br/>';
                params.forEach(param => {
                    if (param.seriesName === 'K线') {
                        const data = param.data;
                        result += `开盘: ${data[1]}<br/>`;
                        result += `收盘: ${data[2]}<br/>`;
                        result += `最低: ${data[3]}<br/>`;
                        result += `最高: ${data[4]}<br/>`;
                        result += `成交量: ${data[5]}<br/>`;
                    } else {
                        result += `${param.seriesName}: ${param.data[1]?.toFixed(2) || '--'}<br/>`;
                    }
                });
                return result;
            }
        },
        legend: {
            data: ['K线', 'MA5', 'MA10', 'MA20', '布林上轨', '布林下轨'],
            top: 30
        },
        grid: {
            left: '10%',
            right: '10%',
            bottom: '15%',
            top: '15%'
        },
        xAxis: {
            type: 'time',
            scale: true,
            boundaryGap: false,
            axisLine: { onZero: false },
            splitLine: { show: false },
            splitNumber: 20,
            min: 'dataMin',
            max: 'dataMax'
        },
        yAxis: {
            scale: true,
            splitArea: {
                show: true
            }
        },
        dataZoom: [
            {
                type: 'inside',
                start: 50,
                end: 100
            },
            {
                show: true,
                type: 'slider',
                top: '90%',
                start: 50,
                end: 100
            }
        ],
        series: [
            {
                name: 'K线',
                type: 'candlestick',
                data: klineData,
                itemStyle: {
                    color: '#00da3c',
                    color0: '#ec0000',
                    borderColor: '#00da3c',
                    borderColor0: '#ec0000'
                }
            },
            {
                name: 'MA5',
                type: 'line',
                data: ma5Data,
                smooth: true,
                lineStyle: {
                    opacity: 0.8,
                    width: 2,
                    color: '#FFD700'
                },
                symbol: 'none'
            },
            {
                name: 'MA10',
                type: 'line',
                data: ma10Data,
                smooth: true,
                lineStyle: {
                    opacity: 0.8,
                    width: 2,
                    color: '#1f77b4'
                },
                symbol: 'none'
            },
            {
                name: 'MA20',
                type: 'line',
                data: ma20Data,
                smooth: true,
                lineStyle: {
                    opacity: 0.8,
                    width: 2,
                    color: '#ff7f0e'
                },
                symbol: 'none'
            },
            {
                name: '布林上轨',
                type: 'line',
                data: bollingerUpper,
                smooth: true,
                lineStyle: {
                    opacity: 0.6,
                    width: 1,
                    color: '#d62728',
                    type: 'dashed'
                },
                symbol: 'none'
            },
            {
                name: '布林下轨',
                type: 'line',
                data: bollingerLower,
                smooth: true,
                lineStyle: {
                    opacity: 0.6,
                    width: 1,
                    color: '#d62728',
                    type: 'dashed'
                },
                symbol: 'none'
            }
        ]
    };
    
    klineChart.setOption(option, true);
}

// 更新RSI图
function updateRSIChart(timeData, rsiData) {
    const rsiSeriesData = rsiData.map((value, index) => 
        value !== null ? [timeData[index], value] : null
    ).filter(item => item !== null);
    
    const option = {
        title: {
            text: 'RSI (相对强弱指数)',
            left: 'center',
            textStyle: {
                fontSize: 14,
                color: '#666'
            }
        },
        tooltip: {
            trigger: 'axis',
            formatter: function(params) {
                return params[0].axisValueLabel + '<br/>RSI: ' + (params[0].data[1]?.toFixed(2) || '--');
            }
        },
        grid: {
            left: '10%',
            right: '10%',
            bottom: '15%',
            top: '25%'
        },
        xAxis: {
            type: 'time',
            scale: true,
            boundaryGap: false,
            axisLine: { onZero: false },
            splitLine: { show: false }
        },
        yAxis: {
            scale: true,
            min: 0,
            max: 100,
            splitLine: {
                show: true,
                lineStyle: {
                    color: ['#ccc'],
                    width: 1,
                    type: 'dashed'
                }
            }
        },
        series: [
            {
                name: 'RSI',
                type: 'line',
                data: rsiSeriesData,
                smooth: true,
                lineStyle: {
                    color: '#9c27b0',
                    width: 2
                },
                symbol: 'none',
                markLine: {
                    data: [
                        { yAxis: 70, lineStyle: { color: '#f44336', type: 'dashed' } },
                        { yAxis: 30, lineStyle: { color: '#4caf50', type: 'dashed' } }
                    ],
                    label: {
                        formatter: '{c}'
                    }
                }
            }
        ]
    };
    
    rsiChart.setOption(option, true);
}

// 更新MACD图
function updateMACDChart(timeData, indicators) {
    const macdLineData = indicators.macd_line.map((value, index) => 
        value !== null ? [timeData[index], value] : null
    ).filter(item => item !== null);
    
    const signalLineData = indicators.signal_line.map((value, index) => 
        value !== null ? [timeData[index], value] : null
    ).filter(item => item !== null);
    
    const macdHistData = indicators.macd_hist.map((value, index) => 
        value !== null ? [timeData[index], value] : null
    ).filter(item => item !== null);
    
    const option = {
        title: {
            text: 'MACD (指数平滑异同移动平均线)',
            left: 'center',        // 水平位置：'left', 'center', 'right' 或像素值如 '20px'
            top: '5px',           // 垂直位置：距离顶部的距离
            textStyle: {
                fontSize: 14,      // 字体大小
                color: '#666',     // 字体颜色
                fontWeight: 'bold'  // 字体粗细：'normal', 'bold', 'bolder', 'lighter'
            }
        },
        tooltip: {
            trigger: 'axis',
            formatter: function(params) {
                let result = params[0].axisValueLabel + '<br/>';
                params.forEach(param => {
                    result += `${param.seriesName}: ${param.data[1]?.toFixed(4) || '--'}<br/>`;
                });
                return result;
            }
        },
        legend: {
            data: ['MACD线', '信号线', 'MACD柱'],
            top: 25
        },
        grid: {
            left: '10%',
            right: '10%',
            bottom: '15%',
            top: '35%'
        },
        xAxis: {
            type: 'time',
            scale: true,
            boundaryGap: false,
            axisLine: { onZero: false },
            splitLine: { show: false }
        },
        yAxis: {
            scale: true,
            splitLine: {
                show: true,
                lineStyle: {
                    color: ['#ccc'],
                    width: 1,
                    type: 'dashed'
                }
            }
        },
        series: [
            {
                name: 'MACD线',
                type: 'line',
                data: macdLineData,
                smooth: true,
                lineStyle: {
                    color: '#2196f3',
                    width: 2
                },
                symbol: 'none'
            },
            {
                name: '信号线',
                type: 'line',
                data: signalLineData,
                smooth: true,
                lineStyle: {
                    color: '#ff9800',
                    width: 2
                },
                symbol: 'none'
            },
            {
                name: 'MACD柱',
                type: 'bar',
                data: macdHistData,
                itemStyle: {
                    color: function(params) {
                        return params.data[1] >= 0 ? '#4caf50' : '#f44336';
                    }
                }
            }
        ]
    };
    
    macdChart.setOption(option, true);
}

// 更新技术指标显示
function updateIndicators(indicators) {
    const latestIndex = indicators.ma5.length - 1;
    
    // 更新MA指标
    document.getElementById('ma5').textContent = 
        indicators.ma5[latestIndex]?.toFixed(2) || '--';
    document.getElementById('ma10').textContent = 
        indicators.ma10[latestIndex]?.toFixed(2) || '--';
    document.getElementById('ma20').textContent = 
        indicators.ma20[latestIndex]?.toFixed(2) || '--';
    
    // 更新RSI
    document.getElementById('rsi').textContent = 
        indicators.rsi[latestIndex]?.toFixed(2) || '--';
    
    // 更新MACD
    document.getElementById('macd').textContent = 
        indicators.macd_line[latestIndex]?.toFixed(4) || '--';
    
    // 更新波动率
    document.getElementById('volatility').textContent = 
        indicators.volatility[latestIndex]?.toFixed(2) + '%' || '--';
    
    // 更新布林带
    document.getElementById('bollingerUpper').textContent = 
        indicators.bollinger.upper[latestIndex]?.toFixed(2) || '--';
    document.getElementById('bollingerLower').textContent = 
        indicators.bollinger.lower[latestIndex]?.toFixed(2) || '--';
    
    // 更新KDJ
    document.getElementById('kdjK').textContent = 
        indicators.kdj.k[latestIndex]?.toFixed(2) || '--';
    document.getElementById('kdjD').textContent = 
        indicators.kdj.d[latestIndex]?.toFixed(2) || '--';
    document.getElementById('kdjJ').textContent = 
        indicators.kdj.j[latestIndex]?.toFixed(2) || '--';
}

// 更新价格信息
function updatePriceInfo(klineData) {
    if (!klineData || klineData.length === 0) return;
    
    const latest = klineData[klineData.length - 1];
    const previous = klineData.length > 1 ? klineData[klineData.length - 2] : latest;
    
    // 当前价格（收盘价）
    document.getElementById('currentPrice').textContent = latest[4].toFixed(2);
    
    // 开盘价
    document.getElementById('openPrice').textContent = latest[1].toFixed(2);
    
    // 最高价
    document.getElementById('highPrice').textContent = latest[2].toFixed(2);
    
    // 最低价
    document.getElementById('lowPrice').textContent = latest[3].toFixed(2);
    
    // 成交量
    document.getElementById('volume').textContent = latest[5].toFixed(2);
    
    // 24h涨跌
    const change = latest[4] - previous[4];
    const changePercent = (change / previous[4] * 100).toFixed(2);
    const changeElement = document.getElementById('change24h');
    changeElement.textContent = `${change >= 0 ? '+' : ''}${change.toFixed(2)} (${changePercent}%)`;
    changeElement.className = `price-info-value ${change >= 0 ? 'positive' : 'negative'}`;
}

// 切换加密货币
function switchCrypto(symbol) {
    currentSymbol = symbol;
    
    // 更新按钮状态
    document.querySelectorAll('.crypto-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    // 更新图表标题
    document.getElementById('chartSymbol').textContent = `${symbol}/USDT`;
    
    // 重新加载数据
    loadKlineData();
}

// 切换时间周期
function switchTimeframe(timeframe) {
    currentTimeframe = timeframe;
    
    // 更新按钮状态
    document.querySelectorAll('.timeframe-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    // 更新时间周期显示
    const timeframeMap = {
        'minute': '1分钟',
        'hour': '1小时',
        'day': '1天'
    };
    document.getElementById('chartTimeframe').textContent = timeframeMap[timeframe];
    
    // 重新加载数据
    loadKlineData();
}

// 显示/隐藏加载状态
function showLoading(show) {
    const loadingElement = document.getElementById('klineLoading');
    if (loadingElement) {
        loadingElement.style.display = show ? 'block' : 'none';
    }
}

// 显示错误信息
function showError(message) {
    console.error(message);
    // 可以在这里添加用户友好的错误提示
    alert(message);
}

// 刷新K线数据
function refreshKlineData() {
    console.log('手动刷新K线数据');
    loadKlineData();
}

// 全屏切换
function toggleFullscreen() {
    const container = document.querySelector('.charts-container');
    if (!isFullscreen) {
        if (container.requestFullscreen) {
            container.requestFullscreen();
        } else if (container.webkitRequestFullscreen) {
            container.webkitRequestFullscreen();
        } else if (container.msRequestFullscreen) {
            container.msRequestFullscreen();
        }
        isFullscreen = true;
    } else {
        if (document.exitFullscreen) {
            document.exitFullscreen();
        } else if (document.webkitExitFullscreen) {
            document.webkitExitFullscreen();
        } else if (document.msExitFullscreen) {
            document.msExitFullscreen();
        }
        isFullscreen = false;
    }
}

// 下载图表
function downloadChart() {
    if (klineChart) {
        const url = klineChart.getDataURL({
            pixelRatio: 2,
            backgroundColor: '#fff'
        });
        const link = document.createElement('a');
        link.download = `${currentSymbol}_${currentTimeframe}_kline.png`;
        link.href = url;
        link.click();
    }
}

// 重置缩放
function resetZoom() {
    if (klineChart) {
        klineChart.dispatchAction({
            type: 'dataZoom',
            start: 50,
            end: 100
        });
    }
}