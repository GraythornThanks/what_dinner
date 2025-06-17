from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..models.database import get_db
from ..models.schemas import User, Food, FoodHistory, FoodHistoryCreate
from ..models.models import User as UserModel, Food as FoodModel, FoodHistory as FoodHistoryModel
from ..security import get_current_active_user

router = APIRouter(
    prefix="/users",
    tags=["用户"],
    responses={404: {"description": "未找到"}},
)

@router.get("/me/favorites", response_model=List[Food])
def read_user_favorites(
    skip: int = 0, 
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """获取当前用户收藏的食物/餐厅"""
    return current_user.favorites[skip:skip+limit]

@router.post("/me/favorites/{food_id}", response_model=Food)
def add_favorite(
    food_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """将食物/餐厅添加到收藏"""
    food = db.query(FoodModel).filter(FoodModel.id == food_id).first()
    if food is None:
        raise HTTPException(status_code=404, detail="食物不存在")
        
    if food in current_user.favorites:
        raise HTTPException(status_code=400, detail="该食物已在收藏中")
        
    current_user.favorites.append(food)
    db.commit()
    return food

@router.delete("/me/favorites/{food_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_favorite(
    food_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """从收藏中移除食物/餐厅"""
    food = db.query(FoodModel).filter(FoodModel.id == food_id).first()
    if food is None:
        raise HTTPException(status_code=404, detail="食物不存在")
        
    if food not in current_user.favorites:
        raise HTTPException(status_code=400, detail="该食物不在收藏中")
        
    current_user.favorites.remove(food)
    db.commit()
    return {"status": "success"}

@router.get("/me/history", response_model=List[FoodHistory])
def read_user_history(
    skip: int = 0, 
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """获取用户的历史选择记录"""
    histories = db.query(FoodHistoryModel).filter(
        FoodHistoryModel.user_id == current_user.id
    ).order_by(
        FoodHistoryModel.selected_at.desc()
    ).offset(skip).limit(limit).all()
    
    return histories

@router.post("/me/history", response_model=FoodHistory)
def create_history(
    history: FoodHistoryCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """记录用户的食物选择"""
    food = db.query(FoodModel).filter(FoodModel.id == history.food_id).first()
    if food is None:
        raise HTTPException(status_code=404, detail="食物不存在")
        
    db_history = FoodHistoryModel(
        user_id=current_user.id,
        food_id=history.food_id,
        rating=history.rating,
        comment=history.comment
    )
    
    db.add(db_history)
    db.commit()
    db.refresh(db_history)
    return db_history
