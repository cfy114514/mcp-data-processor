# MCP架构说明

## 当前架构

这个项目使用以下架构连接到小智AI平台：

```
小智AI平台 <-- WebSocket --> mcp_pipe.py <-- stdio --> data_query_server.py
```

### 组件说明

1. **data_query_server.py** - 数据查询MCP服务器
   - 提供5个数据查询工具
   - 通过stdio与mcp_pipe.py通信

2. **main_mcp_simulator.py** - 瑞维亚记忆之旅游戏服务器
   - 提供互动式故事游戏功能
   - 支持场景探索和角色对话
   - 包含5个游戏工具

3. **mcp_pipe.py** - WebSocket通信管道
   - 连接到小智AI WebSocket端点
   - 将WebSocket消息转换为stdio通信
   - 管理多个MCP服务器进程

4. **小智AI平台** - 远程AI服务
   - 通过WebSocket接收MCP工具调用
   - 处理AI查询并调用相应工具

### 配置说明

- **MCP_ENDPOINT** 环境变量：指定小智AI WebSocket端点
- **mcp_config.json**：配置本地MCP服务器（stdio模式）

### 支持的传输类型

- `stdio` - 标准输入输出（用于本地MCP服务器）
- `sse` - Server-Sent Events
- `http` - HTTP API
- `streamablehttp` - 流式HTTP

**注意**：直接的`websocket`类型不被支持，WebSocket连接通过`MCP_ENDPOINT`环境变量配置。

## 工作流程

1. 启动脚本设置`MCP_ENDPOINT`环境变量
2. `mcp_pipe.py`读取环境变量并连接到WebSocket端点
3. `mcp_pipe.py`启动本地MCP服务器(`data_query_server.py`和`main_mcp_simulator.py`)
4. 小智AI通过WebSocket发送工具调用请求
5. `mcp_pipe.py`将请求转发给相应的本地服务器
6. 本地服务器处理请求并返回结果
7. `mcp_pipe.py`将结果通过WebSocket返回给小智AI

## 可用工具

### 数据查询服务器工具
- `query_users()` - 查询用户数据
- `query_products()` - 查询产品数据  
- `query_orders()` - 查询订单数据
- `get_user_orders(user_id)` - 获取用户订单详情
- `get_statistics()` - 获取数据统计信息

### 瑞维亚记忆之旅游戏工具
- `start_journey()` - 开始游戏
- `talk_to_rivia(message)` - 与瑞维亚对话
- `get_game_state()` - 获取游戏状态
- `get_story_progress()` - 获取故事进度
- `reset_game()` - 重置游戏状态

## 测试状态

✅ **成功** - 数据查询服务器正常运行
✅ **成功** - 瑞维亚记忆之旅游戏服务器正常运行
✅ **成功** - WebSocket连接建立
✅ **成功** - 工具调用请求被正确处理
✅ **成功** - 返回查询结果给小智AI平台
