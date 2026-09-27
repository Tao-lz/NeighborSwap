from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import current_user_id
from ..models import Item, ItemStatus, Want
from ..schemas import ItemOut, MyWantOut
from ..serializers import serialize_item

router = APIRouter(prefix="/api/me", tags=["me"])


@router.get("/items", response_model=list[ItemOut])
def my_items(
    status: ItemStatus | None = None,
    db: Session = Depends(get_db),
    user_id: int = Depends(current_user_id),
):
    query = db.query(Item).filter(Item.owner_id == user_id)
    if status:
        query = query.filter(Item.status == status)
    items = query.order_by(Item.created_at.desc()).all()
    return [serialize_item(item, db, user_id) for item in items]


@router.get("/wants", response_model=list[MyWantOut])
def my_wants(
    db: Session = Depends(get_db),
    user_id: int = Depends(current_user_id),
):
    wants = (
        db.query(Want)
        .filter(Want.user_id == user_id)
        .order_by(Want.created_at.desc())
        .all()
    )
    result = []
    for w in wants:
        item = db.query(Item).filter(Item.id == w.item_id).first()
        if not item:
            continue
        result.append(
            MyWantOut(
                id=w.id,
                item_id=item.id,
                item_name=item.name,
                item_image=item.image_url,
                item_status=item.status,
                item_price=item.price,
                item_trade_type=item.trade_type,
                status=w.status,
                created_at=w.created_at,
            )
        )
    return result
