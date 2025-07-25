# 🚀 加密货币价格监控系统

这是一个功能完整的加密货币价格监控系统，支持比特币(BTC)和以太坊(ETH)的实时价格抓取、历史数据存储、技术指标分析和Web可视化展示。

## ✨ 功能特性

- 🚀 **实时数据抓取**: 自动抓取比特币和以太坊的当前价格和历史数据
- 💾 **数据库存储**: 使用MySQL/MariaDB存储价格数据，支持分钟、小时、天级别的历史数据
- ⚡ **Redis缓存**: 集成Redis缓存系统，提升数据访问性能
- 📊 **数据分析**: 自动生成价格统计报告和趋势图表
- 📈 **K线图表**: 专业的K线图表展示，支持ECharts技术指标分析
- 🔧 **技术指标**: 支持MA、RSI、MACD、布林带、KDJ、波动率等多种技术指标
- 🌐 **Web界面**: 现代化的Web界面，支持实时价格显示和交互式图表
- ⏰ **定时任务**: 自动化的数据更新和分析任务
- 🧪 **压力测试**: 内置网络压力测试工具，评估系统性能
- 🌍 **外网访问**: 支持Cloudflare隧道，实现外网访问

## 📁 系统架构

```
Bit_test/
├── main.py                    # 🎯 主控制程序
├── crypto_scraper.py          # 🌐 数据抓取模块
├── crypto_db.py              # 💾 数据库管理模块
├── data_processor.py         # 📊 数据处理模块
├── crypto_analyzer.py        # 📈 数据分析模块
├── crypto_web_app.py         # 🌍 Web应用模块
├── simple_redis_manager.py   # ⚡ Redis缓存管理
├── kline_backend.py          # 📈 K线数据后端处理
├── kline_processor.py        # 📊 K线数据处理器
├── cloudflare_tunnel.py      # 🌐 Cloudflare隧道配置
├── network_stress_test.py    # 🧪 网络压力测试
├── templates/                # 🎨 Web模板
│   ├── index.html           # 主页模板
│   ├── bitcoin.html         # Bitcoin页面
│   ├── ethereum.html        # Ethereum页面
│   └── kline.html           # K线图表页面
├── static/                   # 📁 静态资源
│   ├── charts/              # 图表文件
│   ├── css/                 # 样式文件
│   ├── icons/               # 图标文件
│   └── js/                  # JavaScript文件
├── kline_data/              # 📊 K线数据文件
├── stress_tests/            # 🧪 压力测试工具
├── guides/                  # 📚 文档指南
├── requirements.txt         # 📦 项目依赖
└── README.md               # 📖 项目说明
```

## 💾 数据库结构

系统使用以下表结构存储数据：

- `crypto_info`: 加密货币基本信息
- `current_prices`: 当前价格数据
- `minute_data`: 分钟级历史数据
- `hour_data`: 小时级历史数据  
- `day_data`: 天级历史数据

## 🛠️ 安装和配置

### 1. 环境要求

- Python 3.8+
- MySQL/MariaDB 数据库
- Redis 服务器（可选，用于缓存）

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 数据库配置

确保您的MySQL/MariaDB服务器正在运行，并在 `crypto_db.py` 中配置正确的数据库连接信息：

```python
self.pool_config = {
    'host': '192.168.73.130',
    'user': 'k1ll',
    'password': '654',
    'database': 'Scraping1',
    'port': 3306,
    'charset': 'utf8mb4'
}
```

### 4. Redis配置（可选）

如需启用缓存功能，请在 `simple_redis_manager.py` 中配置Redis连接：

```python
def __init__(self, host='192.168.73.130', port=7001, db=0):
```

### 5. API配置

系统使用CoinDesk API获取数据，API密钥已在代码中配置。如需更换，请修改 `crypto_scraper.py` 中的 `API_KEY`。

## 🚀 快速启动

### 一键启动（推荐）

```bash
python main.py
```

然后选择选项 `5` 启动完整系统！

### 菜单选项说明

- **选项1**: 初始化系统（重建数据库）
- **选项2**: 运行数据抓取和处理
- **选项3**: 生成分析报告
- **选项4**: 启动Web服务器
- **选项5**: 启动完整系统（推荐）⭐
- **选项6**: 查看系统状态
- **选项0**: 退出

## 🌐 Web界面访问

启动Web服务器后，在浏览器中访问：

- **本地访问**: http://localhost:5000
- **局域网访问**: http://192.168.x.x:5000
- **外网访问**: 使用Cloudflare隧道（见guides目录）

### 页面功能

- **主页** (`/`): 系统概览和实时价格
- **比特币页面** (`/bitcoin`): BTC专项分析
- **以太坊页面** (`/ethereum`): ETH专项分析
- **K线图表** (`/kline`): 专业K线图表和技术指标分析

## 📊 核心功能模块

### 1. 数据抓取 (crypto_scraper.py)
- 从CoinDesk API获取实时价格数据
- 支持分钟、小时、天级别的历史数据抓取
- 包含错误处理和重试机制
- 支持速率限制处理

### 2. 数据库管理 (crypto_db.py)
- 自动创建和管理数据库表结构
- 连接池管理，提升并发性能
- 支持数据库清空和重建
- 提供数据插入和查询接口

### 3. Redis缓存 (simple_redis_manager.py)
- 价格数据缓存，减少数据库查询
- 图表数据缓存，提升页面加载速度
- 支持缓存过期和清理
- 提供缓存统计信息

### 4. K线图表 (kline_backend.py)
- 专业K线数据处理
- 技术指标计算：MA、RSI、MACD、布林带、KDJ、波动率
- ECharts图表渲染
- 支持多时间周期分析

### 5. 数据分析 (crypto_analyzer.py)
- 生成价格走势图表
- 计算统计指标（最高价、最低价、平均价等）
- 创建比较图表和分析报告
- 支持多种时间范围的分析

### 6. Web应用 (crypto_web_app.py)
- 提供RESTful API接口
- 实时价格显示
- 交互式图表展示
- 响应式Web设计

### 7. 压力测试 (stress_tests/)
- **快速压力测试** (`quick_stress_test.py`): 网络轰炸测试
- **综合测试** (`comprehensive_test.py`): 全面系统测试
- **系统监控** (`system_monitor.py`): 实时性能监控

## ⏰ 定时任务

系统支持以下自动化任务：
- 每5分钟抓取一次最新数据
- 每15分钟生成一次分析报告
- 每小时执行一次完整的数据处理

## 📝 日志系统

系统为每个模块生成独立的日志文件：
- `crypto_system.log`: 系统总日志
- `crypto_scraper.log`: 数据抓取日志
- `crypto_db.log`: 数据库操作日志
- `data_processor.log`: 数据处理日志
- `crypto_analyzer.log`: 数据分析日志
- `crypto_web_app.log`: Web应用日志

## 🔧 故障排除

### 常见问题

1. **数据库连接失败**
   - 检查数据库服务器是否运行
   - 验证连接配置信息
   - 确认数据库用户权限
   - 检查防火墙设置

2. **Redis连接失败**
   - 检查Redis服务器状态
   - 验证Redis配置信息
   - 确认网络连接
   - 系统会自动降级到无缓存模式

3. **API请求失败**
   - 检查网络连接
   - 验证API密钥有效性
   - 查看速率限制状态
   - 检查防火墙和代理设置

4. **Web服务器无法启动**
   - 检查端口5000是否被占用
   - 确认Flask依赖已正确安装
   - 查看系统日志文件

5. **K线图表显示异常**
   - 检查ECharts库是否正确加载
   - 验证数据格式是否正确
   - 查看浏览器控制台错误信息

### 调试模式

在开发环境中，可以启用调试模式：
```python
app.run(debug=True, host='0.0.0.0', port=5000)
```

### 性能优化建议

1. **数据库优化**
   - 定期清理历史数据
   - 优化查询索引
   - 调整连接池大小

2. **缓存优化**
   - 合理设置缓存过期时间
   - 监控缓存命中率
   - 定期清理无效缓存

3. **网络优化**
   - 使用CDN加速静态资源
   - 启用gzip压缩
   - 优化API响应时间

## 🧪 压力测试

系统内置多种压力测试工具：

### 快速压力测试
```bash
cd stress_tests
python quick_stress_test.py
```

### 综合系统测试
```bash
cd stress_tests
python comprehensive_test.py
```

### 系统性能监控
```bash
cd stress_tests
python system_monitor.py
```

## 🌍 外网访问

### Cloudflare隧道

1. 下载并配置cloudflared
2. 运行隧道脚本：
```bash
python cloudflare_tunnel.py
```

详细配置请参考 `guides/外网访问完整方案.md`

## 📚 文档指南

- `guides/README_四阶段实现总结.md`: 项目开发总结
- `guides/外网访问完整方案.md`: 外网访问配置指南
- `guides/网站访问指南.md`: 网站使用指南
- `Cloudflare_Tunnel_成功指南.md`: Cloudflare隧道配置
- `PROJECT_STRUCTURE.md`: 项目结构说明

## 🚀 扩展功能

系统设计支持以下扩展：

### 数据源扩展
- 添加更多加密货币（LTC、ADA、DOT等）
- 集成其他数据源API（Binance、Coinbase等）
- 支持股票、外汇等其他金融数据

### 技术指标扩展
- 增加更多技术指标（BOLL、SAR、CCI等）
- 支持自定义指标公式
- 添加量化交易信号

### 功能扩展
- 价格预警和通知系统
- 数据导出功能（CSV、Excel）
- 移动端适配
- 多语言支持
- 用户管理系统

### 部署扩展
- Docker容器化部署
- Kubernetes集群部署
- 云服务器部署
- 负载均衡配置

## 💻 技术栈

### 后端技术
- **Python 3.8+**: 主要开发语言
- **Flask**: Web框架
- **MySQL/MariaDB**: 主数据库
- **Redis**: 缓存数据库
- **Pandas**: 数据处理
- **NumPy**: 数值计算
- **Matplotlib**: 图表生成

### 前端技术
- **HTML5/CSS3**: 页面结构和样式
- **JavaScript**: 交互逻辑
- **ECharts**: 专业图表库
- **Bootstrap**: 响应式框架

### 开发工具
- **Schedule**: 定时任务
- **Logging**: 日志系统
- **Asyncio**: 异步编程
- **Aiohttp**: 异步HTTP客户端

### 部署工具
- **Cloudflare**: CDN和隧道服务
- **Gunicorn**: WSGI服务器（可选）
- **Nginx**: 反向代理（可选）

## 📄 许可证

本项目采用 MIT 许可证，详情请参阅 LICENSE 文件。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request 来改进这个项目！

## 📞 联系方式

如有问题或建议，请通过以下方式联系：
- 提交 GitHub Issue
- 发送邮件至项目维护者

---

**感谢使用加密货币价格监控系统！** 🚀
- **后端**: Python, Flask
- **数据库**: MySQL/MariaDB
- **数据处理**: Pandas, NumPy
- **图表生成**: Matplotlib
- **前端**: HTML5, CSS3, JavaScript, Chart.js
- **任务调度**: Schedule
- **API**: CoinDesk API

## 许可证

本项目仅供学习和研究使用。

## 联系方式

如有问题或建议，请通过以下方式联系：
- 项目仓库: [GitHub链接]
- 邮箱: [联系邮箱]

---

**注意**: 请确保在生产环境中使用时，妥善保护API密钥和数据库凭据。
