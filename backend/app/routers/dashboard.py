from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Item, ItemStatus
from ..schemas import DashboardOut
from ..serializers import serialize_item

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("", response_model=DashboardOut)
def dashboard(db: Session = Depends(get_db)):
    now = datetime.now()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    month_published = (
        db.query(Item).filter(Item.created_at >= month_start).count()
    )
    month_given = (
        db.query(Item)
        .filter(Item.status == ItemStatus.given, Item.given_at >= month_start)
        .count()
    )
    current_available = (
        db.query(Item).filter(Item.status == ItemStatus.available).count()
    )

    # 最快被领走的物品：成交耗时最短
    given = (
        db.query(Item)
        .filter(Item.status == ItemStatus.given, Item.given_at.isnot(None))
        .all()
    )
    fastest_given = None
    if given:
        fastest_item = min(
            given, key=lambda i: (i.given_at - i.created_at).total_seconds()
        )
        fastest_given = serialize_item(fastest_item, db, None)

    # 最多人想要但尚未成交
    available = (
        db.query(Item).filter(Item.status == ItemStatus.available).all()
    )
    hottest_wanted = None
    if available:
        hottest_wanted = max(
            (serialize_item(i, db, None) for i in available),
            key=lambda i: i.want_count,
        )

    return DashboardOut(
        month_published=month_published,
        month_given=month_given,
        current_available=current_available,
        fastest_given=fastest_given,
        hottest_wanted=hottest_wanted,
    )
