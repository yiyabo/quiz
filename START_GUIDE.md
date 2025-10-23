# 🚀 快速启动指南

## 第一次启动（需要安装依赖）

### 步骤1: 安装后端依赖

打开终端，执行：

```bash
cd /Users/apple/work/quiz/backend
conda activate quiz
pip install -r requirements.txt
```

### 步骤2: 安装前端依赖

打开**新的**终端窗口，执行：

```bash
cd /Users/apple/work/quiz/frontend
npm install
```

---

## 每次启动服务

### 启动后端

在终端1中执行：

```bash
cd /Users/apple/work/quiz/backend
conda activate quiz
python3 main.py
```

看到以下信息表示启动成功：
```
✅ 数据库初始化完成
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**保持这个终端窗口运行，不要关闭！**

### 启动前端

在**新的**终端2中执行：

```bash
cd /Users/apple/work/quiz/frontend
npm run dev
```

看到以下信息表示启动成功：
```
  ➜  Local:   http://localhost:3000/
```

**保持这个终端窗口运行，不要关闭！**

---

## 访问平台

打开浏览器，访问：**http://localhost:3000**

---

## 停止服务

在各个终端窗口中按 `Ctrl + C` 停止服务

---

## 常见问题

### Q: 提示端口被占用怎么办？

**后端端口8000被占用：**
```bash
# 查找占用进程
lsof -i :8000
# 杀死进程（替换<PID>为实际进程号）
kill -9 <PID>
```

**前端端口3000被占用：**
```bash
# 查找占用进程
lsof -i :3000
# 杀死进程
kill -9 <PID>
```

### Q: 找不到模块怎么办？

确保conda环境已激活：
```bash
conda activate quiz
```

重新安装依赖：
```bash
cd /Users/apple/work/quiz/backend
pip install -r requirements.txt
```

### Q: 数据库报错怎么办？

删除数据库文件重新初始化：
```bash
rm /Users/apple/work/quiz/backend/quiz_platform.db
```

然后重新启动后端服务。

---

## 快速测试

1. 访问 http://localhost:3000
2. 点击"注册"创建账号
3. 登录后下载数据集
4. 查看排行榜
5. 提交预测文件测试

---

## 重要提示

✅ 必须同时启动后端和前端
✅ 两个终端窗口都要保持运行
✅ 确保conda环境quiz已创建并激活
✅ 第一次启动需要先安装依赖

---

祝使用愉快！🎉

