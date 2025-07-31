# 🚀 Bit_test - 加密货币实时监控系统 / Cryptocurrency Real-time Monitoring System

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.3.3-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)]()

[中文](#中文文档) | [English](#english-documentation)

---

## 中文文档

一个功能完整的加密货币实时监控和分析系统，支持多种数据源、实时价格追踪、技术指标分析和K线图表展示。

### 📋 目录

- [功能特性](#-功能特性)
- [系统架构](#-系统架构)
- [快速开始](#-快速开始)
- [安装指南](#-安装指南)
- [配置说明](#-配置说明)
- [使用方法](#-使用方法)
- [API文档](#-api文档)
- [部署指南](#-部署指南)
- [项目结构](#-项目结构)
- [维护团队](#-维护团队)
- [贡献指南](#-贡献指南)
- [许可证](#-许可证)

### ✨ 功能特性

#### 🔥 核心功能
- **实时价格监控**: 支持Bitcoin (BTC)、Ethereum (ETH)等主流加密货币
- **多时间维度数据**: 分钟级、小时级、日级数据采集和分析
- **技术指标分析**: 移动平均线、RSI、MACD等技术指标计算
- **K线图表**: 交互式K线图表展示，支持多种时间周期
- **数据缓存**: Redis缓存机制，提升数据访问速度
- **定时任务**: 自动化数据采集和分析任务

#### 🌐 Web界面
- **响应式设计**: 支持桌面和移动设备
- **实时更新**: WebSocket实时数据推送
- **图表展示**: Chart.js驱动的交互式图表
- **多页面支持**: 首页、详情页、K线分析页

#### 🔧 技术特性
- **微服务架构**: 模块化设计，易于扩展
- **数据库支持**: MariaDB/MySQL数据存储
- **缓存系统**: Redis高性能缓存
- **API集成**: CoinDesk API数据源
- **负载均衡**: Nginx反向代理支持
- **云部署**: Cloudflare Tunnel外网访问

### 🏗️ 系统架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   前端界面      │    │   Flask Web     │    │   数据处理      │
│   (HTML/JS)     │◄──►│   应用服务      │◄──►│   (Python)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Nginx代理     │    │   Redis缓存     │    │   MariaDB       │
│   (负载均衡)    │    │   (高速缓存)    │    │   (数据存储)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                    ┌─────────────────┐
                    │   外部API       │
                    │   (CoinDesk)    │
                    └─────────────────┘
```

### 🚀 快速开始

#### 前置要求
- Python 3.8+
- MariaDB/MySQL 5.7+
- Redis 6.0+
- Git

#### 一键启动
```bash
# 克隆项目
git clone https://github.com/your-username/Bit_test.git
cd Bit_test

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入您的配置

# 启动系统
python main.py
# 选择选项 5: 启动完整系统
```

访问 http://localhost:5000 查看应用！

### 📦 安装指南

#### 1. 环境准备
```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 升级pip
pip install --upgrade pip
```

#### 2. 安装依赖
```bash
pip install -r requirements.txt
```

#### 3. 数据库配置
```sql
-- 创建数据库
CREATE DATABASE Scraping1 CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 创建用户（可选）
CREATE USER 'crypto_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON Scraping1.* TO 'crypto_user'@'localhost';
FLUSH PRIVILEGES;
```

#### 4. Redis配置
```bash
# 启动Redis服务
redis-server

# 验证Redis连接
redis-cli ping
```

### ⚙️ 配置说明

#### 数据库配置
编辑 `crypto_db.py` 中的连接参数：
```python
pool_config = {
    'host': 'localhost',        # 数据库主机
    'user': 'your_username',    # 数据库用户名
    'password': 'your_password', # 数据库密码
    'database': 'Scraping1',    # 数据库名称
    'port': 3306,               # 数据库端口
    'pool_name': 'crypto_pool',
    'pool_size': 10,
    'pool_reset_session': True,
    'autocommit': True
}
```

#### Redis配置
编辑 `simple_redis_manager.py` 中的连接参数：
```python
def __init__(self, host='localhost', port=6379, db=0, password=None):
    self.host = host
    self.port = port
    self.db = db
    self.password = password
```

### 🎯 使用方法

#### 启动系统
```bash
python main.py
```

选择相应的选项：
1. **初始化系统** - 重建数据库结构
2. **运行数据抓取和处理** - 执行数据采集和处理
3. **生成分析报告** - 运行技术指标分析
4. **启动Web服务器** - 启动Web界面
5. **启动完整系统** - 一键启动所有服务（推荐）
6. **查看系统状态** - 检查系统运行状态

#### Web界面功能

- **主页 (/)**: 实时价格展示、价格变化趋势、快速导航菜单
- **Bitcoin详情页 (/bitcoin)**: BTC详细价格信息、历史价格图表、技术指标分析
- **Ethereum详情页 (/ethereum)**: ETH详细价格信息、历史价格图表、技术指标分析
- **K线分析页 (/kline)**: 交互式K线图表、多时间周期切换、技术指标叠加

### 📚 API文档

#### 获取当前价格
```http
GET /api/current-prices
```

响应示例：
```json
{
  "BTC": {
    "price": 45000.00,
    "change_24h": 2.5,
    "timestamp": "2025-01-27T12:00:00Z"
  },
  "ETH": {
    "price": 3200.00,
    "change_24h": 1.8,
    "timestamp": "2025-01-27T12:00:00Z"
  }
}
```

#### 获取历史数据
```http
GET /api/historical/{symbol}?timeframe={minute|hour|day}&limit={number}
```

#### 获取K线数据
```http
GET /api/kline/{symbol}?timeframe={minute|hour|day}
```

### 🚀 部署指南

#### Docker部署
```bash
# 构建镜像
docker build -t bit_test .

# 运行容器
docker run -d -p 5000:5000 --name crypto_monitor bit_test
```

#### Nginx配置
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### Cloudflare Tunnel
```bash
# 安装cloudflared
# 运行tunnel
python cloudflare_tunnel.py
```

详细部署指南请参考 [DEPLOYMENT.md](DEPLOYMENT.md)

### 📁 项目结构

```
Bit_test/
├── 📄 main.py                 # 主程序入口
├── 🗃️ crypto_db.py           # 数据库操作
├── 🕷️ crypto_scraper.py      # 数据采集
├── 📊 crypto_analyzer.py     # 数据分析
├── 🌐 crypto_web_app.py      # Web应用
├── ⚙️ data_processor.py      # 数据处理
├── 📈 kline_processor.py     # K线数据处理
├── 🔄 simple_redis_manager.py # Redis管理
├── 📋 requirements.txt       # 依赖列表
├── 📁 frontend/              # 前端文件
│   ├── 🎨 css/              # 样式文件
│   ├── 📜 js/               # JavaScript文件
│   ├── 🖼️ icons/            # 图标文件
│   └── 📄 index.html        # 主页面
├── 📁 templates/             # 模板文件
├── 📁 static/                # 静态资源
├── 📁 kline_data/           # K线数据存储
├── 📁 nginx/                # Nginx配置
├── 📁 guides/               # 使用指南
└── 📁 stress_tests/         # 压力测试
```

### 👥 维护团队

**William (willia1m)**
- 📧 Email: tu760979288@gmail.com
- 🔧 负责: 系统架构设计、核心功能开发
- 🌟 专长: Python后端开发、数据库设计、API集成

### 联系方式
- 📧 技术支持: tu760979288@gmail.com
- 🐛 问题反馈: [GitHub Issues](https://github.com/your-username/Bit_test/issues)
- 💬 讨论交流: [GitHub Discussions](https://github.com/your-username/Bit_test/discussions)

### 🤝 贡献指南

我们欢迎所有形式的贡献！

#### 如何贡献
1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

#### 代码规范
- 遵循 PEP 8 Python代码规范
- 添加适当的注释和文档
- 编写单元测试
- 确保所有测试通过

### 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

---

## English Documentation

A comprehensive cryptocurrency real-time monitoring and analysis system that supports multiple data sources, real-time price tracking, technical indicator analysis, and K-line chart visualization.

### 📋 Table of Contents

- [Features](#-features)
- [System Architecture](#-system-architecture)
- [Quick Start](#-quick-start)
- [Installation Guide](#-installation-guide)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [API Documentation](#-api-documentation)
- [Deployment Guide](#-deployment-guide)
- [Project Structure](#-project-structure)
- [Maintainers](#-maintainers)
- [Contributing](#-contributing)
- [License](#-license)

### ✨ Features

#### 🔥 Core Features
- **Real-time Price Monitoring**: Support for Bitcoin (BTC), Ethereum (ETH), and other major cryptocurrencies
- **Multi-timeframe Data**: Minute, hourly, and daily data collection and analysis
- **Technical Indicator Analysis**: Moving averages, RSI, MACD, and other technical indicators
- **K-line Charts**: Interactive K-line chart display with multiple time periods
- **Data Caching**: Redis caching mechanism for improved data access speed
- **Scheduled Tasks**: Automated data collection and analysis tasks

#### 🌐 Web Interface
- **Responsive Design**: Support for desktop and mobile devices
- **Real-time Updates**: WebSocket real-time data push
- **Chart Display**: Chart.js-powered interactive charts
- **Multi-page Support**: Homepage, detail pages, K-line analysis page

#### 🔧 Technical Features
- **Microservice Architecture**: Modular design, easy to extend
- **Database Support**: MariaDB/MySQL data storage
- **Caching System**: Redis high-performance caching
- **API Integration**: CoinDesk API data source
- **Load Balancing**: Nginx reverse proxy support
- **Cloud Deployment**: Cloudflare Tunnel external access

### 🏗️ System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Flask Web     │    │   Data          │
│   (HTML/JS)     │◄──►│   Application   │◄──►│   Processing    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Nginx Proxy   │    │   Redis Cache   │    │   MariaDB       │
│   (Load Balance)│    │   (High Speed)  │    │   (Data Store)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                    ┌─────────────────┐
                    │   External API  │
                    │   (CoinDesk)    │
                    └─────────────────┘
```

### 🚀 Quick Start

#### Prerequisites
- Python 3.8+
- MariaDB/MySQL 5.7+
- Redis 6.0+
- Git

#### One-click Launch
```bash
# Clone the project
git clone https://github.com/your-username/Bit_test.git
cd Bit_test

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env file with your configuration

# Start the system
python main.py
# Select option 5: Start complete system
```

Visit http://localhost:5000 to view the application!

### 📦 Installation Guide

#### 1. Environment Setup
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

#### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 3. Database Configuration
```sql
-- Create database
CREATE DATABASE Scraping1 CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create user (optional)
CREATE USER 'crypto_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON Scraping1.* TO 'crypto_user'@'localhost';
FLUSH PRIVILEGES;
```

#### 4. Redis Configuration
```bash
# Start Redis service
redis-server

# Verify Redis connection
redis-cli ping
```

### ⚙️ Configuration

#### Database Configuration
Edit connection parameters in `crypto_db.py`:
```python
pool_config = {
    'host': 'localhost',        # Database host
    'user': 'your_username',    # Database username
    'password': 'your_password', # Database password
    'database': 'Scraping1',    # Database name
    'port': 3306,               # Database port
    'pool_name': 'crypto_pool',
    'pool_size': 10,
    'pool_reset_session': True,
    'autocommit': True
}
```

#### Redis Configuration
Edit connection parameters in `simple_redis_manager.py`:
```python
def __init__(self, host='localhost', port=6379, db=0, password=None):
    self.host = host
    self.port = port
    self.db = db
    self.password = password
```

### 🎯 Usage

#### Start System
```bash
python main.py
```

Select the appropriate option:
1. **Initialize System** - Rebuild database structure
2. **Run Data Scraping and Processing** - Execute data collection and processing
3. **Generate Analysis Report** - Run technical indicator analysis
4. **Start Web Server** - Launch web interface
5. **Start Complete System** - One-click start all services (Recommended)
6. **View System Status** - Check system running status

#### Web Interface Features

- **Homepage (/)**: Real-time price display, price change trends, quick navigation menu
- **Bitcoin Details (/bitcoin)**: BTC detailed price information, historical price charts, technical indicator analysis
- **Ethereum Details (/ethereum)**: ETH detailed price information, historical price charts, technical indicator analysis
- **K-line Analysis (/kline)**: Interactive K-line charts, multi-timeframe switching, technical indicator overlay

### 📚 API Documentation

#### Get Current Prices
```http
GET /api/current-prices
```

Response example:
```json
{
  "BTC": {
    "price": 45000.00,
    "change_24h": 2.5,
    "timestamp": "2025-01-27T12:00:00Z"
  },
  "ETH": {
    "price": 3200.00,
    "change_24h": 1.8,
    "timestamp": "2025-01-27T12:00:00Z"
  }
}
```

#### Get Historical Data
```http
GET /api/historical/{symbol}?timeframe={minute|hour|day}&limit={number}
```

#### Get K-line Data
```http
GET /api/kline/{symbol}?timeframe={minute|hour|day}
```

### 🚀 Deployment Guide

#### Docker Deployment
```bash
# Build image
docker build -t bit_test .

# Run container
docker run -d -p 5000:5000 --name crypto_monitor bit_test
```

#### Nginx Configuration
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### Cloudflare Tunnel
```bash
# Install cloudflared
# Run tunnel
python cloudflare_tunnel.py
```

For detailed deployment guide, please refer to [DEPLOYMENT.md](DEPLOYMENT.md)

### 📁 Project Structure

```
Bit_test/
├── 📄 main.py                 # Main program entry
├── 🗃️ crypto_db.py           # Database operations
├── 🕷️ crypto_scraper.py      # Data collection
├── 📊 crypto_analyzer.py     # Data analysis
├── 🌐 crypto_web_app.py      # Web application
├── ⚙️ data_processor.py      # Data processing
├── 📈 kline_processor.py     # K-line data processing
├── 🔄 simple_redis_manager.py # Redis management
├── 📋 requirements.txt       # Dependencies list
├── 📁 frontend/              # Frontend files
│   ├── 🎨 css/              # Style files
│   ├── 📜 js/               # JavaScript files
│   ├── 🖼️ icons/            # Icon files
│   └── 📄 index.html        # Main page
├── 📁 templates/             # Template files
├── 📁 static/                # Static resources
├── 📁 kline_data/           # K-line data storage
├── 📁 nginx/                # Nginx configuration
├── 📁 guides/               # Usage guides
└── 📁 stress_tests/         # Stress tests
```

### 👥 Maintainers

**William (willia1m)**
- 📧 Email: tu760979288@gmail.com
- 🔧 Responsibilities: System architecture design, core feature development
- 🌟 Expertise: Python backend development, database design, API integration

### Contact
- 📧 Technical Support: tu760979288@gmail.com
- 🐛 Bug Reports: [GitHub Issues](https://github.com/your-username/Bit_test/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/your-username/Bit_test/discussions)

### 🤝 Contributing

We welcome all forms of contributions!

#### How to Contribute
1. Fork this project
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

#### Code Standards
- Follow PEP 8 Python code standards
- Add appropriate comments and documentation
- Write unit tests
- Ensure all tests pass

### 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### 🙏 Acknowledgments

- [CoinDesk API](https://www.coindesk.com/coindesk-api) - Cryptocurrency data provider
- [Chart.js](https://www.chartjs.org/) - Chart visualization library
- [Flask](https://flask.palletsprojects.com/) - Web framework
- [Redis](https://redis.io/) - Caching system
- [MariaDB](https://mariadb.org/) - Database system

---

<div align="center">

**⭐ If this project helps you, please give us a star!**

[🏠 Home](https://github.com/your-username/Bit_test) • 
[📖 Documentation](https://github.com/your-username/Bit_test/wiki) • 
[🐛 Issues](https://github.com/your-username/Bit_test/issues) • 
[💬 Discussions](https://github.com/your-username/Bit_test/discussions)

</div>