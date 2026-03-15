import uuid
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Text, JSON, Boolean, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base

# 使用本地 SQLite 数据库
SQLALCHEMY_DATABASE_URL = "sqlite:///./skillcraft_library.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class SkillRecord(Base):
    """组件资产数据库模型"""
    __tablename__ = "skills"

    # 基础信息
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, index=True)          # 英文真名，用于 Godot (如 HealthComponent)
    alias_zh = Column(String, index=True)      # 中文具象别名 (如 生命值核心)
    category = Column(String, index=True)      # 目录分类 (如 Combat, Movement, System)
    description = Column(Text)                 # 详细描述
    
    # 核心数据
    code_content = Column(Text)                # GDScript 源码
    export_params = Column(JSON)               # 提取的 UI 参数字典
    
    # 👇 云端仓库扩展预留区 👇
    cloud_id = Column(String, nullable=True, index=True) # 未来对接云端时的唯一 ID
    is_synced = Column(Boolean, default=False)           # 是否已同步到云端
    version = Column(String, default="1.0.0")            # 组件版本号
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# 创建数据库表（如果不存在的话）
Base.metadata.create_all(bind=engine)