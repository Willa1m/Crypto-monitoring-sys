# 🚀 加密货币监控系统

一个功能完整的加密货币价格监控和分析系统，支持实时数据抓取、价格分析、K线图展示和Web界面展示。

## ✨ 主要功能

- 🔄 **实时数据抓取**: 自动获取BTC、ETH等主流加密货币价格数据
- 💾 **数据存储**: 使用MariaDB/MySQL数据库进行数据持久化存储
- ⚡ **缓存加速**: Redis缓存系统提升数据访问性能
- 📊 **数据分析**: 自动生成价格趋势分析和技术指标
- 📈 **K线图表**: 支持分钟、小时、日线等多时间周期K线图
- 🌍 **Web界面**: 现代化的前后端分离Web应用
- ⏰ **定时任务**: 自动化数据更新和分析报告生成
- 🔒 **安全配置**: 完整的安全配置和部署指南

## 🏗️ 系统架构

### 前后端分离架构
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

### 核心模块
- **crypto_scraper.py**: 数据抓取模块，支持多种API数据源
- **crypto_db.py**: 数据库操作模块，处理数据存储和查询
- **data_processor.py**: 数据处理流程，数据清洗和格式化
- **crypto_analyzer.py**: 数据分析模块，生成技术指标和趋势分析
- **kline_processor.py**: K线数据处理，生成多时间周期K线
- **realtime_processor.py**: 实时数据处理，处理实时价格更新
- **crypto_web_app.py**: Web应用模块，提供API接口

## 🚀 快速开始

### 环境要求
- Python 3.8+
- MariaDB/MySQL 5.7+
- Redis 6.0+
- Node.js 14+ (可选，用于前端开发)

### 安装步骤

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

### 访问地址
- 前端界面: http://localhost:8080
- 后端API: http://localhost:5000
- 完整系统: http://localhost:5000 (集成模式)

## 🔧 配置说明

### 必需配置项

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

### API密钥获取

1. **CoinDesk API**: 访问 [CoinDesk API](https://data-api.coindesk.com/) 获取免费API密钥
2. **ngrok**: 访问 [ngrok官网](https://ngrok.com/) 注册获取认证令牌

## 📊 功能特性

### 数据监控
- 支持BTC、ETH等主流加密货币
- 实时价格更新（30秒间隔）
- 历史数据存储和查询
- 多时间周期数据分析

### 图表展示
- 实时价格走势图
- K线图（分钟/小时/日线）
- 技术指标分析
- 价格对比图表

### Web界面
- 响应式设计，支持移动端
- 实时数据更新
- 交互式图表
- 多页面导航

### 系统管理
- 自动化定时任务
- 系统状态监控
- 日志记录和管理
- 缓存管理

## 🔒 安全配置

### 重要安全提醒
⚠️ **本项目已移除所有敏感信息，使用前请务必配置以下内容：**

1. **API密钥**: 配置真实的API密钥
2. **数据库密码**: 设置强密码
3. **Redis密码**: 启用密码保护
4. **管理员密码**: 修改默认密码
5. **SECRET_KEY**: 设置强密码的密钥

### 生产环境部署
- 禁用调试模式
- 配置HTTPS
- 设置防火墙
- 启用访问日志
- 定期安全更新

详细安全配置请参考: [安全配置指南](docs/SECURITY.md)

## 📚 文档

- [项目结构说明](docs/PROJECT_STRUCTURE.md)
- [部署指南](docs/DEPLOYMENT.md)
- [安全配置指南](docs/SECURITY.md)
- [Cloudflare隧道配置](docs/Cloudflare_Tunnel_成功指南.md)

## 🛠️ 开发指南

### 项目结构
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

### 开发环境设置
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

### 运行测试
```bash
cd core
python main.py
# 选择相应的测试选项
```

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 📞 支持与联系

如有问题或建议，请联系：
- 邮箱: tu760979288@gmail.com
- 项目Issues: [GitHub Issues](../../issues)

## 🔄 更新日志

### v1.0.0
- 初始版本发布
- 实现基础数据抓取和存储功能
- 添加Web界面展示
- 支持K线图分析
- 完善安全配置

---

⭐ 如果这个项目对您有帮助，请给它一个星标！