from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from .models import ItemStatus, TradeType


# ---- User ----
class UserLogin(BaseModel):
    nickname: str = Field(min_length=1, max_length=50)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nickname: str
    created_at: datetime


# ---- Item ----
class ItemCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str = ""
    trade_type: TradeType = TradeType.free
    price: float | None = None
    image_url: str | None = None


class ItemUpdate(BaseModel):
    status: ItemStatus


class ItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    description: str
    trade_type: TradeType
    price: float | None
    image_url: str | None
    status: ItemStatus
    owner_id: int
    created_at: datetime
    given_at: datetime | None
    owner_nickname: str | None = None
    want_count: int = 0
    wanted_by_me: bool = False


# ---- Want ----
class WantOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    item_id: int
    user_id: int
    status: str
    created_at: datetime
    user_nickname: str | None = None


# ---- Comment ----
class CommentCreate(BaseModel):
    content: str = Field(min_length=1, max_length=1000)


class CommentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    item_id: int
    user_id: int
    content: str
    created_at: datetime
    user_nickname: str | None = None


# ---- 我想要的（关联物品信息） ----
class MyWantOut(BaseModel):
    id: int
    item_id: int
    item_name: str
    item_image: str | None
    item_status: str
    item_price: float | None
    item_trade_type: str
    status: str
    created_at: datetime


# ---- 数据看板 ----
class DashboardOut(BaseModel):
    month_published: int
    month_given: int
    current_available: int
    fastest_given: ItemOut | None
    hottest_wanted: ItemOut | None


# ---- LLM ----
class PriceSuggestIn(BaseModel):
    name: str
    description: str = ""


class PriceSuggestOut(BaseModel):
    trade_type: str
    price_min: float | None = None
    price_max: float | None = None
    reason: str = ""


class PolishIn(BaseModel):
    description: str


class PolishOut(BaseModel):
    polished: str


class FaqIn(BaseModel):
    item_id: int
    question: str


class FaqOut(BaseModel):
    answer: str
