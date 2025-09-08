# Python命令问题解决方案

## 问题诊断

错误信息 `[Errno 2] No such file or directory: 'python'` 表明系统找不到 `python` 命令。

这在Linux/Unix系统上很常见，因为Python 3通常安装为 `python3` 而不是 `python`。

## 解决方案（按推荐顺序）

### 方案1: 使用自动配置的简单启动脚本 ⭐⭐⭐

```bash
chmod +x start_simple.sh
./start_simple.sh
```

这个脚本会：
- 自动检测正确的Python命令
- 自动更新配置文件
- 安装依赖包
- 启动服务器

### 方案2: 使用直接启动模式 ⭐⭐⭐

```bash
chmod +x start_direct.sh
./start_direct.sh
```

这种方式完全绕过配置文件，直接运行服务器。

### 方案3: 手动配置后启动

```bash
# 1. 运行配置脚本
chmod +x setup_config.sh
./setup_config.sh

# 2. 启动服务器
chmod +x start.sh
./start.sh
```

### 方案4: 完全手动方式

```bash
# 1. 检查Python命令
if command -v python3 >/dev/null 2>&1; then
    PYTHON="python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON="python"
else
    echo "Python not found"
    exit 1
fi

# 2. 设置环境变量
export MCP_ENDPOINT="wss://api.xiaozhi.me/mcp/?token=your_token"

# 3. 直接运行
$PYTHON mcp_pipe.py data_query_server.py
```

## 快速诊断命令

检查您的系统上可用的Python命令：

```bash
# 检查python3
which python3
python3 --version

# 检查python
which python
python --version

# 检查所有Python相关命令
ls -la /usr/bin/python*
```

## 推荐操作

对于大多数Linux服务器，我推荐：

1. **首选**: 使用 `start_direct.sh`（最简单，最可靠）
2. **备选**: 使用更新后的 `start_simple.sh`
3. **兜底**: 手动设置环境变量并直接运行

## 示例输出

成功启动后您应该看到：

```
Starting MCP Server (Direct Mode)...
Using: python3
Starting server directly...
INFO - Starting servers: data-query-server
INFO - Successfully connected to WebSocket server
INFO - Processing request of type ListToolsRequest
```

## 如果仍有问题

请运行诊断命令并提供输出：

```bash
echo "=== Python Diagnostic ==="
which python3 2>/dev/null || echo "python3 not found"
which python 2>/dev/null || echo "python not found"
python3 --version 2>/dev/null || echo "python3 version check failed"
python --version 2>/dev/null || echo "python version check failed"
echo "=== End Diagnostic ==="
```
