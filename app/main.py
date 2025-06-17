from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .models.database import get_db, engine
from .models.models import Base
from .routers import auth, foods, tags, users

# 创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="今晚吃什么",
    description="一个帮助用户决定今晚吃什么的API",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该限制为特定域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 包含路由
app.include_router(auth.router)
app.include_router(foods.router)
app.include_router(tags.router)
app.include_router(users.router)

@app.get("/")
async def root():
    """API根路径，返回欢迎信息"""
    return {
        "message": "欢迎使用'今晚吃什么'API",
        "endpoints": {
            "文档": "/docs",
            "认证": "/auth/token",
            "注册": "/auth/register", 
            "食物": "/foods", 
            "随机推荐": "/foods/random"
        }
    }

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """健康检查端点"""
    try:
        # 尝试执行简单查询以验证数据库连接
        db.execute("SELECT 1")
        return {"status": "健康", "database": "连接正常"}
    except Exception as e:
        return {"status": "不健康", "database": str(e)}

# 如果作为主模块运行，启动Uvicorn服务器
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)