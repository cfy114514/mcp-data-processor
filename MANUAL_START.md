# 手动启动指南 - Linux/Unix服务器

## 如果启动脚本无法运行，请按以下步骤手动启动：

### 步骤1: 检查Python环境
```bash
# 检查Python版本（需要3.7+）
python3 --version
# 或者
python --version

# 检查pip
pip3 --version
# 或者
pip --version
```

### 步骤2: 安装依赖包
```bash
# 使用pip3（推荐）
pip3 install -r requirements.txt

# 或使用pip
pip install -r requirements.txt

# 手动安装核心依赖（如果上面失败）
pip3 install mcp websockets pydantic python-dotenv mcp-proxy
```

### 步骤3: 设置环境变量
```bash
# 设置WebSocket端点
export MCP_ENDPOINT="wss://api.xiaozhi.me/mcp/?token=eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOjMyMzM0NywiYWdlbnRJZCI6NTUyNTUyLCJlbmRwb2ludElkIjoiYWdlbnRfNTUyNTUyIiwicHVycG9zZSI6Im1jcC1lbmRwb2ludCIsImlhdCI6MTc1NzI5NzYxMn0.Qw66VsLooShlL_sA9wD-oiKdcIzRpQrtt5AaleHM7l--DM-3IiMaMfOQp3hD1hZXK0Aq2ydkXjYGtUgugPZsAQ"

# 设置配置文件路径
export MCP_CONFIG="./mcp_config.json"
```

### 步骤4: 启动服务器
```bash
# 方法1: 使用python3
python3 mcp_pipe.py

# 方法2: 使用python（如果python3不可用）
python mcp_pipe.py

# 方法3: 直接运行数据查询服务器（仅本地测试）
python3 data_query_server.py
```

## 权限问题解决

如果遇到权限错误：

```bash
# 给脚本添加执行权限
chmod +x start.sh
chmod +x start_simple.sh

# 或者直接用bash运行
bash start.sh
bash start_simple.sh
```

## 常见问题排查

### 1. Python版本问题
```bash
# 如果系统Python版本过低，安装新版本
# Ubuntu/Debian:
sudo apt update
sudo apt install python3 python3-pip

# CentOS/RHEL:
sudo yum install python3 python3-pip
# 或
sudo dnf install python3 python3-pip
```

### 2. pip安装问题
```bash
# 更新pip
pip3 install --upgrade pip

# 使用国内源加速（中国用户）
pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

### 3. 网络连接问题
```bash
# 测试网络连接
curl -I https://api.xiaozhi.me/

# 检查防火墙设置
# 确保允许WebSocket连接（端口443）
```

### 4. 文件编码问题
```bash
# 如果看到乱码，转换文件编码
iconv -f utf-8 -t ascii//IGNORE start.sh > start_ascii.sh
chmod +x start_ascii.sh
./start_ascii.sh
```

## 验证服务器运行

成功启动后，你应该看到类似的输出：
```
Starting Data Query MCP Server...
INFO - Starting servers: data-query-server
INFO - Successfully connected to WebSocket server
INFO - Processing request of type ListToolsRequest
```

## 停止服务器

按 `Ctrl+C` 停止服务器

## 后台运行

如果需要后台运行：
```bash
# 使用nohup
nohup python3 mcp_pipe.py > mcp_server.log 2>&1 &

# 使用screen
screen -S mcp_server
python3 mcp_pipe.py
# 按Ctrl+A然后按D分离会话

# 使用systemd（需要root权限）
# 创建服务文件 /etc/systemd/system/mcp-server.service
```

如果以上所有方法都失败，请提供具体的错误信息以便进一步诊断。
