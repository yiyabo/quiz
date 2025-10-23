#!/bin/bash

# 蛋白质相互作用预测竞赛平台 - 后端启动脚本

echo "🚀 启动后端服务..."

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到Python3，请先安装Python 3.8+"
    exit 1
fi

# 检查虚拟环境是否存在
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "📥 安装依赖包..."
pip install -r requirements.txt

# 启动服务
echo "✅ 启动FastAPI服务器..."
echo "📍 API地址: http://localhost:8000"
echo "📖 API文档: http://localhost:8000/docs"
echo ""
python3 main.py

