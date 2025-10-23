"""
FastAPI主应用
"""
import os
import shutil
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import List

from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from database import get_db, init_db, User, Submission, Competition
from schemas import (
    UserCreate, UserLogin, UserResponse, Token,
    SubmissionResponse, SubmissionDetail, LeaderboardEntry, Statistics,
    CompetitionResponse
)
from auth import (
    get_password_hash, authenticate_user, create_access_token, get_current_user
)
from scoring import evaluate_submission
from scoring_cci import evaluate_cci_submission

# 统一的路径设置
BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent
SUBMISSIONS_DIR = ROOT_DIR / "submissions"
UPLOADS_DIR = ROOT_DIR / "uploads"

# 创建必要的目录（与运行目录无关）
SUBMISSIONS_DIR.mkdir(parents=True, exist_ok=True)
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)


def resolve_resource_path(relative_path: str) -> Path:
    """
    将数据库中保存的相对路径转换成项目根目录下的绝对路径。
    只允许访问项目根目录内的资源，避免路径穿越。
    """
    cleaned = Path(relative_path).as_posix().lstrip("/")
    resolved = (ROOT_DIR / cleaned).resolve()

    if ROOT_DIR not in resolved.parents and resolved != ROOT_DIR:
        raise ValueError(f"非法资源路径: {relative_path}")
    return resolved

# 初始化数据库 - 使用lifespan事件
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时执行
    init_db()
    print("✅ 数据库初始化完成")
    yield
    # 关闭时执行（可选）

# 创建FastAPI应用
app = FastAPI(
    title="蛋白质相互作用预测竞赛平台",
    description="迷你Kaggle竞赛平台",
    version="1.0.0",
    lifespan=lifespan
)

# CORS配置 - 允许前端跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== 健康检查 ====================
@app.get("/")
def root():
    return {
        "message": "蛋白质相互作用预测竞赛平台 API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/api/health")
def health_check():
    return {"status": "healthy"}


# ==================== 用户认证 ====================
@app.post("/api/auth/register", response_model=Token)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """用户注册"""
    # 检查用户名是否已存在
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 检查邮箱是否已存在
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已被注册"
        )
    
    # 处理密码长度（bcrypt限制72字节）
    password = user_data.password
    if len(password.encode('utf-8')) > 72:
        password = password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
    
    # 创建新用户
    hashed_password = get_password_hash(password)
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # 生成访问令牌
    access_token = create_access_token(data={"sub": new_user.username})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": new_user
    }


@app.post("/api/auth/login", response_model=Token)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """用户登录"""
    user = authenticate_user(db, user_data.username, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.username})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }


@app.get("/api/auth/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return current_user


# ==================== 竞赛管理 ====================
@app.get("/api/competitions", response_model=List[CompetitionResponse])
def get_competitions(db: Session = Depends(get_db)):
    """获取所有竞赛列表"""
    competitions = db.query(Competition).filter(Competition.is_active == 1).all()
    return competitions


@app.get("/api/competitions/{competition_id}", response_model=CompetitionResponse)
def get_competition(competition_id: int, db: Session = Depends(get_db)):
    """获取单个竞赛详情"""
    competition = db.query(Competition).filter(Competition.id == competition_id).first()
    if not competition:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="竞赛不存在"
        )
    return competition


# ==================== 提交管理 ====================
@app.post("/api/submissions", response_model=SubmissionDetail)
async def submit_prediction(
    competition_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """提交预测结果CSV文件"""
    
    # 验证竞赛是否存在
    competition = db.query(Competition).filter(Competition.id == competition_id).first()
    if not competition:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="竞赛不存在"
        )
    
    # 验证文件类型
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只能上传CSV文件"
        )
    
    # 生成唯一的文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{current_user.username}_{timestamp}_{file.filename}"
    file_path = SUBMISSIONS_DIR / filename
    
    # 保存文件
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件保存失败: {str(e)}"
        )
    
    # 创建提交记录
    submission = Submission(
        user_id=current_user.id,
        competition_id=competition_id,
        filename=filename,
        status="pending"
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)
    
    # 根据竞赛选择评分函数
    try:
        answer_path = resolve_resource_path(competition.answer_path)
        if competition.name == "ppi":
            result = evaluate_submission(str(file_path), str(answer_path))
        elif competition.name == "cci":
            result = evaluate_cci_submission(str(file_path), str(answer_path))
        else:
            raise ValueError(f"未知的竞赛类型: {competition.name}")
        
        if result['status'] == 'success':
            submission.status = 'success'
            submission.accuracy = result['accuracy']
            submission.precision = result['precision']
            submission.recall = result['recall']
            submission.f1_score = result['f1']
            submission.final_score = result['final_score']
            submission.tp = result['tp']
            submission.tn = result['tn']
            submission.fp = result['fp']
            submission.fn = result['fn']
        else:
            submission.status = 'error'
            submission.error_message = result.get('error_message', '未知错误')
        
        db.commit()
        db.refresh(submission)
        
    except Exception as e:
        submission.status = 'error'
        submission.error_message = f"评分失败: {str(e)}"
        db.commit()
        db.refresh(submission)
    
    return submission


@app.get("/api/submissions/me", response_model=List[SubmissionDetail])
def get_my_submissions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 50
):
    """获取当前用户的所有提交记录"""
    submissions = db.query(Submission)\
        .filter(Submission.user_id == current_user.id)\
        .order_by(desc(Submission.submitted_at))\
        .limit(limit)\
        .all()
    
    return submissions


@app.get("/api/submissions/{submission_id}", response_model=SubmissionDetail)
def get_submission(
    submission_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取单个提交的详细信息"""
    submission = db.query(Submission).filter(Submission.id == submission_id).first()
    
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="提交记录不存在"
        )
    
    # 只能查看自己的提交
    if submission.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问此提交记录"
        )
    
    return submission


# ==================== 排行榜 ====================
@app.get("/api/leaderboard", response_model=List[LeaderboardEntry])
def get_leaderboard(
    competition_id: int = None,
    db: Session = Depends(get_db),
    limit: int = 100
):
    """获取排行榜（可按竞赛筛选）"""
    
    # 构建查询
    query = db.query(
        Submission.user_id,
        func.max(Submission.final_score).label('best_score'),
        func.count(Submission.id).label('submission_count'),
        func.max(Submission.submitted_at).label('last_submission')
    ).filter(
        Submission.status == 'success'
    )
    
    # 如果指定了竞赛ID，则筛选
    if competition_id:
        query = query.filter(Submission.competition_id == competition_id)
    
    subquery = query.group_by(Submission.user_id).subquery()
    
    # 获取完整信息
    results = db.query(
        User.id,
        User.username,
        subquery.c.best_score,
        subquery.c.submission_count,
        subquery.c.last_submission
    ).join(
        subquery, User.id == subquery.c.user_id
    ).order_by(
        desc(subquery.c.best_score)
    ).limit(limit).all()
    
    # 构建排行榜
    leaderboard = []
    for rank, (user_id, username, best_score, submission_count, last_submission) in enumerate(results, start=1):
        # 获取该用户最佳提交的详细信息
        best_submission_query = db.query(Submission).filter(
            Submission.user_id == user_id,
            Submission.final_score == best_score,
            Submission.status == 'success'
        )
        
        # 如果指定了竞赛ID，则筛选
        if competition_id:
            best_submission_query = best_submission_query.filter(Submission.competition_id == competition_id)
        
        best_submission = best_submission_query.first()
        
        leaderboard.append(LeaderboardEntry(
            rank=rank,
            user_id=user_id,
            username=username,
            best_score=best_score,
            best_accuracy=best_submission.accuracy if best_submission else 0,
            best_f1_score=best_submission.f1_score if best_submission else 0,
            submission_count=submission_count,
            last_submission=last_submission
        ))
    
    return leaderboard


# ==================== 统计信息 ====================
@app.get("/api/statistics", response_model=Statistics)
def get_statistics(db: Session = Depends(get_db)):
    """获取平台统计信息"""
    
    total_users = db.query(func.count(User.id)).scalar()
    total_submissions = db.query(func.count(Submission.id)).scalar()
    
    # 只统计成功的提交
    successful_submissions = db.query(Submission).filter(Submission.status == 'success').all()
    
    if successful_submissions:
        scores = [s.final_score for s in successful_submissions if s.final_score is not None]
        avg_score = sum(scores) / len(scores) if scores else 0
        best_score = max(scores) if scores else 0
    else:
        avg_score = 0
        best_score = 0
    
    return Statistics(
        total_users=total_users,
        total_submissions=total_submissions,
        avg_score=avg_score,
        best_score=best_score
    )


# ==================== 数据下载 ====================
@app.get("/api/download/dataset/{competition_id}")
def download_dataset(competition_id: int, db: Session = Depends(get_db)):
    """下载竞赛数据集"""
    # 获取竞赛信息
    competition = db.query(Competition).filter(Competition.id == competition_id).first()
    if not competition:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="竞赛不存在"
        )
    
    file_path = resolve_resource_path(competition.dataset_path)
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="数据集文件不存在"
        )
    
    return FileResponse(
        path=str(file_path),
        filename=os.path.basename(competition.dataset_path),
        media_type="application/gzip"
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
