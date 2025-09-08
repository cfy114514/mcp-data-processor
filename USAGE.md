# 数据查询MCP服务器使用说明

## 概述

这是一个基于MCP (Model Context Protocol) 的数据查询服务器，提供用户、产品、订单数据的查询和分析功能。服务器支持通过WebSocket连接到小智AI平台。

## 可用工具 (Available Tools)

### 1. query_users(filter_by, value)
查询用户数据，支持按字段过滤。

**参数：**
- `filter_by` (可选): 过滤字段名，如 'department', 'city', 'age'
- `value` (可选): 过滤值

**示例：**
```python
# 查询所有用户
query_users()

# 查询技术部用户
query_users("department", "技术部")

# 查询北京用户
query_users("city", "北京")
```

### 2. query_products(filter_by, value)
查询产品数据，支持按字段过滤。

**参数：**
- `filter_by` (可选): 过滤字段名，如 'category', 'price_range'
- `value` (可选): 过滤值

**示例：**
```python
# 查询所有产品
query_products()

# 查询电子产品
query_products("category", "电子产品")

# 查询价格范围 100-500 的产品
query_products("price_range", "100-500")
```

### 3. query_orders(filter_by, value)
查询订单数据，支持按字段过滤。

**参数：**
- `filter_by` (可选): 过滤字段名，如 'user_id', 'product_id', 'date'
- `value` (可选): 过滤值

**示例：**
```python
# 查询所有订单
query_orders()

# 查询用户ID=1的订单
query_orders("user_id", "1")

# 查询特定产品的订单
query_orders("product_id", "2")
```

### 4. get_user_orders(user_id)
获取指定用户的所有订单信息，包含用户详情和订单详情。

**参数：**
- `user_id` (必需): 用户ID

**示例：**
```python
# 获取用户ID=1的所有订单
get_user_orders(1)
```

### 5. get_statistics()
获取数据统计信息，包括用户、产品、订单的统计数据。

**示例：**
```python
# 获取统计信息
get_statistics()
```

## 数据结构

### 用户数据
```json
{
  "id": 1,
  "name": "张三",
  "age": 28,
  "city": "北京",
  "department": "技术部"
}
```

### 产品数据
```json
{
  "id": 1,
  "name": "笔记本电脑",
  "price": 5999,
  "category": "电子产品",
  "stock": 50
}
```

### 订单数据
```json
{
  "id": 1,
  "user_id": 1,
  "product_id": 1,
  "quantity": 1,
  "total": 5999,
  "date": "2024-01-15"
}
```

## 配置说明

### WebSocket端点配置
在 `mcp_config.json` 中已配置小智AI的WebSocket端点：

```json
{
  "mcpServers": {
    "xiaozhi-websocket-server": {
      "type": "websocket",
      "url": "wss://api.xiaozhi.me/mcp/?token=your_token_here",
      "description": "小智 AI WebSocket MCP 服务器连接"
    }
  }
}
```

### 环境变量
```bash
MCP_ENDPOINT=wss://api.xiaozhi.me/mcp/?token=your_token_here
MCP_CONFIG=./mcp_config.json
```

## 启动方式

### Windows
```powershell
.\start.ps1
```

### Linux/Mac
```bash
./start.sh
```

### 手动启动
```bash
# 设置环境变量
export MCP_ENDPOINT="wss://api.xiaozhi.me/mcp/?token=your_token_here"

# 启动服务器
python mcp_pipe.py
```

## 测试

运行测试脚本验证功能：
```bash
python test_server.py
```

## 注意事项

1. 确保已安装所有依赖包：`pip install -r requirements.txt`
2. 需要有效的小智AI访问令牌
3. WebSocket连接需要网络访问权限
4. 服务器支持自动重连机制
