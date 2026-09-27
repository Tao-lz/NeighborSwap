from sqlalchemy.orm import Session

from .models import Item, Want
from .schemas import ItemOut, WantOut


def serialize_item(item: Item, db: Session, user_id: int | None) -> ItemOut:
    want_count = db.query(Want).filter(Want.item_id == item.id).count()
    wanted_by_me = (
        user_id is not None
        and db.query(Want)
        .filter(Want.item_id == item.id, Want.user_id == user_id)
        .first()
        is not None
    )
    return ItemOut(
        id=item.id,
        name=item.name,
        description=item.description,
        trade_type=item.trade_type,
        price=item.price,
        image_url=item.image_url,
        status=item.status,
        owner_id=item.owner_id,
        created_at=item.created_at,
        given_at=item.given_at,
        owner_nickname=item.owner.nickname if item.owner else None,
        want_count=want_count,
        wanted_by_me=wanted_by_me,
    )


def serialize_want(want: Want, db: Session) -> WantOut:
    return WantOut(
        id=want.id,
        item_id=want.item_id,
        user_id=want.user_id,
        status=want.status,
        created_at=want.created_at,
        user_nickname=want.user.nickname if want.user else None,
    )
