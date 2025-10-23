#!/bin/bash

# 生物数据竞赛平台 - 前端启动脚本

echo "🎨 启动前端服务..."

# 检查Node.js是否安装
if ! command -v node &> /dev/null; then
    echo "❌ 错误: 未找到Node.js，请先安装Node.js 16+"
    exit 1
fi

# 检查npm是否安装
if ! command -v npm &> /dev/null; then
    echo "❌ 错误: 未找到npm"
    exit 1
fi

# 检查node_modules是否存在
if [ ! -d "node_modules" ]; then
    echo "📦 安装依赖包..."
    npm install
fi

# 启动开发服务器
echo "✅ 启动Vite开发服务器..."
echo "📍 前端地址: http://localhost:3000"
echo ""
npm run dev
