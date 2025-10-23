#!/bin/bash

echo "🚀 启动后端服务..."
echo ""

cd /Users/apple/work/quiz/backend

# 检查conda环境
if ! conda info --envs | grep -q "quiz"; then
    echo "❌ 错误: conda环境 'quiz' 不存在"
    echo "请先创建环境: conda create -n quiz python=3.9"
    exit 1
fi

echo "📦 使用conda环境: quiz"

# 激活conda环境并运行
source $(conda info --base)/etc/profile.d/conda.sh
conda activate quiz

echo ""
echo "✅ 启动FastAPI服务器..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📍 后端地址: http://localhost:8000"
echo "📖 API文档: http://localhost:8000/docs"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "按 Ctrl+C 停止服务"
echo ""

python main.py

