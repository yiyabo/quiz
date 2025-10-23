#!/bin/bash

# 蛋白质相互作用预测竞赛平台 - 一键启动脚本

echo "╔══════════════════════════════════════════════════════════╗"
echo "║   🧬 蛋白质相互作用预测竞赛平台                        ║"
echo "║   Protein-Protein Interaction Prediction Platform       ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# 检查是否在项目根目录
if [ ! -f "kaggle_dataset.tar.gz" ]; then
    echo "❌ 错误: 请在项目根目录运行此脚本"
    exit 1
fi

# 启动后端
echo "📡 启动后端服务..."
cd backend
chmod +x run.sh
./run.sh &
BACKEND_PID=$!
cd ..

# 等待后端启动
echo "⏳ 等待后端服务启动..."
sleep 3

# 启动前端
echo ""
echo "🎨 启动前端服务..."
cd frontend
chmod +x run.sh
./run.sh &
FRONTEND_PID=$!
cd ..

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║                   ✅ 服务已启动                         ║"
echo "╠══════════════════════════════════════════════════════════╣"
echo "║  📍 前端地址: http://localhost:3000                     ║"
echo "║  📍 后端地址: http://localhost:8000                     ║"
echo "║  📖 API文档:  http://localhost:8000/docs                ║"
echo "╠══════════════════════════════════════════════════════════╣"
echo "║  按 Ctrl+C 停止所有服务                                 ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# 等待用户中断
wait

