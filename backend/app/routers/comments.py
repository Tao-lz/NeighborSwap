from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import current_user_id
from ..models import Comment, Item, User
from ..schemas import CommentCreate, CommentOut

router = APIRouter(prefix="/api/items", tags=["comments"])


def _serialize_comment(c: Comment) -> CommentOut:
    return CommentOut(
        id=c.id,
        item_id=c.item_id,
        user_id=c.user_id,
        content=c.content,
        created_at=c.created_at,
        user_nickname=c.user.nickname if c.user else None,
    )


@router.get("/{item_id}/comments", response_model=list[CommentOut])
def list_comments(item_id: int, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(404, "物品不存在")
    comments = (
        db.query(Comment)
        .filter(Comment.item_id == item_id)
        .order_by(Comment.created_at.asc())
        .all()
    )
    return [_serialize_comment(c) for c in comments]


@router.post("/{item_id}/comments", response_model=CommentOut, status_code=201)
def create_comment(
    item_id: int,
    payload: CommentCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(current_user_id),
):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(404, "物品不存在")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "用户不存在")
    comment = Comment(item_id=item_id, user_id=user_id, content=payload.content)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return _serialize_comment(comment)
