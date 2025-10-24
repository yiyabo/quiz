"""
数据库配置和模型定义
"""
from datetime import datetime
from pathlib import Path

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

# 统一的路径设置
BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "quiz_platform.db"

# 数据库URL - 使用SQLite（路径固定在backend目录下）
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# 创建数据库引擎
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}  # SQLite特有配置
)

# 创建Session工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类
Base = declarative_base()


# 竞赛模型
class Competition(Base):
    __tablename__ = "competitions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    dataset_path = Column(String(255), nullable=False)
    answer_path = Column(String(255), nullable=False)
    is_active = Column(Integer, default=1)  # 1=活跃, 0=已结束
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关联关系
    submissions = relationship("Submission", back_populates="competition", cascade="all, delete-orphan")


# 用户模型
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关联关系
    submissions = relationship("Submission", back_populates="user", cascade="all, delete-orphan")


# 提交记录模型
class Submission(Base):
    __tablename__ = "submissions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    competition_id = Column(Integer, ForeignKey("competitions.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    submitted_at = Column(DateTime, default=datetime.utcnow)
    
    # 评分指标
    accuracy = Column(Float, nullable=True)
    precision = Column(Float, nullable=True)
    recall = Column(Float, nullable=True)
    f1_score = Column(Float, nullable=True)
    final_score = Column(Float, nullable=True)
    
    # 混淆矩阵
    tp = Column(Integer, nullable=True)
    tn = Column(Integer, nullable=True)
    fp = Column(Integer, nullable=True)
    fn = Column(Integer, nullable=True)
    
    # 评分状态
    status = Column(String(20), default="pending")  # pending, success, error
    error_message = Column(Text, nullable=True)
    
    # 关联关系
    user = relationship("User", back_populates="submissions")
    competition = relationship("Competition", back_populates="submissions")


# 创建所有表
def init_db():
    Base.metadata.create_all(bind=engine)
    
    # 初始化竞赛数据
    db = SessionLocal()
    try:
        # 标准的竞赛资源路径（相对于项目根目录）
        default_paths = {
            "ppi": {
                "dataset_path": "kaggle_dataset.tar.gz",
                "answer_path": "teacher_only/test_labels.csv"
            },
            "cci": {
                "dataset_path": "cci test/dataset.tar.gz",
                "answer_path": "cci test/answer/test_edges.csv"
            }
        }

        # 检查并初始化/修正竞赛数据
        for name, paths in default_paths.items():
            competition = db.query(Competition).filter(Competition.name == name).first()

            if competition is None:
                # 新建竞赛
                if name == "ppi":
                    competition = Competition(
                        name="ppi",
                        title="Protein-Protein Interaction Prediction",
                        description="Predict whether two proteins will interact (Protein-Protein Interaction, PPI)",
                        dataset_path=paths["dataset_path"],
                        answer_path=paths["answer_path"],
                        is_active=1
                    )
                elif name == "cci":
                    competition = Competition(
                        name="cci",
                        title="Cell-Cell Interaction Prediction",
                        description="Predict cell-cell interactions based on spatial transcriptomics data (Cell-Cell Interaction, CCI)",
                        dataset_path=paths["dataset_path"],
                        answer_path=paths["answer_path"],
                        is_active=1
                    )
                db.add(competition)
            else:
                # 已存在的竞赛，修正资源路径
                updated = False
                if competition.dataset_path != paths["dataset_path"]:
                    competition.dataset_path = paths["dataset_path"]
                    updated = True
                if competition.answer_path != paths["answer_path"]:
                    competition.answer_path = paths["answer_path"]
                    updated = True
                if updated:
                    db.add(competition)

        db.commit()
        print("✅ 竞赛数据初始化完成")
    except Exception as e:
        print(f"⚠️  竞赛数据初始化失败: {e}")
        db.rollback()
    finally:
        db.close()


# 数据库依赖
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
