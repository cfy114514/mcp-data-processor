# 数据查询 MCP 服务器 | Data Query MCP Server

一个强大的MCP (Model Context Protocol) 服务器，提供用户、产品、订单数据的查询功能，支持WebSocket连接到小智AI平台。

A powerful MCP (Model Context Protocol) server that provides user, product, and order data querying capabilities with WebSocket support for XiaoZhi AI platform.

## 概述 | Overview

本项目实现了一个数据查询MCP服务器，包含以下功能：
- 用户数据查询和过滤
- 产品数据查询和过滤  
- 订单数据查询和分析
- 用户订单关联查询
- 数据统计分析

This project implements a data query MCP server with the following features:
- User data querying and filtering
- Product data querying and filtering
- Order data querying and analysis
- User-order association queries
- Data statistics analysis

## 特性 | Features

- 🔌 支持WebSocket连接到小智AI平台 | WebSocket connection to XiaoZhi AI platform
- 🔄 自动重连机制 | Automatic reconnection with exponential backoff
- 📊 实时数据查询 | Real-time data querying
- 🛠️ 简单易用的工具接口 | Easy-to-use tool interface
- 🔒 安全的WebSocket通信 | Secure WebSocket communication
- ⚙️ 多种传输类型支持 | Multiple transport types support (stdio/websocket/sse/http)

## 快速开始 | Quick Start

### 方法1: 使用启动脚本 | Method 1: Using Startup Scripts

**Windows PowerShell:**
```powershell
.\start.ps1
```

**Linux/Mac 标准脚本 | Linux/Mac Standard Script:**
```bash
chmod +x start.sh
./start.sh
```

**Linux/Mac 简化脚本 | Linux/Mac Simple Script:**
```bash
chmod +x start_simple.sh
./start_simple.sh
```

### 方法2: 服务器部署 | Method 2: Server Deployment

**自动部署（推荐用于服务器）| Auto Deployment (Recommended for Servers):**
```bash
chmod +x deploy.sh
./deploy.sh
```

**手动部署 | Manual Deployment:**
参考 `MANUAL_START.md` 文件获取详细步骤。

### 方法3: 系统服务 | Method 3: System Service

**Linux系统服务 | Linux System Service:**
```bash
# 1. 编辑服务文件
sudo cp mcp-server.service /etc/systemd/system/
sudo nano /etc/systemd/system/mcp-server.service

# 2. 启动服务
sudo systemctl daemon-reload
sudo systemctl enable mcp-server
sudo systemctl start mcp-server

# 3. 查看状态
sudo systemctl status mcp-server
```

### 方法4: 手动设置 | Method 4: Manual Setup

1. **安装依赖 | Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **设置环境变量 | Set environment variables:**

**Windows PowerShell:**
```powershell
$env:MCP_ENDPOINT = "wss://api.xiaozhi.me/mcp/?token=your_token_here"
$env:MCP_CONFIG = "./mcp_config.json"
```

**Linux/Mac Bash:**
```bash
export MCP_ENDPOINT="wss://api.xiaozhi.me/mcp/?token=your_token_here"
export MCP_CONFIG="./mcp_config.json"
```

3. **启动服务器 | Start the server:**
```bash
# 运行所有配置的服务器 | Run all configured servers
python mcp_pipe.py

# 或单独运行数据查询服务器 | Or run data query server individually  
python mcp_pipe.py data_query_server.py
```

## 项目结构 | Project Structure

- `data_query_server.py`: 数据查询MCP服务器，提供用户、产品、订单查询功能 | Data query MCP server with user, product, and order querying
- `mcp_pipe.py`: WebSocket连接和进程管理的主通信管道 | Main communication pipe handling WebSocket connections and process management
- `mcp_config.json`: 服务器配置文件 | Server configuration file
- `requirements.txt`: Python依赖包列表 | Python dependencies list
- `.env`: 环境变量配置文件 | Environment variables configuration
- `start.ps1`: Windows PowerShell启动脚本 | Windows PowerShell startup script
- `start.sh`: Linux/Mac Bash启动脚本 | Linux/Mac Bash startup script
- `calculator.py`: Example MCP tool implementation for mathematical calculations | 用于数学计算的MCP工具示例实现
- `requirements.txt`: Project dependencies | 项目依赖

## Config-driven Servers | 通过配置驱动的服务

编辑 `mcp_config.json` 文件来配置服务器列表（也可设置 `MCP_CONFIG` 环境变量指向其他配置文件）。

配置说明：
- 无参数时启动所有配置的服务（自动跳过 `disabled: true` 的条目）
- 有参数时运行单个本地脚本文件
- `type=stdio` 直接启动；`type=sse/http` 通过 `python -m mcp_proxy` 代理

## Creating Your Own MCP Tools | 创建自己的MCP工具

Here's a simple example of creating an MCP tool | 以下是一个创建MCP工具的简单示例:

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("YourToolName")

@mcp.tool()
def your_tool(parameter: str) -> dict:
    """Tool description here"""
    # Your implementation
    return {"success": True, "result": result}

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

## Use Cases | 使用场景

- Mathematical calculations | 数学计算
- Email operations | 邮件操作
- Knowledge base search | 知识库搜索
- Remote device control | 远程设备控制
- Data processing | 数据处理
- Custom tool integration | 自定义工具集成

## Requirements | 环境要求

- Python 3.7+
- websockets>=11.0.3
- python-dotenv>=1.0.0
- mcp>=1.8.1
- pydantic>=2.11.4
- mcp-proxy>=0.8.2

## Contributing | 贡献指南

Contributions are welcome! Please feel free to submit a Pull Request.

欢迎贡献代码！请随时提交Pull Request。

## License | 许可证

This project is licensed under the MIT License - see the LICENSE file for details.

本项目采用MIT许可证 - 详情请查看LICENSE文件。

## Acknowledgments | 致谢

- Thanks to all contributors who have helped shape this project | 感谢所有帮助塑造这个项目的贡献者
- Inspired by the need for extensible AI capabilities | 灵感来源于对可扩展AI能力的需求
