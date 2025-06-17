from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()

# 数据库连接URL
SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost/dinner_chooser"
)

# 创建SQLAlchemy引擎
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# 创建SessionLocal类，每个实例都是一个数据库会话
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建Base类，用于创建数据库模型/类（ORM模型）
Base = declarative_base()

# 依赖项函数
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
