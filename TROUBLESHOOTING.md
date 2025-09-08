# 服务器部署故障排除指南

## 常见问题及解决方案

### 1. 启动脚本权限问题

**问题**: `Permission denied` 或 `bash: ./start.sh: Permission denied`

**解决方案**:
```bash
# 添加执行权限
chmod +x start.sh
chmod +x start_simple.sh
chmod +x deploy.sh

# 或直接用bash运行
bash start.sh
```

### 2. Python版本问题

**问题**: `Python version X.X is not supported`

**解决方案**:
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.8 python3.8-pip python3.8-venv

# CentOS/RHEL 8+
sudo dnf install python3.8 python3.8-pip

# 创建软链接（如果需要）
sudo ln -sf /usr/bin/python3.8 /usr/bin/python3
```

### 3. pip安装失败

**问题**: `pip install` 命令失败

**解决方案**:
```bash
# 更新pip
python3 -m pip install --upgrade pip

# 使用不同源
pip3 install -r requirements.txt -i https://pypi.org/simple/
pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/

# 手动安装核心包
pip3 install mcp==1.8.1 websockets==11.0.3 pydantic==2.11.4
```

### 4. 网络连接问题

**问题**: 无法连接到WebSocket端点

**解决方案**:
```bash
# 测试网络连接
curl -I https://api.xiaozhi.me/
ping api.xiaozhi.me

# 检查防火墙设置
sudo ufw status
sudo iptables -L

# 允许HTTPS流量
sudo ufw allow 443
sudo ufw allow out 443
```

### 5. 虚拟环境问题

**问题**: `venv` 创建失败

**解决方案**:
```bash
# 安装venv模块
sudo apt install python3-venv  # Ubuntu/Debian
sudo dnf install python3-venv  # Fedora

# 手动创建虚拟环境
python3 -m venv venv --without-pip
source venv/bin/activate
curl https://bootstrap.pypa.io/get-pip.py | python
```

### 6. 依赖包冲突

**问题**: 包版本冲突或依赖问题

**解决方案**:
```bash
# 使用虚拟环境隔离
python3 -m venv clean_env
source clean_env/bin/activate
pip install --upgrade pip

# 逐个安装核心依赖
pip install websockets==11.0.3
pip install pydantic==2.11.4
pip install mcp==1.8.1
pip install python-dotenv
pip install mcp-proxy==0.8.2
```

### 7. 端口或进程问题

**问题**: 端口被占用或进程冲突

**解决方案**:
```bash
# 查找占用端口的进程
sudo netstat -tulpn | grep :端口号
sudo lsof -i :端口号

# 杀死占用进程
sudo kill -9 PID

# 查找MCP相关进程
ps aux | grep mcp
ps aux | grep python
```

### 8. 日志和调试

**查看详细日志**:
```bash
# 直接运行查看错误
python3 mcp_pipe.py

# 后台运行并记录日志
nohup python3 mcp_pipe.py > mcp_server.log 2>&1 &

# 实时查看日志
tail -f mcp_server.log

# 系统服务日志
sudo journalctl -u mcp-server -f
```

### 9. 环境变量问题

**问题**: 环境变量未正确设置

**解决方案**:
```bash
# 检查环境变量
echo $MCP_ENDPOINT
echo $MCP_CONFIG

# 永久设置环境变量
echo 'export MCP_ENDPOINT="wss://api.xiaozhi.me/mcp/?token=your_token"' >> ~/.bashrc
echo 'export MCP_CONFIG="./mcp_config.json"' >> ~/.bashrc
source ~/.bashrc

# 或创建.env文件
cat > .env << EOF
MCP_ENDPOINT=wss://api.xiaozhi.me/mcp/?token=your_token
MCP_CONFIG=./mcp_config.json
EOF
```

### 10. 系统资源问题

**问题**: 内存不足或CPU过载

**解决方案**:
```bash
# 检查系统资源
free -h
top
htop

# 调整Python进程优先级
nice -n 10 python3 mcp_pipe.py

# 限制内存使用
ulimit -v 1048576  # 限制为1GB
```

## 完全重置方案

如果所有方法都失败，尝试完全重置：

```bash
# 1. 清理现有环境
rm -rf venv/
rm -rf __pycache__/
rm -f *.log

# 2. 重新部署
./deploy.sh

# 3. 或手动重新安装
python3 -m venv fresh_env
source fresh_env/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 4. 测试基本功能
python3 -c "import mcp, websockets, pydantic; print('OK')"
python3 test_server.py
```

## 获取帮助

如果问题仍然存在，请提供以下信息：

1. 操作系统版本: `cat /etc/os-release`
2. Python版本: `python3 --version`
3. pip版本: `pip3 --version`
4. 错误日志: 完整的错误信息
5. 网络状况: `curl -I https://api.xiaozhi.me/`

将这些信息提供给技术支持以获得进一步帮助。
