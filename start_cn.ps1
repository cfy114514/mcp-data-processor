# 数据查询MCP服务器启动脚本 (Windows PowerShell)
# 编码：UTF-8 with BOM

# 设置环境变量
$env:MCP_ENDPOINT = "wss://api.xiaozhi.me/mcp/?token=eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOjMyMzM0NywiYWdlbnRJZCI6NTUyNTUyLCJlbmRwb2ludElkIjoiYWdlbnRfNTUyNTUyIiwicHVycG9zZSI6Im1jcC1lbmRwb2ludCIsImlhdCI6MTc1NzI5NzYxMn0.Qw66VsLooShlL_sA9wD-oiKdcIzRpQrtt5AaleHM7l--DM-3IiMaMfOQp3hD1hZXK0Aq2ydkXjYGtUgugPZsAQ"
$env:MCP_CONFIG = "./mcp_config.json"

Write-Host "正在启动数据查询MCP服务器..." -ForegroundColor Green
Write-Host "端点地址: $env:MCP_ENDPOINT" -ForegroundColor Yellow

# 检查Python是否可用
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "错误: 未找到Python。请确保Python已安装并添加到PATH。" -ForegroundColor Red
    Read-Host "按任意键退出"
    exit 1
}

# 检查依赖包
Write-Host "检查Python依赖包..." -ForegroundColor Blue
$checkResult = python -c "import mcp, websockets, pydantic; print('OK')" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "正在安装依赖包..." -ForegroundColor Blue
    pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "依赖包安装失败！" -ForegroundColor Red
        Read-Host "按任意键退出"
        exit 1
    }
}

# 启动MCP服务器
Write-Host "启动MCP管道服务器..." -ForegroundColor Green
Write-Host "按 Ctrl+C 停止服务器" -ForegroundColor Yellow
python mcp_pipe.py
