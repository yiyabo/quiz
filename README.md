# 🧬 蛋白质相互作用预测竞赛平台

一个仿Kaggle的机器学习竞赛平台，用于蛋白质相互作用预测任务。

## 📋 项目简介

这是一个完整的机器学习竞赛平台，包含：
- ✅ 用户注册/登录系统
- ✅ 数据集下载
- ✅ CSV文件提交
- ✅ 自动评分系统
- ✅ 实时排行榜
- ✅ 个人提交历史
- ✅ 现代化Web界面

## 🏗️ 技术栈

### 后端
- **FastAPI** - 现代、高性能的Python Web框架
- **SQLAlchemy** - ORM数据库操作
- **SQLite** - 轻量级数据库
- **JWT** - 用户认证
- **Pandas** - 数据处理
- **scikit-learn** - 评分指标计算

### 前端
- **Vue 3** - 渐进式JavaScript框架
- **Element Plus** - 优秀的Vue 3组件库
- **Vite** - 下一代前端构建工具
- **Pinia** - Vue 3状态管理
- **Axios** - HTTP客户端

## 📁 项目结构

```
quiz/
├── backend/                    # 后端代码
│   ├── main.py                # FastAPI主应用
│   ├── database.py            # 数据库模型
│   ├── auth.py                # 用户认证
│   ├── schemas.py             # Pydantic模型
│   ├── scoring.py             # PPI评分系统
│   ├── scoring_cci.py         # CCI评分系统
│   └── requirements.txt       # Python依赖
├── frontend/                   # 前端代码
│   ├── src/
│   │   ├── views/             # 页面组件
│   │   ├── components/        # 公共组件
│   │   ├── api/               # API接口
│   │   ├── stores/            # 状态管理
│   │   └── router/            # 路由配置
│   └── package.json           # npm依赖
├── kaggle_dataset/             # PPI竞赛数据集
├── cci test/                   # CCI竞赛数据集
├── teacher_only/               # 评分答案文件
├── submissions/                # 提交文件存储
├── start_backend.sh            # 后端启动脚本
├── start_frontend.sh           # 前端启动脚本
└── README.md                   # 本文件
```

## 🚀 快速启动

### 前置要求

- Python 3.8+ (需要 conda 环境)
- Node.js 16+

### 启动步骤

**1. 启动后端**（终端1）

```bash
./start_backend.sh
```

看到 `Uvicorn running on http://0.0.0.0:8000` 表示成功。

**2. 启动前端**（终端2）

```bash
./start_frontend.sh
```

看到 `Local: http://localhost:3000/` 表示成功。

**3. 访问平台**

打开浏览器访问：`http://localhost:3000`

## 📖 使用说明

### 学生使用流程

1. **访问平台**
   - 打开浏览器访问 `http://localhost:3000`

2. **注册账号**
   - 点击"注册"按钮
   - 填写用户名、邮箱和密码
   - 提交注册

3. **下载数据集**
   - 登录后在首页点击"下载数据集"
   - 获取 `kaggle_dataset.tar.gz` 文件
   - 解压后包含训练集、验证集和测试集

4. **训练模型**
   - 使用 `train.csv` 训练你的模型
   - 使用 `valid.csv` 验证模型性能
   - 参考 `README.md` 了解数据格式和评分标准

5. **生成预测**
   - 对 `test.csv` 中的样本进行预测
   - 生成符合格式要求的 `submission.csv`
   - 格式示例：
     ```csv
     protein_A,protein_B,prediction
     9606.ENSP00000178640,9606.ENSP00000256458,1
     9606.ENSP00000253727,9606.ENSP00000257724,0
     ...
     ```

6. **提交结果**
   - 在平台上点击"提交"
   - 上传你的 `submission.csv` 文件
   - 系统会自动评分并显示结果

7. **查看排名**
   - 在"排行榜"页面查看你的排名
   - 在"个人中心"查看提交历史和得分趋势

### 评分标准

最终得分采用**加权多指标**评分：

| 指标 | 权重 | 说明 |
|-----|------|------|
| **Accuracy** | 30% | 预测正确的比例 |
| **Precision** | 20% | 预测为正样本中真正为正的比例 |
| **Recall** | 20% | 真正样本中被正确预测的比例 |
| **F1-Score** | 30% | Precision和Recall的调和平均 |

**计算公式：**
```
Final Score = Accuracy × 0.3 + Precision × 0.2 + Recall × 0.2 + F1 × 0.3
```

得分范围: 0.0 ~ 1.0 (越高越好)

## 🔧 开发说明

### 后端开发

```bash
cd backend

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 运行开发服务器
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

访问 API 文档: `http://localhost:8000/docs`

### 前端开发

```bash
cd frontend

# 安装依赖
npm install

# 运行开发服务器
npm run dev

# 构建生产版本
npm run build
```

## 📊 API接口

### 用户认证
- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `GET /api/auth/me` - 获取当前用户信息

### 提交管理
- `POST /api/submissions` - 提交预测文件
- `GET /api/submissions/me` - 获取我的提交历史
- `GET /api/submissions/{id}` - 获取提交详情

### 排行榜
- `GET /api/leaderboard` - 获取排行榜

### 统计信息
- `GET /api/statistics` - 获取平台统计

### 数据下载
- `GET /api/download/dataset` - 下载数据集

## 🎯 主要功能

### ✅ 已实现功能

1. **用户系统**
   - 用户注册/登录
   - JWT令牌认证
   - 用户信息管理

2. **提交系统**
   - CSV文件上传
   - 文件格式验证
   - 自动评分
   - 提交历史记录
   - 无提交次数限制

3. **排行榜**
   - 实时排名计算
   - 最佳成绩展示
   - 前三名特殊展示
   - 用户提交统计

4. **个人中心**
   - 提交历史时间线
   - 得分趋势图
   - 个人统计数据
   - 最佳提交标记

5. **美观的UI**
   - 响应式设计
   - 现代化界面
   - 流畅的交互体验

## 📝 数据集说明

### 文件列表

- `train.csv` - 训练集 (11,436个样本，含标签)
- `valid.csv` - 验证集 (2,287个样本，含标签)
- `test.csv` - 测试集 (1,525个样本，无标签)
- `sample_submission.csv` - 提交格式示例

### 数据格式

**训练集/验证集：**
```csv
protein_A,protein_B,sequence_A,sequence_B,label
9606.ENSP00000000233,9606.ENSP00000019317,MGLTVSALFS...,MTECFLPPTS...,1
```

**测试集：**
```csv
protein_A,protein_B,sequence_A,sequence_B
9606.ENSP00000178640,9606.ENSP00000256458,MLWLALGPFP...,MACYIYQLPS...
```

**提交文件：**
```csv
protein_A,protein_B,prediction
9606.ENSP00000178640,9606.ENSP00000256458,1
```

## 🚀 部署到服务器

### 使用Nginx + Uvicorn

1. **后端部署**

```bash
# 安装依赖
cd backend
pip install -r requirements.txt

# 使用gunicorn运行
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

2. **前端部署**

```bash
# 构建前端
cd frontend
npm run build

# dist目录中的文件部署到Nginx
```

3. **Nginx配置示例**

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端
    location / {
        root /path/to/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # 后端API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 使用Docker (可选)

如果需要Docker部署，可以创建 `Dockerfile` 和 `docker-compose.yml`。

## 🐛 故障排除

### 后端问题

1. **端口被占用**
   ```bash
   # 查找占用8000端口的进程
   lsof -i :8000
   # 杀死进程
   kill -9 <PID>
   ```

2. **数据库错误**
   ```bash
   # 删除数据库文件重新初始化
   rm backend/quiz_platform.db
   ```

### 前端问题

1. **依赖安装失败**
   ```bash
   # 清除缓存重新安装
   rm -rf node_modules package-lock.json
   npm install
   ```

2. **端口被占用**
   ```bash
   # 修改 vite.config.js 中的端口号
   ```

## 📄 License

MIT License

## 👥 联系方式

如有问题，请联系管理员。

---

**祝你在竞赛中取得好成绩！🎉**

