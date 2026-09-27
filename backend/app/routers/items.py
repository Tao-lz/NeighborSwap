from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import current_user_id, optional_user_id
from ..models import Item, ItemStatus, TradeType, User, now
from ..schemas import ItemCreate, ItemOut, ItemUpdate
from ..serializers import serialize_item

router = APIRouter(prefix="/api/items", tags=["items"])


def _parse_trade_types(raw: str | None):
    """支持 'free' 或 'free,offer' 逗号分隔，用于免费/标价筛选。"""
    if not raw:
        return None
    result = []
    for part in raw.split(","):
        part = part.strip()
        if not part:
            continue
        try:
            result.append(TradeType(part))
        except ValueError:
            raise HTTPException(400, f"无效的交易方式: {part}")
    return result


@router.get("", response_model=list[ItemOut])
def list_items(
    q: str | None = None,
    trade_type: str | None = None,
    status: ItemStatus = ItemStatus.available,
    page: int = 1,
    page_size: int = 50,
    user_id: int | None = Depends(optional_user_id),
    db: Session = Depends(get_db),
):
    query = db.query(Item).filter(Item.status == status)
    if q:
        like = f"%{q}%"
        query = query.filter(or_(Item.name.like(like), Item.description.like(like)))
    types = _parse_trade_types(trade_type)
    if types:
        query = query.filter(Item.trade_type.in_(types))
    items = (
        query.order_by(Item.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return [serialize_item(item, db, user_id) for item in items]


@router.post("", response_model=ItemOut, status_code=201)
def create_item(
    payload: ItemCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(current_user_id),
):
    owner = db.query(User).filter(User.id == user_id).first()
    if not owner:
        raise HTTPException(404, "用户不存在")
    price = payload.price if payload.trade_type == TradeType.priced else None
    item = Item(
        name=payload.name,
        description=payload.description or "",
        trade_type=payload.trade_type,
        price=price,
        image_url=payload.image_url,
        owner_id=user_id,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return serialize_item(item, db, user_id)


@router.get("/{item_id}", response_model=ItemOut)
def get_item(
    item_id: int,
    db: Session = Depends(get_db),
    user_id: int | None = Depends(optional_user_id),
):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(404, "物品不存在")
    return serialize_item(item, db, user_id)


@router.patch("/{item_id}", response_model=ItemOut)
def update_item(
    item_id: int,
    payload: ItemUpdate,
    db: Session = Depends(get_db),
    user_id: int = Depends(current_user_id),
):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(404, "物品不存在")
    if item.owner_id != user_id:
        raise HTTPException(403, "只有发布者可以操作")
    item.status = payload.status
    if payload.status == ItemStatus.given:
        item.given_at = now()
    db.commit()
    db.refresh(item)
    return serialize_item(item, db, user_id)
