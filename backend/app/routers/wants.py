from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import current_user_id
from ..models import Item, ItemStatus, Want, WantStatus, now
from ..schemas import ItemOut, WantOut
from ..serializers import serialize_item, serialize_want

router = APIRouter(prefix="/api", tags=["wants"])


@router.get("/items/{item_id}/wants", response_model=list[WantOut])
def list_wants(
    item_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(current_user_id),
):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(404, "物品不存在")
    if item.owner_id != user_id:
        raise HTTPException(403, "只有发布者可以查看谁想要")
    wants = (
        db.query(Want)
        .filter(Want.item_id == item_id)
        .order_by(Want.created_at.desc())
        .all()
    )
    return [serialize_want(w, db) for w in wants]


@router.post("/items/{item_id}/wants", response_model=WantOut, status_code=201)
def create_want(
    item_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(current_user_id),
):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(404, "物品不存在")
    if item.status != ItemStatus.available:
        raise HTTPException(400, "该物品已送出")
    if item.owner_id == user_id:
        raise HTTPException(400, "不能想要自己发布的物品")
    existing = (
        db.query(Want).filter(Want.item_id == item_id, Want.user_id == user_id).first()
    )
    if existing:
        raise HTTPException(400, "你已经表达过想要")
    want = Want(item_id=item_id, user_id=user_id, status=WantStatus.wanted)
    db.add(want)
    db.commit()
    db.refresh(want)
    return serialize_want(want, db)


@router.post("/wants/{want_id}/confirm", response_model=ItemOut)
def confirm_want(
    want_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(current_user_id),
):
    want = db.query(Want).filter(Want.id == want_id).first()
    if not want:
        raise HTTPException(404, "意向不存在")
    item = db.query(Item).filter(Item.id == want.item_id).first()
    if not item:
        raise HTTPException(404, "物品不存在")
    if item.owner_id != user_id:
        raise HTTPException(403, "只有发布者可以确认成交")
    if item.status == ItemStatus.given:
        raise HTTPException(400, "该物品已送出")
    want.status = WantStatus.confirmed
    item.status = ItemStatus.given
    item.given_at = now()
    db.commit()
    db.refresh(item)
    return serialize_item(item, db, user_id)
