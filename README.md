# 🚀 加密货币监控系统 | Cryptocurrency Monitoring System

[中文](#中文文档) | [English](#english-documentation)

<a name="中文文档"></a>
## 中文文档

一个功能完整的加密货币价格监控和分析系统，支持实时数据抓取、价格分析、K线图展示和Web界面展示。

### ✨ 主要功能

- 🔄 **实时数据抓取**: 自动获取BTC、ETH等主流加密货币价格数据
- 💾 **数据存储**: 使用MariaDB/MySQL数据库进行数据持久化存储
- ⚡ **缓存加速**: Redis缓存系统提升数据访问性能
- 📊 **数据分析**: 自动生成价格趋势分析和技术指标
- 📈 **K线图表**: 支持分钟、小时、日线等多时间周期K线图
- 🌍 **Web界面**: 现代化的前后端分离Web应用
- ⏰ **定时任务**: 自动化数据更新和分析报告生成
- 🔒 **安全配置**: 完整的安全配置和部署指南

### 🏗️ 系统架构

#### 前后端分离架构
```
├── backend/                 # 后端API服务 (Flask)
├── frontend/               # 前端静态文件 (HTML/CSS/JS)
├── core/                   # 核心业务逻辑
├── config/                 # 配置文件
├── data/                   # 数据存储目录
├── static/                 # 静态资源
├── templates/              # 模板文件
└── docs/                   # 文档目录
```

#### 核心模块
- **crypto_scraper.py**: 数据抓取模块，支持多种API数据源
- **crypto_db.py**: 数据库操作模块，处理数据存储和查询
- **data_processor.py**: 数据处理流程，数据清洗和格式化
- **crypto_analyzer.py**: 数据分析模块，生成技术指标和趋势分析
- **kline_processor.py**: K线数据处理，生成多时间周期K线
- **realtime_processor.py**: 实时数据处理，处理实时价格更新
- **crypto_web_app.py**: Web应用模块，提供API接口

### 🚀 快速开始

#### 环境要求
- Python 3.8+
- MariaDB/MySQL 5.7+
- Redis 6.0+
- Node.js 14+ (可选，用于前端开发)

#### 安装步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd Crypto-monitoring-sys-main
```

2. **安装Python依赖**
```bash
# 安装核心依赖
pip install -r core/requirements.txt

# 安装后端依赖
pip install -r backend/requirements.txt
```

3. **配置环境变量**
```bash
# 复制配置文件模板
cp config/.env.example .env

# 编辑配置文件，填入真实配置信息
nano .env
```

4. **初始化数据库**
```bash
cd core
python main.py
# 选择选项 1: 初始化系统
```

5. **启动系统**

**方式1: 启动完整系统（推荐）**
```bash
cd core
python main.py
# 选择选项 6: 启动完整系统
```

**方式2: 分别启动前后端**
```bash
# 启动后端API服务
cd backend
python run.py --host 0.0.0.0 --port 5000

# 启动前端服务（新终端）
cd frontend
python -m http.server 8080
```

#### 访问地址
- 前端界面: http://localhost:8080
- 后端API: http://localhost:5000
- 完整系统: http://localhost:5000 (集成模式)

### 🔧 配置说明

#### 必需配置项

在 `.env` 文件中配置以下信息：

```env
# 数据库配置
DB_HOST=localhost
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_NAME=crypto_db

# Redis配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password

# API密钥配置
COINDESK_API_KEY=your_coindesk_api_key

# ngrok配置（外网访问）
NGROK_AUTHTOKEN=your_ngrok_token

# 安全配置
SECRET_KEY=your_secret_key
ADMIN_PASSWORD=your_admin_password
```

#### API密钥获取

1. **CoinDesk API**: 访问 [CoinDesk API](https://data-api.coindesk.com/) 获取免费API密钥
2. **ngrok**: 访问 [ngrok官网](https://ngrok.com/) 注册获取认证令牌

### 📊 功能特性

#### 数据监控
- 支持BTC、ETH等主流加密货币
- 实时价格更新（30秒间隔）
- 历史数据存储和查询
- 多时间周期数据分析

#### 图表展示
- 实时价格走势图
- K线图（分钟/小时/日线）
- 技术指标分析
- 价格对比图表

#### Web界面
- 响应式设计，支持移动端
- 实时数据更新
- 交互式图表
- 多页面导航

#### 系统管理
- 自动化定时任务
- 系统状态监控
- 日志记录和管理
- 缓存管理

### 🔒 安全配置

#### 重要安全提醒
⚠️ **本项目已移除所有敏感信息，使用前请务必配置以下内容：**

1. **API密钥**: 配置真实的API密钥
2. **数据库密码**: 设置强密码
3. **Redis密码**: 启用密码保护
4. **管理员密码**: 修改默认密码
5. **SECRET_KEY**: 设置强密码的密钥

#### 生产环境部署
- 禁用调试模式
- 配置HTTPS
- 设置防火墙
- 启用访问日志
- 定期安全更新

详细安全配置请参考: [安全配置指南](docs/SECURITY.md)

### 📚 文档

- [项目结构说明](docs/PROJECT_STRUCTURE.md)
- [部署指南](docs/DEPLOYMENT.md)
- [安全配置指南](docs/SECURITY.md)
- [Cloudflare隧道配置](docs/Cloudflare_Tunnel_成功指南.md)

### 🛠️ 开发指南

#### 项目结构
```
Crypto-monitoring-sys-main/
├── backend/                 # 后端API服务
│   ├── app.py              # Flask API应用
│   ├── run.py              # 启动脚本
│   └── requirements.txt    # 依赖包
├── frontend/               # 前端应用
│   ├── index.html          # 主页面
│   ├── css/                # 样式文件
│   └── js/                 # JavaScript文件
├── core/                   # 核心业务逻辑
│   ├── main.py             # 主程序入口
│   ├── crypto_*.py         # 各功能模块
│   └── requirements.txt    # 核心依赖
├── config/                 # 配置文件
├── data/                   # 数据存储
├── static/                 # 静态资源
├── templates/              # 模板文件
└── docs/                   # 文档
```

#### 开发环境设置
```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows

# 安装开发依赖
pip install -r requirements.txt
pip install -r backend/requirements.txt
```

#### 运行测试
```bash
cd core
python main.py
# 选择相应的测试选项
```

### 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

### 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

### 📞 支持与联系

如有问题或建议，请联系：
- 邮箱: tu760979288@gmail.com
- 项目Issues: [GitHub Issues](../../issues)

### 🔄 更新日志

#### v1.0.0
- 初始版本发布
- 实现基础数据抓取和存储功能
- 添加Web界面展示
- 支持K线图分析
- 完善安全配置

---

<a name="english-documentation"></a>
## English Documentation

A comprehensive cryptocurrency price monitoring and analysis system supporting real-time data scraping, price analysis, K-line chart display, and web interface presentation.

### ✨ Key Features

- 🔄 **Real-time Data Collection**: Automatically fetch price data for mainstream cryptocurrencies like BTC and ETH
- 💾 **Data Storage**: Persistent data storage using MariaDB/MySQL database
- ⚡ **Cache Acceleration**: Redis caching system to improve data access performance
- 📊 **Data Analysis**: Automatic generation of price trend analysis and technical indicators
- 📈 **K-line Charts**: Support for multiple time period K-line charts (minute/hour/day)
- 🌍 **Web Interface**: Modern front-end and back-end separated web application
- ⏰ **Scheduled Tasks**: Automated data updates and analysis report generation
- 🔒 **Security Configuration**: Complete security configuration and deployment guide

### 🏗️ System Architecture

#### Front-end and Back-end Separation
```
├── backend/                 # Backend API service (Flask)
├── frontend/               # Frontend static files (HTML/CSS/JS)
├── core/                   # Core business logic
├── config/                 # Configuration files
├── data/                   # Data storage directory
├── static/                 # Static resources
├── templates/              # Template files
└── docs/                   # Documentation directory
```

#### Core Modules
- **crypto_scraper.py**: Data scraping module, supporting multiple API data sources
- **crypto_db.py**: Database operation module, handling data storage and queries
- **data_processor.py**: Data processing workflow, data cleaning and formatting
- **crypto_analyzer.py**: Data analysis module, generating technical indicators and trend analysis
- **kline_processor.py**: K-line data processing, generating multi-time period K-lines
- **realtime_processor.py**: Real-time data processing, handling real-time price updates
- **crypto_web_app.py**: Web application module, providing API interfaces

### 🚀 Quick Start

#### Requirements
- Python 3.8+
- MariaDB/MySQL 5.7+
- Redis 6.0+
- Node.js 14+ (optional, for frontend development)

#### Installation Steps

1. **Clone the Project**
```bash
git clone <repository-url>
cd Crypto-monitoring-sys-main
```

2. **Install Python Dependencies**
```bash
# Install core dependencies
pip install -r core/requirements.txt

# Install backend dependencies
pip install -r backend/requirements.txt
```

3. **Configure Environment Variables**
```bash
# Copy configuration file template
cp config/.env.example .env

# Edit configuration file, fill in real configuration information
nano .env
```

4. **Initialize Database**
```bash
cd core
python main.py
# Select option 1: Initialize system
```

5. **Start the System**

**Method 1: Start Complete System (Recommended)**
```bash
cd core
python main.py
# Select option 6: Start complete system
```

**Method 2: Start Frontend and Backend Separately**
```bash
# Start backend API service
cd backend
python run.py --host 0.0.0.0 --port 5000

# Start frontend service (new terminal)
cd frontend
python -m http.server 8080
```

#### Access Addresses
- Frontend interface: http://localhost:8080
- Backend API: http://localhost:5000
- Complete system: http://localhost:5000 (integrated mode)

### 🔧 Configuration Instructions

#### Required Configuration Items

Configure the following information in the `.env` file:

```env
# Database configuration
DB_HOST=localhost
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_NAME=crypto_db

# Redis configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password

# API key configuration
COINDESK_API_KEY=your_coindesk_api_key

# ngrok configuration (external access)
NGROK_AUTHTOKEN=your_ngrok_token

# Security configuration
SECRET_KEY=your_secret_key
ADMIN_PASSWORD=your_admin_password
```

#### API Key Acquisition

1. **CoinDesk API**: Visit [CoinDesk API](https://data-api.coindesk.com/) to get a free API key
2. **ngrok**: Visit [ngrok website](https://ngrok.com/) to register and get an authentication token

### 📊 Features

#### Data Monitoring
- Support for mainstream cryptocurrencies like BTC and ETH
- Real-time price updates (30-second intervals)
- Historical data storage and query
- Multi-time period data analysis

#### Chart Display
- Real-time price trend charts
- K-line charts (minute/hour/day)
- Technical indicator analysis
- Price comparison charts

#### Web Interface
- Responsive design, supporting mobile devices
- Real-time data updates
- Interactive charts
- Multi-page navigation

#### System Management
- Automated scheduled tasks
- System status monitoring
- Log recording and management
- Cache management

### 🔒 Security Configuration

#### Important Security Reminder
⚠️ **All sensitive information has been removed from this project. Before use, please be sure to configure the following:**

1. **API Keys**: Configure real API keys
2. **Database Password**: Set strong passwords
3. **Redis Password**: Enable password protection
4. **Admin Password**: Change default password
5. **SECRET_KEY**: Set a strong password key

#### Production Environment Deployment
- Disable debug mode
- Configure HTTPS
- Set up firewall
- Enable access logs
- Regular security updates

For detailed security configuration, please refer to: [Security Configuration Guide](docs/SECURITY.md)

### 📚 Documentation

- [Project Structure Description](docs/PROJECT_STRUCTURE.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Security Configuration Guide](docs/SECURITY.md)
- [Cloudflare Tunnel Configuration](docs/Cloudflare_Tunnel_成功指南.md)

### 🛠️ Development Guide

#### Project Structure
```
Crypto-monitoring-sys-main/
├── backend/                 # Backend API service
│   ├── app.py              # Flask API application
│   ├── run.py              # Startup script
│   └── requirements.txt    # Dependencies
├── frontend/               # Frontend application
│   ├── index.html          # Main page
│   ├── css/                # Style files
│   └── js/                 # JavaScript files
├── core/                   # Core business logic
│   ├── main.py             # Main program entry
│   ├── crypto_*.py         # Various function modules
│   └── requirements.txt    # Core dependencies
├── config/                 # Configuration files
├── data/                   # Data storage
├── static/                 # Static resources
├── templates/              # Template files
└── docs/                   # Documentation
```

#### Development Environment Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install development dependencies
pip install -r requirements.txt
pip install -r backend/requirements.txt
```

#### Running Tests
```bash
cd core
python main.py
# Select the appropriate test option
```

### 🤝 Contribution Guidelines

1. Fork the project
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

### 📞 Support and Contact

For questions or suggestions, please contact:
- Email: tu760979288@gmail.com
- Project Issues: [GitHub Issues](../../issues)

### 🔄 Update Log

#### v1.0.0
- Initial version release
- Implementation of basic data scraping and storage functionality
- Addition of web interface display
- Support for K-line chart analysis
- Improved security configuration

---

⭐ If this project is helpful to you, please give it a star!