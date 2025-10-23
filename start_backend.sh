#!/bin/bash

echo "🚀 启动后端服务..."
echo ""

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/backend"

# 检查Python环境
if command -v conda &> /dev/null && conda info --envs | grep -q "quiz"; then
    # 使用conda环境
    echo "📦 使用conda环境: quiz"
    source $(conda info --base)/etc/profile.d/conda.sh
    conda activate quiz
elif [ -d "venv" ]; then
    # 使用虚拟环境
    echo "📦 使用虚拟环境: venv"
    source venv/bin/activate
else
    # 使用系统Python
    echo "📦 使用系统Python"
    if ! command -v python3 &> /dev/null; then
        echo "❌ 错误: 未找到Python3"
        exit 1
    fi
fi

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

