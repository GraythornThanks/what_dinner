from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..models.database import get_db
from ..models.schemas import Tag, TagCreate
from ..models.models import Tag as TagModel
from ..security import get_current_active_user
from ..models.models import User as UserModel

router = APIRouter(
    prefix="/tags",
    tags=["标签"],
    responses={404: {"description": "未找到"}},
)

@router.post("/", response_model=Tag)
def create_tag(
    tag: TagCreate, 
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """创建新标签"""
    db_tag = db.query(TagModel).filter(TagModel.name == tag.name).first()
    if db_tag:
        raise HTTPException(status_code=400, detail="标签已存在")
        
    db_tag = TagModel(name=tag.name)
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag

@router.get("/", response_model=List[Tag])
def read_tags(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """获取所有标签列表"""
    tags = db.query(TagModel).offset(skip).limit(limit).all()
    return tags

@router.get("/{tag_id}", response_model=Tag)
def read_tag(tag_id: int, db: Session = Depends(get_db)):
    """获取特定标签的详细信息"""
    db_tag = db.query(TagModel).filter(TagModel.id == tag_id).first()
    if db_tag is None:
        raise HTTPException(status_code=404, detail="标签不存在")
    return db_tag

@router.delete("/{tag_id}")
def delete_tag(
    tag_id: int, 
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """删除标签"""
    db_tag = db.query(TagModel).filter(TagModel.id == tag_id).first()
    if db_tag is None:
        raise HTTPException(status_code=404, detail="标签不存在")
        
    db.delete(db_tag)
    db.commit()
    return {"status": "success"}
