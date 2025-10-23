#!/bin/bash

echo "🎨 启动前端服务..."
echo ""

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/frontend"

# 检查node_modules
if [ ! -d "node_modules" ]; then
    echo "📦 首次运行，安装依赖..."
    npm install
    echo ""
fi

echo "✅ 启动Vite开发服务器..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📍 前端地址: http://localhost:3000"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "按 Ctrl+C 停止服务"
echo ""

npm run dev

