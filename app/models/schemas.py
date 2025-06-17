from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime

# 标签架构
class TagBase(BaseModel):
    name: str

class TagCreate(TagBase):
    pass

class Tag(TagBase):
    id: int
    
    class Config:
        orm_mode = True

# 食物架构
class FoodBase(BaseModel):
    name: str
    description: Optional[str] = None
    cuisine_type: Optional[str] = None
    price_level: int = 2
    location: Optional[str] = None
    is_restaurant: bool = False
    image_url: Optional[str] = None

class FoodCreate(FoodBase):
    tags: List[str] = []

class FoodUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    cuisine_type: Optional[str] = None
    price_level: Optional[int] = None
    location: Optional[str] = None
    is_restaurant: Optional[bool] = None
    image_url: Optional[str] = None
    tags: Optional[List[str]] = None

class Food(FoodBase):
    id: int
    rating: float = 0
    created_at: datetime
    tags: List[Tag] = []
    
    class Config:
        orm_mode = True

# 用户架构
class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    favorites: List[Food] = []
    
    class Config:
        orm_mode = True

# 食物历史记录架构
class FoodHistoryBase(BaseModel):
    food_id: int
    rating: Optional[int] = None
    comment: Optional[str] = None

class FoodHistoryCreate(FoodHistoryBase):
    pass

class FoodHistory(FoodHistoryBase):
    id: int
    user_id: int
    selected_at: datetime
    food: Food
    
    class Config:
        orm_mode = True

# 随机食物推荐请求架构
class RandomFoodRequest(BaseModel):
    cuisine_type: Optional[str] = None
    price_min: Optional[int] = None
    price_max: Optional[int] = None
    tags: Optional[List[str]] = None
    is_restaurant: Optional[bool] = None

# 令牌架构
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
