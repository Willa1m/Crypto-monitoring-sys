# 🔒 安全配置指南

## 重要提醒
本项目已移除所有敏感信息，请在使用前配置以下内容：

## 1. API密钥配置

### CoinDesk API
1. 访问 [CoinDesk API](https://data-api.coindesk.com/) 获取API密钥
2. 在 `crypto_scraper.py` 中替换 `YOUR_API_KEY_HERE`
3. 或使用环境变量：`COINDESK_API_KEY`

## 2. 环境变量配置

### 创建 .env 文件
```bash
cp .env.example .env
```

### 填写配置信息
编辑 `.env` 文件，填入真实的配置信息：
- API密钥
- 数据库连接信息
- Redis配置
- ngrok认证令牌
- 管理员密码

## 3. ngrok配置

### 获取认证令牌
1. 注册 [ngrok账户](https://ngrok.com/)
2. 获取认证令牌
3. 在 `.env` 文件中设置 `NGROK_AUTHTOKEN`

### 配置方法
```bash
# 方法1：使用环境变量
export NGROK_AUTHTOKEN=your_token_here

# 方法2：使用配置命令
python -c "from pyngrok import conf; conf.get_default().auth_token = 'your_token_here'"
```

## 4. 数据库安全

### MySQL配置
- 使用强密码
- 限制访问权限
- 定期备份数据

### Redis配置
- 设置密码保护
- 配置访问控制
- 监控连接状态

## 5. Web应用安全

### Flask配置
- 设置强密码的SECRET_KEY
- 启用HTTPS（生产环境）
- 配置访问控制

### 管理员认证
- 修改默认用户名和密码
- 使用强密码策略
- 定期更换密码

## 6. 文件权限

### 敏感文件保护
```bash
# 设置环境变量文件权限
chmod 600 .env

# 设置配置文件权限
chmod 600 config.ini
```

## 7. 生产环境部署

### 安全检查清单
- [ ] 移除调试模式
- [ ] 配置防火墙
- [ ] 启用HTTPS
- [ ] 设置访问日志
- [ ] 配置监控告警
- [ ] 定期安全更新

### 环境隔离
- 开发环境与生产环境分离
- 使用不同的API密钥
- 独立的数据库实例

## 8. 监控和日志

### 安全日志
- 记录访问日志
- 监控异常行为
- 设置告警机制

### 定期检查
- 检查依赖包安全性
- 更新安全补丁
- 审计访问权限

## 9. 备份策略

### 数据备份
- 定期备份数据库
- 备份配置文件
- 测试恢复流程

### 版本控制
- 不提交敏感信息
- 使用 .gitignore 保护
- 定期检查提交历史

## 联系支持
如有安全问题，请联系：tu760979288@gmail.com