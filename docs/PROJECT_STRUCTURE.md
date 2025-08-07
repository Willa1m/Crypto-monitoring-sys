# 🚀 加密货币监控系统 - 精简版

## 📁 项目结构

```
Bit_test/
├── main.py                    # 🎯 主程序入口（运行此文件启动系统）
├── crypto_db.py              # 💾 数据库操作模块
├── crypto_scraper.py         # 🌐 数据抓取模块
├── data_processor.py         # 📊 数据处理模块
├── crypto_analyzer.py        # 📈 数据分析模块
├── crypto_web_app.py         # 🌍 Web应用模块
├── simple_redis_manager.py   # ⚡ Redis缓存管理
├── requirements.txt          # 📦 依赖包列表
├── README.md                 # 📖 项目说明
├── templates/                # 🎨 Web模板
│   ├── index.html           # 主页模板
│   ├── bitcoin.html         # Bitcoin页面
│   └── ethereum.html        # Ethereum页面
├── static/                   # 📁 静态资源
│   ├── charts/              # 图表文件
│   ├── css/                 # 样式文件
│   ├── icons/               # 图标文件
│   └── js/                  # JavaScript文件
├── guides/                   # 📚 文档指南
│   ├── README_四阶段实现总结.md
│   ├── 外网访问完整方案.md
│   └── 网站访问指南.md
├── cloudflare_tunnel.py      # 🌐 Cloudflare隧道（可选）
└── cloudflared.exe          # 🔧 Cloudflare工具（可选）
```

## 🎯 快速启动

只需运行一个命令：

```bash
python main.py
```

然后选择选项 `5` 启动完整系统！

## ✨ 系统功能

- 🔄 **数据抓取**: 实时获取BTC、ETH价格数据
- 💾 **数据存储**: MariaDB数据库存储
- ⚡ **缓存加速**: Redis缓存提升性能
- 📊 **数据分析**: 自动生成价格趋势分析
- 🌍 **Web界面**: 美观的数据展示界面
- ⏰ **定时任务**: 自动化数据更新

## 🔧 核心模块说明

| 模块 | 功能 | 依赖 |
|------|------|------|
| `main.py` | 系统入口，菜单控制 | 所有模块 |
| `crypto_db.py` | 数据库连接和操作 | mysql.connector |
| `crypto_scraper.py` | 数据抓取 | requests |
| `data_processor.py` | 数据处理流程 | crypto_scraper, crypto_db |
| `crypto_analyzer.py` | 数据分析和图表 | pandas, matplotlib |
| `crypto_web_app.py` | Web应用 | Flask |
| `simple_redis_manager.py` | Redis缓存 | redis |

## 🎮 使用方式

1. **初始化系统**: 选择选项 1
2. **数据抓取**: 选择选项 2  
3. **生成分析**: 选择选项 3
4. **启动Web**: 选择选项 4
5. **完整系统**: 选择选项 5 ⭐（推荐）

## 🌐 访问地址

启动后访问: http://localhost:5000

---

*精简版已删除所有测试文件、部署脚本和多余的管理器，只保留核心功能模块。*