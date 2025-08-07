// 加密货币监控系统JavaScript

// 全局变量
let currentTimeframe = 'hour';
let currentSymbol = 'BTC';

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
let priceChart = null;
let previousPrices = {}; // 存储上一次的价格数据
let priceUpdateInterval = null; // 价格更新定时器
let lastUpdateTime = null;
let apiUsageInfo = null;

// 加载最新价格
function loadLatestPrices() {
    setStatus('正在获取最新价格...', 'loading');

    fetch('/api/latest_prices')
        .then(response => {
            if (!response.ok) {
                throw new Error('网络响应不正常');
            }
            return response.json();
        })
        .then(response => {
            if (response.success && response.data) {
                displayPrices(response.data);
                setStatus('价格数据已更新', 'info');
                updateLastUpdated();
            } else {
                throw new Error('获取数据失败');
            }
        })
        .catch(error => {
            console.error('获取价格数据时出错:', error);
            setStatus('获取价格数据失败', 'error');
        });
}

// 显示价格数据
function displayPrices(data) {
    const priceList = document.getElementById('priceList');
    if (!priceList) return;
    
    // 确保data是数组
    const priceData = Array.isArray(data) ? data : (data.data || []);
    
    // 获取每个symbol的最新价格（第一条记录）
    const latestPrices = {};
    priceData.forEach(item => {
        if (!latestPrices[item.symbol]) {
            latestPrices[item.symbol] = item;
        }
    });
    
    // 显示每个加密货币的最新价格
    Object.values(latestPrices).forEach(item => {
        const currentPrice = parseFloat(item.price);
        const priceChange = parseFloat(item.change_24h);
        const changeClass = priceChange >= 0 ? 'positive' : 'negative';
        const changeIcon = priceChange >= 0 ? '↑' : '↓';
        
        // 检查是否已存在该货币的价格项
        let priceItem = document.querySelector(`[data-symbol="${item.symbol}"]`);
        
        if (!priceItem) {
            // 创建新的价格项
            priceItem = document.createElement('div');
            priceItem.className = 'price-item';
            priceItem.setAttribute('data-symbol', item.symbol);
            priceList.appendChild(priceItem);
        }
        
        // 检查价格是否发生变化
        const previousPrice = previousPrices[item.symbol];
        let priceChangeDirection = '';
        
        if (previousPrice !== undefined && previousPrice !== currentPrice) {
            priceChangeDirection = currentPrice > previousPrice ? 'price-up' : 'price-down';
            
            // 添加闪烁动画类
            priceItem.classList.add('price-flash', priceChangeDirection);
            
            // 移除动画类
            setTimeout(() => {
                priceItem.classList.remove('price-flash', 'price-up', 'price-down');
            }, 1000);
        }
        
        // 更新价格项内容
        const iconPath = item.symbol === 'BTC' ? '/static/icons/bitcoin.svg' : '/static/icons/ethereum.svg';
        priceItem.innerHTML = `
            <div class="crypto-info">
                <img src="${iconPath}" alt="${item.symbol}" class="crypto-icon">
                <div>
                    <span class="crypto-symbol">${item.symbol}</span>
                    <span class="crypto-name">${item.name}</span>
                </div>
            </div>
            <div class="price-info">
                <div class="current-price ${priceChangeDirection}">$${currentPrice.toLocaleString()}</div>
                <div class="price-change ${changeClass}">
                    ${changeIcon} ${Math.abs(priceChange).toFixed(2)}%
                </div>
            </div>
        `;
        
        // 存储当前价格
        previousPrices[item.symbol] = currentPrice;
    });
}

// 加载图表
function loadChart(symbol = 'BTC') {
    setStatus('正在加载图表数据...', 'loading');
    
    fetch(`/api/chart_data?timeframe=${currentTimeframe}&symbol=${symbol}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('网络响应不正常');
            }
            return response.json();
        })
        .then(response => {
            if (response.success && response.data) {
                displayChart(response.data, symbol, currentTimeframe);
                setStatus('图表数据已更新', 'info');
                updateLastUpdated();
            } else {
                throw new Error('获取数据失败');
            }
        })
        .catch(error => {
            console.error('获取图表数据时出错:', error);
            setStatus('获取图表数据失败', 'error');
        });
}

// 显示图表
function displayChart(data, symbol = 'BTC', timeframe = 'hour') {
    const chartContainer = document.getElementById('chartContainer');
    const chartLoading = document.getElementById('chartLoading');
    
    if (!chartContainer) {
        console.error('图表容器未找到');
        return;
    }
    
    // 显示加载状态
    if (chartLoading) {
        chartLoading.style.display = 'block';
    }
    
    const canvas = document.getElementById('priceChart');
    if (!canvas) {
        console.error('图表canvas未找到');
        if (chartLoading) {
            chartLoading.textContent = '图表加载失败';
            chartLoading.style.color = '#e53e3e';
        }
        return;
    }
    
    // 检查数据
    if (!data || !Array.isArray(data) || data.length === 0) {
        console.error('图表数据为空或格式错误');
        if (chartLoading) {
            chartLoading.textContent = '暂无图表数据';
            chartLoading.style.color = '#718096';
        }
        return;
    }
    
    try {
        const ctx = canvas.getContext('2d');
        
        // 格式化数据并计算平均值
        const formattedData = data.map(item => ({
            x: new Date(item.date).getTime(),
            y: parseFloat(item.close) || 0
        }));
        
        // 计算平均价格
        const prices = formattedData.map(item => item.y);
        const averagePrice = prices.reduce((sum, price) => sum + price, 0) / prices.length;
        
        // 计算与平均值的交点并创建分段数据
        const segmentedData = calculateIntersectionSegments(formattedData, averagePrice);
        
        // 创建渐变背景 - 更白色的背景
        const gradient = ctx.createLinearGradient(0, 0, 0, 400);
        gradient.addColorStop(0, symbol === 'BTC' ? 'rgba(247, 147, 26, 0.1)' : 'rgba(98, 126, 234, 0.1)');
        gradient.addColorStop(1, 'rgba(255, 255, 255, 0)');
        
        // 配置图表
        const config = {
            type: 'line',
            data: {
                datasets: [
                    // 高于平均值的绿色线段
                    {
                        label: `${symbol} 价格 (高于平均)`,
                        data: segmentedData.aboveAverage,
                        borderColor: '#22c55e',
                        backgroundColor: 'transparent',
                        tension: 0.3,
                        pointRadius: 0,
                        pointHitRadius: 10,
                        borderWidth: 3,
                        fill: false,
                        spanGaps: false
                    },
                    // 低于平均值的红色线段
                    {
                        label: `${symbol} 价格 (低于平均)`,
                        data: segmentedData.belowAverage,
                        borderColor: '#ef4444',
                        backgroundColor: 'transparent',
                        tension: 0.3,
                        pointRadius: 0,
                        pointHitRadius: 10,
                        borderWidth: 3,
                        fill: false,
                        spanGaps: false
                    }, {
                    // 平均线
                    label: '平均价格',
                    data: formattedData.map(item => ({
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
                        position: 'top',
                        align: 'end',
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
                        type: 'linear',
                        title: {
                            display: false
                        },
                        grid: {
                            display: false,
                            drawBorder: false
                        },
                        border: {
                            display: false
                        },
                        ticks: {
                            display: true,
                            maxRotation: 0,
                            padding: 10,
                            color: '#94a3b8',
                            callback: function(value, index) {
                                // 只显示部分刻度标签
                                if (index % Math.ceil(data.length / 6) === 0) {
                                    const date = new Date(data[index]?.date || value);
                                    if (timeframe === 'minute') {
                                        return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
                                    } else if (timeframe === 'hour') {
                                        return date.toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' }) + ' ' + 
                                               date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
                                    } else {
                                        return date.toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' });
                                    }
                                }
                                return '';
                            }
                        }
                    },
                    y: {
                        title: {
                            display: false
                        },
                        grid: {
                            display: false,
                            drawBorder: false
                        },
                        border: {
                            display: false
                        },
                        ticks: {
                            display: true,
                            padding: 10,
                            color: '#94a3b8',
                            callback: function(value) {
                                return '$' + value.toLocaleString();
                            }
                        }
                    }
                }
            }
        };
        
        // 如果已存在图表，销毁它
        const existingChart = Chart.getChart(canvas);
        if (existingChart) {
            existingChart.destroy();
        }
        
        // 创建新图表
        window.priceChart = new Chart(ctx, config);
        
        // 隐藏加载状态
        if (chartLoading) {
            chartLoading.style.display = 'none';
        }
        
        // 显示图表统计信息
        displayChartStats(symbol, prices, averagePrice);
        
    } catch (error) {
        console.error('创建图表时出错:', error);
        if (chartLoading) {
            chartLoading.textContent = '图表创建失败';
            chartLoading.style.color = '#e53e3e';
            chartLoading.style.display = 'block';
        }
    }
}

// 显示图表统计信息
function displayChartStats(symbol, prices, averagePrice) {
    const currentPrice = prices[prices.length - 1];
    const priceChange = ((currentPrice - prices[0]) / prices[0] * 100);
    const isAboveAverage = currentPrice >= averagePrice;
    
    // 获取统计信息容器
    const statsContainer = document.getElementById('chartStats');
    if (!statsContainer) {
        console.warn('统计信息容器未找到，尝试初始化...');
        return;
    }
    
    // 保存旧的统计数据用于比较
    let oldStats = {
        currentPrice: NaN,
        averagePrice: NaN,
        trend: NaN
    };
    
    // 尝试获取旧的统计数据
    try {
        if (statsContainer.querySelector('.stats-item:nth-child(1) .stats-value')) {
            oldStats.currentPrice = parseFloat(statsContainer.querySelector('.stats-item:nth-child(1) .stats-value').textContent.replace('$', '').replace(/,/g, ''));
            oldStats.averagePrice = parseFloat(statsContainer.querySelector('.stats-item:nth-child(2) .stats-value').textContent.replace('$', '').replace(/,/g, ''));
            oldStats.trend = parseFloat(statsContainer.querySelector('.stats-item:nth-child(3) .stats-value').textContent.replace(/[^0-9.-]/g, ''));
        }
    } catch (error) {
        console.warn('获取旧统计数据失败，使用默认值');
    }
    
    // 更新统计信息
    statsContainer.innerHTML = `
        <div class="stats-item" id="currentPriceItem">
            <span class="stats-label">当前价格:</span>
            <span class="stats-value ${isAboveAverage ? 'positive' : 'negative'}">
                $${currentPrice.toLocaleString()}
            </span>
        </div>
        <div class="stats-item" id="averagePriceItem">
            <span class="stats-label">平均价格:</span>
            <span class="stats-value">$${averagePrice.toLocaleString()}</span>
        </div>
        <div class="stats-item" id="trendItem">
            <span class="stats-label">趋势:</span>
            <span class="stats-value ${priceChange >= 0 ? 'positive' : 'negative'}">
                ${priceChange >= 0 ? '↗' : '↘'} ${Math.abs(priceChange).toFixed(2)}%
            </span>
        </div>
    `;
    
    // 更新标题显示当前选择的加密货币
    const statsTitle = document.querySelector('.stats-title');
    if (statsTitle) {
        statsTitle.textContent = `${symbol === 'BTC' ? '比特币' : '以太坊'} (${currentTimeframe === 'minute' ? '分钟' : currentTimeframe === 'hour' ? '小时' : '天'}) 统计`;
    }
    
    // 添加闪动动画效果
    if (!isNaN(oldStats.currentPrice) && oldStats.currentPrice !== currentPrice) {
        const currentPriceItem = document.getElementById('currentPriceItem');
        if (currentPriceItem) {
            currentPriceItem.classList.add('flash');
            setTimeout(() => {
                currentPriceItem.classList.remove('flash');
            }, 1000);
        }
    }
    
    if (!isNaN(oldStats.averagePrice) && oldStats.averagePrice !== averagePrice) {
        const averagePriceItem = document.getElementById('averagePriceItem');
        if (averagePriceItem) {
            averagePriceItem.classList.add('flash');
            setTimeout(() => {
                averagePriceItem.classList.remove('flash');
            }, 1000);
        }
    }
    
    if (!isNaN(oldStats.trend) && oldStats.trend !== Math.abs(priceChange)) {
        const trendItem = document.getElementById('trendItem');
        if (trendItem) {
            trendItem.classList.add('flash');
            setTimeout(() => {
                trendItem.classList.remove('flash');
            }, 1000);
        }
    }
    
    // 更新统计容器的标题
    document.getElementById('chartStatsContainer').style.display = 'block';
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

// 刷新所有数据
function refreshData() {
    // 添加闪动效果到统计数据容器
    const statsContainer = document.getElementById('chartStats');
    if (statsContainer) {
        statsContainer.classList.add('flash-container');
        setTimeout(() => {
            statsContainer.classList.remove('flash-container');
        }, 1000);
    }
    
    loadLatestPrices();
    loadChart(currentSymbol);
}

// 切换加密货币
function changeCrypto(symbol) {
    currentSymbol = symbol;
    
    // 更新按钮状态
    document.querySelectorAll('.crypto-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.textContent.trim() === symbol) {
            btn.classList.add('active');
        }
    });
    
    // 添加闪动效果到统计数据容器
    const statsContainer = document.getElementById('chartStats');
    if (statsContainer) {
        statsContainer.classList.add('flash-container');
        setTimeout(() => {
            statsContainer.classList.remove('flash-container');
        }, 1000);
    }
    
    // 重新加载图表
    loadChart(symbol);
}

// 切换时间范围
function changeTimeframe(timeframe) {
    if (timeframe === currentTimeframe) return;
    
    // 更新当前选择的时间范围
    currentTimeframe = timeframe;
    
    // 更新按钮状态
    document.querySelectorAll('.timeframe-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // 根据timeframe找到对应的按钮并激活
    const timeframeMap = {
        'minute': '分钟',
        'hour': '小时', 
        'day': '天'
    };
    
    document.querySelectorAll('.timeframe-btn').forEach(btn => {
        if (btn.textContent.trim() === timeframeMap[timeframe]) {
            btn.classList.add('active');
        }
    });
    
    // 添加闪动效果到统计数据容器
    const statsContainer = document.getElementById('chartStats');
    if (statsContainer) {
        statsContainer.classList.add('flash-container');
        setTimeout(() => {
            statsContainer.classList.remove('flash-container');
        }, 1000);
    }
    
    // 重新加载图表
    loadChart(currentSymbol);
}

// 启动优化的更新策略
function startOptimizedUpdates() {
    // 清除现有的定时器
    if (priceUpdateInterval) {
        clearInterval(priceUpdateInterval);
    }
    
    // 价格显示更新：每30秒检查一次
    priceUpdateInterval = setInterval(() => {
        loadLatestPrices();
        updateLastUpdated();
    }, 30000);
    
    // 图表数据更新：每5分钟更新一次
    setInterval(() => {
        loadChart(currentSymbol);
    }, 300000);
    
    console.log('⏰ 优化更新策略已启动');
    console.log('   - 价格显示: 每30秒更新');
    console.log('   - 图表数据: 每5分钟更新');
}

// 停止实时价格更新
function stopRealTimePriceUpdates() {
    if (priceUpdateInterval) {
        clearInterval(priceUpdateInterval);
        priceUpdateInterval = null;
    }
}

// 处理页面可见性变化
function handleVisibilityChange() {
    if (document.hidden) {
        // 页面隐藏时暂停更新
        if (priceUpdateInterval) {
            clearInterval(priceUpdateInterval);
            console.log('⏸️ 页面隐藏，暂停更新');
        }
    } else {
        // 页面显示时恢复更新
        startOptimizedUpdates();
        loadLatestPrices();
        console.log('▶️ 页面显示，恢复更新');
    }
}

// 页面卸载时清理
window.addEventListener('beforeunload', function() {
    if (priceUpdateInterval) {
        clearInterval(priceUpdateInterval);
    }
});

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 加密货币监控系统初始化...');
    
    // 初始化统计数据容器
    const statsTitle = document.querySelector('.stats-title');
    if (statsTitle) {
        statsTitle.textContent = `${currentSymbol === 'BTC' ? '比特币' : '以太坊'} (${currentTimeframe === 'minute' ? '分钟' : currentTimeframe === 'hour' ? '小时' : '天'}) 统计`;
    }
    
    // 初始化加载
    loadLatestPrices();
    loadChart(currentSymbol);
    
    // 启动优化的更新策略
    startOptimizedUpdates();
    
    // 添加页面可见性检测
    document.addEventListener('visibilitychange', handleVisibilityChange);
});