import enum
from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from .database import Base


def now():
    return datetime.now()


class TradeType(str, enum.Enum):
    free = "free"      # 免费送
    offer = "offer"    # 随便给
    priced = "priced"  # 标价


class ItemStatus(str, enum.Enum):
    available = "available"
    given = "given"


class WantStatus(str, enum.Enum):
    wanted = "wanted"
    confirmed = "confirmed"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    nickname = Column(String(50), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=now)

    items = relationship("Item", back_populates="owner")
    wants = relationship("Want", back_populates="user")
    comments = relationship("Comment", back_populates="user")


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, default="")
    trade_type = Column(Enum(TradeType), nullable=False, default=TradeType.free)
    price = Column(Float, nullable=True)
    image_url = Column(String(500), nullable=True)
    status = Column(Enum(ItemStatus), nullable=False, default=ItemStatus.available, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=now, index=True)
    given_at = Column(DateTime, nullable=True)

    owner = relationship("User", back_populates="items")
    wants = relationship("Want", back_populates="item")
    comments = relationship("Comment", back_populates="item")


class Want(Base):
    __tablename__ = "wants"
    __table_args__ = (UniqueConstraint("item_id", "user_id", name="uq_want_item_user"),)

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    status = Column(Enum(WantStatus), nullable=False, default=WantStatus.wanted)
    created_at = Column(DateTime, default=now)

    item = relationship("Item", back_populates="wants")
    user = relationship("User", back_populates="wants")


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=now)

    item = relationship("Item", back_populates="comments")
    user = relationship("User", back_populates="comments")
