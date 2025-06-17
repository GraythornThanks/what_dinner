from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from typing import List, Optional
import random
from sqlalchemy import and_, or_

from ..models.database import get_db
from ..models.schemas import Food, FoodCreate, FoodUpdate, RandomFoodRequest
from ..models.models import Food as FoodModel, Tag as TagModel, food_tag
from ..security import get_current_active_user
from ..models.models import User as UserModel

router = APIRouter(
    prefix="/foods",
    tags=["食物"],
    responses={404: {"description": "未找到"}},
)

@router.post("/", response_model=Food)
def create_food(
    food: FoodCreate, 
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """创建新食物/餐厅"""
    db_food = FoodModel(
        name=food.name,
        description=food.description,
        cuisine_type=food.cuisine_type,
        price_level=food.price_level,
        location=food.location,
        is_restaurant=food.is_restaurant,
        image_url=food.image_url
    )
    
    # 处理标签
    if food.tags:
        for tag_name in food.tags:
            tag = db.query(TagModel).filter(TagModel.name == tag_name).first()
            if not tag:
                tag = TagModel(name=tag_name)
                db.add(tag)
                db.flush()
            db_food.tags.append(tag)
    
    db.add(db_food)
    db.commit()
    db.refresh(db_food)
    return db_food

@router.get("/", response_model=List[Food])
def read_foods(
    skip: int = 0, 
    limit: int = 100, 
    cuisine: Optional[str] = None,
    is_restaurant: Optional[bool] = None,
    tag: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取食物/餐厅列表，支持筛选"""
    query = db.query(FoodModel)
    
    # 应用筛选条件
    if cuisine:
        query = query.filter(FoodModel.cuisine_type == cuisine)
    if is_restaurant is not None:
        query = query.filter(FoodModel.is_restaurant == is_restaurant)
    if tag:
        query = query.join(FoodModel.tags).filter(TagModel.name == tag)
        
    return query.offset(skip).limit(limit).all()

@router.get("/random", response_model=Food)
def get_random_food(
    request: RandomFoodRequest,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """随机推荐食物/餐厅"""
    query = db.query(FoodModel)
    
    # 应用筛选条件
    filters = []
    
    if request.cuisine_type:
        filters.append(FoodModel.cuisine_type == request.cuisine_type)
        
    if request.is_restaurant is not None:
        filters.append(FoodModel.is_restaurant == request.is_restaurant)
        
    if request.price_min is not None and request.price_max is not None:
        filters.append(FoodModel.price_level.between(request.price_min, request.price_max))
    elif request.price_min is not None:
        filters.append(FoodModel.price_level >= request.price_min)
    elif request.price_max is not None:
        filters.append(FoodModel.price_level <= request.price_max)
    
    if request.tags:
        for tag in request.tags:
            query = query.join(FoodModel.tags).filter(TagModel.name == tag)
    
    if filters:
        query = query.filter(and_(*filters))
    
    # 获取符合条件的所有食物
    food_list = query.all()
    
    if not food_list:
        raise HTTPException(status_code=404, detail="没有找到符合条件的食物/餐厅")
    
    # 随机选择一个
    random_food = random.choice(food_list)
    
    # TODO: 可以在这里添加记录历史的逻辑
    
    return random_food

@router.get("/{food_id}", response_model=Food)
def read_food(food_id: int, db: Session = Depends(get_db)):
    """获取特定食物/餐厅的详细信息"""
    db_food = db.query(FoodModel).filter(FoodModel.id == food_id).first()
    if db_food is None:
        raise HTTPException(status_code=404, detail="食物不存在")
    return db_food

@router.put("/{food_id}", response_model=Food)
def update_food(
    food_id: int, 
    food: FoodUpdate, 
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """更新食物/餐厅信息"""
    db_food = db.query(FoodModel).filter(FoodModel.id == food_id).first()
    if db_food is None:
        raise HTTPException(status_code=404, detail="食物不存在")
        
    # 更新基本信息
    update_data = food.dict(exclude_unset=True)
    
    # 单独处理标签更新
    if "tags" in update_data:
        tags = update_data.pop("tags")
        
        # 清除现有标签
        db_food.tags = []
        
        # 添加新标签
        if tags:
            for tag_name in tags:
                tag = db.query(TagModel).filter(TagModel.name == tag_name).first()
                if not tag:
                    tag = TagModel(name=tag_name)
                    db.add(tag)
                    db.flush()
                db_food.tags.append(tag)
    
    # 更新其余属性
    for key, value in update_data.items():
        setattr(db_food, key, value)
    
    db.commit()
    db.refresh(db_food)
    return db_food

@router.delete("/{food_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_food(
    food_id: int, 
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """删除食物/餐厅"""
    db_food = db.query(FoodModel).filter(FoodModel.id == food_id).first()
    if db_food is None:
        raise HTTPException(status_code=404, detail="食物不存在")
    
    db.delete(db_food)
    db.commit()
    return {"status": "success"}
