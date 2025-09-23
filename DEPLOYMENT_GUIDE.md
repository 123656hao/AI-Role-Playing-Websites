# 🚀 AI角色扮演聊天网站 - 部署和维护指南

## 📅 文档版本
**更新时间**: 2025年9月23日  
**项目版本**: v2.0 实时语音交互版

## 🎯 部署概述

本项目支持多种部署方式，从本地开发到生产环境部署，提供完整的解决方案。

## 🏠 本地开发部署

### 环境要求
- **Python**: 3.8+ (推荐3.9+)
- **操作系统**: Windows 10+, macOS 10.15+, Ubuntu 18.04+
- **内存**: 最小2GB，推荐4GB+
- **存储**: 最小1GB可用空间

### 快速部署
```bash
# 1. 克隆项目
git clone <repository-url>
cd AI-Role-Playing-Websites

# 2. 恢复环境
# Windows
restore_environment.bat
# PowerShell
.\restore_environment.ps1

# 3. 启动应用
.venv\Scripts\activate  # Windows
python app.py

# 访问应用
# 主应用: http://localhost:5000
# 演示页面: http://localhost:5000/demo
```

### 配置检查
```bash
# 运行配置检查
python check_config.py

# 测试API连接
python test_api.py
```

## 🌐 生产环境部署

### 1. 服务器要求
- **CPU**: 2核心以上
- **内存**: 4GB以上
- **存储**: 10GB以上
- **网络**: 稳定的互联网连接
- **端口**: 5000 (Flask), 8765 (WebSocket)

### 2. 使用Gunicorn部署

#### 安装Gunicorn
```bash
pip install gunicorn gevent-websocket
```

#### 创建Gunicorn配置
```python
# gunicorn_config.py
bind = "0.0.0.0:5000"
workers = 4
worker_class = "gevent"
worker_connections = 1000
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
preload_app = True
```

#### 启动服务
```bash
gunicorn -c gunicorn_config.py app:app
```

### 3. 使用Docker部署

#### Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    portaudio19-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 创建必要目录
RUN mkdir -p static/audio logs data

# 暴露端口
EXPOSE 5000 8765

# 启动命令
CMD ["python", "app.py"]
```

#### docker-compose.yml
```yaml
version: '3.8'

services:
  ai-roleplay:
    build: .
    ports:
      - "5000:5000"
      - "8765:8765"
    environment:
      - FLASK_ENV=production
    volumes:
      - ./logs:/app/logs
      - ./static/audio:/app/static/audio
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - ai-roleplay
    restart: unless-stopped
```

#### 部署命令
```bash
# 构建和启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 4. Nginx反向代理配置

```nginx
# nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream app {
        server ai-roleplay:5000;
    }
    
    upstream websocket {
        server ai-roleplay:8765;
    }

    server {
        listen 80;
        server_name your-domain.com;
        
        # HTTP重定向到HTTPS
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name your-domain.com;
        
        # SSL配置
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        
        # 主应用代理
        location / {
            proxy_pass http://app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # WebSocket代理
        location /ws/ {
            proxy_pass http://websocket;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # 静态文件
        location /static/ {
            alias /app/static/;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
}
```

## 🔧 环境变量配置

### 生产环境变量
```env
# 应用配置
FLASK_ENV=production
SECRET_KEY=your-super-secret-key-here
DEBUG=False

# AI API配置
ARK_API_KEY=your-real-api-key
OPENAI_API_BASE=https://ark.cn-beijing.volces.com/api/v3
OPENAI_MODEL=doubao-seed-1-6-250615

# 服务器配置
HOST=0.0.0.0
PORT=5000
WEBSOCKET_PORT=8765

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=/app/logs/app.log

# 安全配置
CORS_ORIGINS=https://your-domain.com
MAX_CONTENT_LENGTH=16777216  # 16MB
```

## 📊 监控和日志

### 1. 应用监控

#### 健康检查端点
```python
@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '2.0',
        'services': {
            'ai_service': 'ok',
            'voice_service': 'ok',
            'websocket': 'ok'
        }
    })
```

#### 系统监控脚本
```bash
#!/bin/bash
# monitor.sh

# 检查应用状态
curl -f http://localhost:5000/health || echo "App health check failed"

# 检查WebSocket
nc -z localhost 8765 || echo "WebSocket port not accessible"

# 检查磁盘空间
df -h | grep -E "/$|/app" | awk '{print $5}' | sed 's/%//' | while read usage; do
    if [ $usage -gt 80 ]; then
        echo "Disk usage is ${usage}%"
    fi
done

# 检查内存使用
free -m | awk 'NR==2{printf "Memory Usage: %s/%sMB (%.2f%%)\n", $3,$2,$3*100/$2 }'
```

### 2. 日志管理

#### 日志配置
```python
import logging
from logging.handlers import RotatingFileHandler

# 配置日志
if not app.debug:
    file_handler = RotatingFileHandler(
        'logs/app.log', 
        maxBytes=10240000, 
        backupCount=10
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
```

#### 日志分析脚本
```bash
#!/bin/bash
# log_analysis.sh

LOG_FILE="/app/logs/app.log"

echo "=== 错误统计 ==="
grep "ERROR" $LOG_FILE | tail -10

echo "=== 访问统计 ==="
grep "GET\|POST" $LOG_FILE | awk '{print $7}' | sort | uniq -c | sort -nr | head -10

echo "=== 响应时间分析 ==="
grep "response_time" $LOG_FILE | awk '{print $NF}' | sort -n | tail -10
```

## 🔒 安全配置

### 1. HTTPS配置
```bash
# 使用Let's Encrypt获取SSL证书
certbot --nginx -d your-domain.com

# 自动续期
echo "0 12 * * * /usr/bin/certbot renew --quiet" | crontab -
```

### 2. 防火墙配置
```bash
# UFW配置
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable
```

### 3. 安全头配置
```python
@app.after_request
def after_request(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response
```

## 🔄 备份和恢复

### 1. 数据备份
```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backup/$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR

# 备份应用数据
cp -r /app/data $BACKUP_DIR/
cp -r /app/config $BACKUP_DIR/
cp -r /app/logs $BACKUP_DIR/

# 备份环境配置
cp /app/.env $BACKUP_DIR/

# 压缩备份
tar -czf $BACKUP_DIR.tar.gz $BACKUP_DIR
rm -rf $BACKUP_DIR

echo "Backup completed: $BACKUP_DIR.tar.gz"
```

### 2. 自动备份
```bash
# 添加到crontab
0 2 * * * /app/scripts/backup.sh
```

## 🚀 性能优化

### 1. 应用优化
- 使用连接池管理API连接
- 实现响应缓存机制
- 优化静态文件服务
- 启用Gzip压缩

### 2. 数据库优化（如果使用）
- 添加适当的索引
- 定期清理过期数据
- 实现读写分离

### 3. 缓存策略
```python
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@cache.memoize(timeout=300)
def get_character_info(character_id):
    # 缓存角色信息
    pass
```

## 🔧 故障排除

### 常见问题

1. **WebSocket连接失败**
   ```bash
   # 检查端口占用
   netstat -tulpn | grep 8765
   
   # 检查防火墙
   ufw status
   ```

2. **API调用失败**
   ```bash
   # 测试API连接
   python test_api.py
   
   # 检查网络连接
   curl -I https://ark.cn-beijing.volces.com
   ```

3. **内存不足**
   ```bash
   # 检查内存使用
   free -h
   
   # 重启应用
   docker-compose restart
   ```

### 日志调试
```bash
# 实时查看日志
tail -f logs/app.log

# 搜索错误
grep -i error logs/app.log

# 分析访问模式
awk '{print $1}' access.log | sort | uniq -c | sort -nr
```

## 📞 维护联系

### 定期维护任务
- [ ] 每日：检查应用状态和日志
- [ ] 每周：更新依赖包和安全补丁
- [ ] 每月：清理日志文件和临时数据
- [ ] 每季度：性能评估和优化

### 紧急联系
- **技术支持**: 查看项目文档和Issue
- **监控告警**: 配置自动化监控和告警
- **备份恢复**: 定期测试备份恢复流程

---

**🎯 遵循本指南可确保AI角色扮演聊天网站的稳定运行和高效维护！**