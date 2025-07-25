// 比特币页面JavaScript

// 全局变量
let currentTimeframe = 'hour';
let priceChart = null;
let volumeChart = null;
let volatilityChart = null;
let previousBtcPrice = null; // 存储上一次的BTC价格
let priceUpdateInterval = null; // 价格更新定时器

// 计算曲线与平均值的交点并创建分段数据
function calculateIntersectionSegments(data, averagePrice) {
    const aboveAverage = [];
    const belowAverage = [];
    
    for (let i = 0; i < data.length; i++) {
        const currentPoint = data[i];
        const currentY = currentPoint.y;
        
        // 添加当前点到相应的数组
        if (currentY >= averagePrice) {
            aboveAverage.push(currentPoint);
            belowAverage.push({...currentPoint, y: null}); // 添加null值以断开线段
        } else {
            belowAverage.push(currentPoint);
            aboveAverage.push({...currentPoint, y: null}); // 添加null值以断开线段
        }
        
        // 检查是否与下一个点之间有交点
        if (i < data.length - 1) {
            const nextPoint = data[i + 1];
            const nextY = nextPoint.y;
            
            // 检查是否跨越平均线
            if ((currentY >= averagePrice && nextY < averagePrice) || 
                (currentY < averagePrice && nextY >= averagePrice)) {
                
                // 计算交点
                const intersection = calculateLineIntersection(
                    currentPoint.x, currentY,
                    nextPoint.x, nextY,
                    averagePrice
                );
                
                // 将交点添加到两个数组中
                aboveAverage.push(intersection);
                belowAverage.push(intersection);
            }
        }
    }
    
    return {
        aboveAverage: aboveAverage,
        belowAverage: belowAverage
    };
}

// 计算两点之间与水平线的交点
function calculateLineIntersection(x1, y1, x2, y2, horizontalY) {
    // 如果两点的y值相同，没有交点
    if (y1 === y2) {
        return null;
    }
    
    // 计算交点的x坐标
    const t = (horizontalY - y1) / (y2 - y1);
    const intersectionX = x1 + t * (x2 - x1);
    
    return {
        x: intersectionX,
        y: horizontalY
    };
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    console.log('比特币页面加载完成');
    initializePage();
    
    // 启动实时价格更新
    startRealTimePriceUpdates();
});

// 启动实时价格更新
function startRealTimePriceUpdates() {
    // 清除现有的定时器
    if (priceUpdateInterval) {
        clearInterval(priceUpdateInterval);
    }
    
    // 设置每5秒更新一次价格
    priceUpdateInterval = setInterval(() => {
        loadBitcoinPrice();
    }, 5000);
}

// 停止实时价格更新
function stopRealTimePriceUpdates() {
    if (priceUpdateInterval) {
        clearInterval(priceUpdateInterval);
        priceUpdateInterval = null;
    }
}

// 初始化页面
function initializePage() {
    setStatus('正在初始化...', 'loading');
    loadBitcoinPrice();
    loadBitcoinCharts();
}

// 加载比特币当前价格
function loadBitcoinPrice() {
    fetch('/api/latest_prices')
        .then(response => {
            if (!response.ok) {
                throw new Error('网络响应不正常');
            }
            return response.json();
        })
        .then(response => {
            if (response.success && response.data) {
                displayBitcoinPrice(response.data);
            } else {
                throw new Error('获取数据失败');
            }
        })
        .catch(error => {
            console.error('获取比特币价格时出错:', error);
            setStatus('获取价格数据失败', 'error');
        });
}

// 显示比特币价格
function displayBitcoinPrice(data) {
    const btcPriceElement = document.getElementById('btcPrice');
    if (!btcPriceElement) return;
    
    // 查找BTC数据
    const btcData = data.find(item => item.symbol === 'BTC');
    
    if (btcData) {
        const currentPrice = parseFloat(btcData.price);
        const priceChange = parseFloat(btcData.change_24h);
        const changeClass = priceChange >= 0 ? 'positive' : 'negative';
        const changeIcon = priceChange >= 0 ? '📈' : '📉';
        
        // 检查价格是否发生变化
        let priceChangeDirection = '';
        if (previousBtcPrice !== null && previousBtcPrice !== currentPrice) {
            priceChangeDirection = currentPrice > previousBtcPrice ? 'price-up' : 'price-down';
            
            // 添加闪烁动画类
            btcPriceElement.classList.add('price-flash', priceChangeDirection);
            
            // 移除动画类
            setTimeout(() => {
                btcPriceElement.classList.remove('price-flash', 'price-up', 'price-down');
            }, 1000);
        }
        
        btcPriceElement.innerHTML = `
            <div class="current-price-display">
                <div class="price-value ${priceChangeDirection}">$${currentPrice.toLocaleString()}</div>
                <div class="price-change ${changeClass}">
                    ${changeIcon} ${Math.abs(priceChange).toFixed(2)}% (24h)
                </div>
                <div class="price-timestamp">
                    更新时间: ${btcData.timestamp}
                </div>
            </div>
        `;
        
        // 存储当前价格
        previousBtcPrice = currentPrice;
    } else {
        btcPriceElement.innerHTML = '<div class="error-message">未找到比特币价格数据</div>';
    }
}

// 加载比特币图表数据
function loadBitcoinCharts() {
    setStatus('正在加载图表数据...', 'loading');
    
    fetch(`/api/btc_data?timeframe=${currentTimeframe}&limit=100`)
        .then(response => {
            if (!response.ok) {
                throw new Error('网络响应不正常');
            }
            return response.json();
        })
        .then(response => {
            if (response.success && response.data) {
                displayBitcoinCharts(response.data);
                setStatus('数据加载完成', 'info');
                updateLastUpdated();
            } else {
                throw new Error('获取数据失败');
            }
        })
        .catch(error => {
            console.error('获取比特币图表数据时出错:', error);
            setStatus('获取图表数据失败', 'error');
        });
}

// 显示比特币图表
function displayBitcoinCharts(data) {
    // 显示价格图表
    displayPriceChart(data.price_data);
    
    // 显示成交量图表
    displayVolumeChart(data.volume_data);
    
    // 显示波动率图表
    displayVolatilityChart(data.volatility_data);
}

// 显示价格图表
function displayPriceChart(priceData) {
    const ctx = document.getElementById('priceChart');
    if (!ctx) return;
    
    // 销毁现有图表
    if (priceChart) {
        priceChart.destroy();
    }
    
    // 准备数据
    const chartData = priceData.map(item => ({
        x: new Date(item.date).getTime(),
        y: item.price,
        o: item.open,
        h: item.high,
        l: item.low,
        c: item.price
    }));
    
    // 计算平均价格
    const prices = chartData.map(item => item.y);
    const averagePrice = prices.reduce((sum, price) => sum + price, 0) / prices.length;
    
    // 计算与平均值的交点并创建分段数据
    const segmentedData = calculateIntersectionSegments(chartData, averagePrice);
    
    // 创建渐变背景
    const gradient = ctx.getContext('2d').createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, 'rgba(247, 147, 26, 0.2)');
    gradient.addColorStop(1, 'rgba(255, 255, 255, 0.1)');
    
    // 创建价格图表
    priceChart = new Chart(ctx, {
        type: 'line',
        data: {
            datasets: [
                // 高于平均值的绿色线段
                {
                    label: 'BTC 价格 (高于平均)',
                    data: segmentedData.aboveAverage,
                    borderColor: '#22c55e',
                    backgroundColor: 'transparent',
                    tension: 0.1,
                    pointRadius: 0,
                    pointHitRadius: 10,
                    borderWidth: 3,
                    fill: false,
                    spanGaps: false
                },
                // 低于平均值的红色线段
                {
                    label: 'BTC 价格 (低于平均)',
                    data: segmentedData.belowAverage,
                    borderColor: '#ef4444',
                    backgroundColor: 'transparent',
                    tension: 0.1,
                    pointRadius: 0,
                    pointHitRadius: 10,
                    borderWidth: 3,
                    fill: false,
                    spanGaps: false
                }, {
                // 平均线
                label: '平均价格',
                data: chartData.map(item => ({
                    x: item.x,
                    y: averagePrice
                })),
                borderColor: '#e2e8f0',
                backgroundColor: 'transparent',
                borderDash: [3, 3],
                borderWidth: 2,
                pointRadius: 0,
                fill: false
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                intersect: true,
                mode: 'nearest'
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'right',
                    align: 'start',
                    labels: {
                        usePointStyle: true,
                        boxWidth: 8,
                        boxHeight: 8,
                        padding: 15,
                        font: {
                            size: 11,
                            weight: '400'
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(255, 255, 255, 0.95)',
                    titleColor: '#1a202c',
                    bodyColor: '#4a5568',
                    borderColor: '#e2e8f0',
                    borderWidth: 3,
                    cornerRadius: 8,
                    displayColors: true,
                    callbacks: {
                        label: function(context) {
                            if (context.parsed.y === null) return null;
                            const price = context.parsed.y;
                            const isAboveAverage = price >= averagePrice;
                            const status = isAboveAverage ? '↗ 高于平均' : '↘ 低于平均';
                            return [
                                `价格: $${price.toLocaleString()}`,
                                `${status} ($${averagePrice.toLocaleString()})`
                            ];
                        }
                    }
                }
            },
            scales: {
                x: {
                    type: 'time',
                    time: {
                        unit: getTimeUnit(currentTimeframe),
                        displayFormats: getDisplayFormats()
                    },
                    title: {
                        display: false,
                        text: '时间'
                    },
                    grid: {
                        display: false
                    },
                    border: {
                        display: false
                    },
                    ticks: {
                        display: true,
                        padding: 10,
                        color: '#94a3b8',
                        font: {
                            size: 10
                        }
                    }
                },
                y: {
                    title: {
                        display: false,
                        text: '价格 (USD)'
                    },
                    grid: {
                        display: false
                    },
                    border: {
                        display: false
                    },
                    ticks: {
                        display: true,
                        padding: 10,
                        color: '#94a3b8',
                        font: {
                            size: 10
                        },
                        callback: function(value) {
                            return '$' + value.toLocaleString();
                        }
                    }
                }
            }
        }
    });
}

// 显示成交量图表
function displayVolumeChart(volumeData) {
    const ctx = document.getElementById('volumeChart');
    if (!ctx) return;
    
    // 销毁现有图表
    if (volumeChart) {
        volumeChart.destroy();
    }
    
    // 准备数据
    const chartData = volumeData.map(item => ({
        x: new Date(item.date).getTime(),
        y: item.volume
    }));
    
    // 计算平均成交量
    const volumes = chartData.map(item => item.y);
    const averageVolume = volumes.reduce((sum, volume) => sum + volume, 0) / volumes.length;
    
    // 创建颜色数组，根据是否高于平均值决定颜色
    const barColors = volumes.map(volume => 
        volume >= averageVolume ? 'rgba(34, 197, 94, 0.7)' : 'rgba(239, 68, 68, 0.7)'
    );
    
    // 创建成交量图表
    volumeChart = new Chart(ctx, {
        type: 'bar',
        data: {
            datasets: [{
                label: 'BTC 成交量',
                data: chartData,
                backgroundColor: barColors,
                borderColor: barColors.map(color => color.replace('0.7', '1')),
                borderWidth: 2
            }, {
                // 平均线
                label: '平均成交量',
                data: chartData.map(item => ({
                    x: item.x,
                    y: averageVolume
                })),
                type: 'line',
                borderColor: '#e2e8f0',
                backgroundColor: 'transparent',
                borderDash: [3, 3],
                borderWidth: 2,
                pointRadius: 0,
                fill: false
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                intersect: true,
                mode: 'nearest'
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'right',
                    align: 'start',
                    labels: {
                        usePointStyle: true,
                        boxWidth: 8,
                        boxHeight: 8,
                        padding: 15,
                        font: {
                            size: 11,
                            weight: '400'
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(255, 255, 255, 0.95)',
                    titleColor: '#1a202c',
                    bodyColor: '#4a5568',
                    borderColor: '#e2e8f0',
                    borderWidth: 1,
                    cornerRadius: 8,
                    displayColors: true,
                    callbacks: {
                        label: function(context) {
                            const volume = context.parsed.y;
                            const isAboveAverage = volume >= averageVolume;
                            const status = isAboveAverage ? '↗ 高于平均' : '↘ 低于平均';
                            return [
                                `成交量: ${volume.toLocaleString()}`,
                                `${status} (${averageVolume.toLocaleString()})`
                            ];
                        }
                    }
                }
            },
            scales: {
                x: {
                    type: 'time',
                    time: {
                        unit: getTimeUnit(currentTimeframe),
                        displayFormats: getDisplayFormats()
                    },
                    title: {
                        display: false,
                        text: '时间'
                    },
                    grid: {
                        display: false
                    },
                    border: {
                        display: false
                    },
                    ticks: {
                        display: true,
                        padding: 10,
                        color: '#94a3b8',
                        font: {
                            size: 10
                        }
                    }
                },
                y: {
                    title: {
                        display: false,
                        text: '成交量'
                    },
                    grid: {
                        display: false
                    },
                    border: {
                        display: false
                    },
                    ticks: {
                        display: true,
                        padding: 10,
                        color: '#94a3b8',
                        font: {
                            size: 10
                        },
                        callback: function(value) {
                            return value.toLocaleString();
                        }
                    }
                }
            }
        }
    });
}

// 显示波动率图表
function displayVolatilityChart(volatilityData) {
    const ctx = document.getElementById('volatilityChart');
    if (!ctx) return;
    
    // 销毁现有图表
    if (volatilityChart) {
        volatilityChart.destroy();
    }
    
    // 准备数据
    const chartData = volatilityData.map(item => ({
        x: new Date(item.date).getTime(),
        y: item.volatility_percent
    }));
    
    // 计算平均波动率
    const volatilities = chartData.map(item => item.y);
    const averageVolatility = volatilities.reduce((sum, vol) => sum + vol, 0) / volatilities.length;
    
    // 使用交点算法计算分段数据
    const segments = calculateIntersectionSegments(chartData, averageVolatility);
    
    // 创建波动率图表
    volatilityChart = new Chart(ctx, {
        type: 'line',
        data: {
            datasets: [{
                label: 'BTC 波动率 (高于平均)',
                data: segments.aboveAverage,
                borderColor: '#ef4444',
                backgroundColor: 'transparent',
                tension: 0.1,
                pointRadius: 0,
                pointHitRadius: 10,
                fill: false,
                borderWidth: 3
            }, {
                label: 'BTC 波动率 (低于平均)',
                data: segments.belowAverage,
                borderColor: '#22c55e',
                backgroundColor: 'transparent',
                tension: 0.1,
                pointRadius: 0,
                pointHitRadius: 10,
                fill: false,
                borderWidth: 3
            }, {
                // 平均线
                label: '平均波动率',
                data: chartData.map(item => ({
                    x: item.x,
                    y: averageVolatility
                })),
                borderColor: '#e2e8f0',
                backgroundColor: 'transparent',
                borderDash: [3, 3],
                borderWidth: 1,
                pointRadius: 0,
                fill: false
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                intersect: true,
                mode: 'nearest'
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'right',
                    align: 'start',
                    labels: {
                        usePointStyle: true,
                        boxWidth: 8,
                        boxHeight: 8,
                        padding: 15,
                        font: {
                            size: 11,
                            weight: '400'
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(255, 255, 255, 0.95)',
                    titleColor: '#1a202c',
                    bodyColor: '#4a5568',
                    borderColor: '#e2e8f0',
                    borderWidth: 1,
                    cornerRadius: 8,
                    displayColors: true,
                    callbacks: {
                        label: function(context) {
                            if (context.parsed.y === null) return null;
                            
                            const volatility = context.parsed.y;
                            const isAboveAverage = volatility >= averageVolatility;
                            const status = isAboveAverage ? '↗ 高波动' : '↘ 低波动';
                            return [
                                `波动率: ${volatility.toFixed(2)}%`,
                                `${status} (${averageVolatility.toFixed(2)}%)`
                            ];
                        }
                    }
                }
            },
            scales: {
                x: {
                    type: 'time',
                    time: {
                        unit: getTimeUnit(currentTimeframe),
                        displayFormats: getDisplayFormats()
                    },
                    title: {
                        display: false,
                        text: '时间'
                    },
                    grid: {
                        display: false
                    },
                    border: {
                        display: false
                    },
                    ticks: {
                        display: true,
                        padding: 10,
                        color: '#94a3b8',
                        font: {
                            size: 10
                        }
                    }
                },
                y: {
                    title: {
                        display: false,
                        text: '波动率 (%)'
                    },
                    grid: {
                        display: false
                    },
                    border: {
                        display: false
                    },
                    ticks: {
                        display: true,
                        padding: 10,
                        color: '#94a3b8',
                        font: {
                            size: 10
                        },
                        callback: function(value) {
                            return value.toFixed(2) + '%';
                        }
                    }
                }
            }
        }
    });
}

// 切换时间粒度
function changeTimeframe(timeframe) {
    currentTimeframe = timeframe;
    
    // 更新按钮状态
    document.querySelectorAll('.timeframe-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.getAttribute('data-timeframe') === timeframe) {
            btn.classList.add('active');
        }
    });
    
    // 重新加载图表
    loadBitcoinCharts();
}

// 刷新所有数据
function refreshData() {
    setStatus('正在刷新数据...', 'loading');
    loadBitcoinPrice();
    loadBitcoinCharts();
}

// 获取时间单位
function getTimeUnit(timeframe) {
    switch(timeframe) {
        case 'minute': return 'minute';
        case 'hour': return 'hour';
        case 'day': return 'day';
        default: return 'hour';
    }
}

// 获取显示格式
function getDisplayFormats() {
    return {
        minute: 'HH:mm',
        hour: 'MM-dd HH:mm',
        day: 'yyyy-MM-dd'
    };
}

// 更新最后更新时间
function updateLastUpdated() {
    const lastUpdate = document.getElementById('lastUpdate');
    if (lastUpdate) {
        const now = new Date();
        lastUpdate.textContent = now.toLocaleTimeString();
    }
}

// 设置状态
function setStatus(message, type = 'info') {
    const indicator = document.getElementById('statusIndicator');
    const statusText = document.getElementById('statusText');
    
    if (!indicator || !statusText) return;
    
    // 清除所有状态类
    indicator.classList.remove('loading', 'error');
    
    // 设置新状态
    statusText.textContent = message;
    
    if (type === 'loading') {
        indicator.classList.add('loading');
    } else if (type === 'error') {
        indicator.classList.add('error');
    }
}