"""
Pydantic模型 - 用于API请求和响应的数据验证
"""
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List


# 用户相关模型
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# 提交相关模型
class SubmissionResponse(BaseModel):
    id: int
    user_id: int
    username: str
    filename: str
    submitted_at: datetime
    status: str
    accuracy: Optional[float] = None
    precision: Optional[float] = None
    recall: Optional[float] = None
    f1_score: Optional[float] = None
    final_score: Optional[float] = None
    error_message: Optional[str] = None
    
    class Config:
        from_attributes = True


class SubmissionDetail(BaseModel):
    id: int
    filename: str
    submitted_at: datetime
    status: str
    accuracy: Optional[float] = None
    precision: Optional[float] = None
    recall: Optional[float] = None
    f1_score: Optional[float] = None
    final_score: Optional[float] = None
    tp: Optional[int] = None
    tn: Optional[int] = None
    fp: Optional[int] = None
    fn: Optional[int] = None
    error_message: Optional[str] = None
    
    class Config:
        from_attributes = True


# 排行榜模型
class LeaderboardEntry(BaseModel):
    rank: int
    user_id: int
    username: str
    best_score: float
    best_accuracy: float
    best_precision: float
    best_recall: float
    best_f1_score: float
    submission_count: int
    last_submission: datetime
    
    class Config:
        from_attributes = True


# 竞赛相关模型
class CompetitionResponse(BaseModel):
    id: int
    name: str
    title: str
    description: Optional[str] = None
    is_active: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# 统计信息模型
class Statistics(BaseModel):
    total_users: int
    total_submissions: int
    avg_score: float
    best_score: float

