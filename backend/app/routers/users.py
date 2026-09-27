from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User
from ..schemas import UserLogin, UserOut

router = APIRouter(prefix="/api/users", tags=["users"])


@router.post("/login", response_model=UserOut)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.nickname == payload.nickname).first()
    if not user:
        user = User(nickname=payload.nickname)
        db.add(user)
        db.commit()
        db.refresh(user)
    return user
