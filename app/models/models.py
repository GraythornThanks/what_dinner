from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Table, Float, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

# 食物-标签关联表（多对多关系）
food_tag = Table(
    "food_tag",
    Base.metadata,
    Column("food_id", Integer, ForeignKey("foods.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True)
)

# 用户-食物收藏关联表（多对多关系）
user_favorite = Table(
    "user_favorite",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("food_id", Integer, ForeignKey("foods.id"), primary_key=True)
)

class User(Base):
    """用户模型"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    
    # 关系
    favorites = relationship("Food", secondary=user_favorite, back_populates="favorited_by")
    history = relationship("FoodHistory", back_populates="user")
    
class Food(Base):
    """食物/餐厅模型"""
    __tablename__ = "foods"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text, nullable=True)
    cuisine_type = Column(String, nullable=True)  # 中餐、西餐、日料等
    price_level = Column(Integer, default=2)  # 1-5 价格等级
    location = Column(String, nullable=True)  # 如果是餐厅的话
    is_restaurant = Column(Boolean, default=False)  # 是否是餐厅，否则为食物/菜品
    rating = Column(Float, default=0)  # 用户评分
    image_url = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    
    # 关系
    tags = relationship("Tag", secondary=food_tag, back_populates="foods")
    favorited_by = relationship("User", secondary=user_favorite, back_populates="favorites")
    history = relationship("FoodHistory", back_populates="food")

class Tag(Base):
    """标签模型 - 用于分类食物"""
    __tablename__ = "tags"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    
    # 关系
    foods = relationship("Food", secondary=food_tag, back_populates="tags")

class FoodHistory(Base):
    """食物选择历史记录"""
    __tablename__ = "food_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    food_id = Column(Integer, ForeignKey("foods.id"))
    selected_at = Column(DateTime, server_default=func.now())
    rating = Column(Integer, nullable=True)  # 用户对这次选择的评分
    comment = Column(Text, nullable=True)
    
    # 关系
    user = relationship("User", back_populates="history")
    food = relationship("Food", back_populates="history")
