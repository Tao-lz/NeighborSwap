from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Item
from ..schemas import FaqIn, FaqOut, PolishIn, PolishOut, PriceSuggestIn, PriceSuggestOut
from ..services import llm_service

router = APIRouter(prefix="/api/llm", tags=["llm"])


def _item_dict(item: Item) -> dict:
    return {
        "名称": item.name,
        "描述": item.description,
        "交易方式": item.trade_type.value,
        "价格": item.price,
        "状态": "在售" if item.status.value == "available" else "已送出",
    }


def _local_faq(item: Item, question: str) -> str:
    """未配置 API Key 时的本地兜底，保证 FAQ 演示不中断。"""
    q = question.strip()
    if "还在" in q or "有没有" in q:
        if item.status.value == "available":
            return "还在哦，可以直接联系发布者。"
        return "已经送出啦，看看别的吧～"
    if "自提" in q or "取" in q or "哪里" in q or "地址" in q:
        return "一般是自提，具体地点和时间请和发布者商量。"
    if "刀" in q or "便宜" in q or "少" in q or "优惠" in q:
        return "价格可以商量，直接私聊发布者沟通。"
    return "这个问题建议直接联系发布者确认。"


@router.post("/price-suggest", response_model=PriceSuggestOut)
def price_suggest(payload: PriceSuggestIn):
    try:
        data = llm_service.suggest_price(payload.name, payload.description)
    except llm_service.LLMError as e:
        raise HTTPException(503, str(e))
    except Exception as e:
        raise HTTPException(502, f"定价建议生成失败：{e}")
    return PriceSuggestOut(**data)


@router.post("/polish", response_model=PolishOut)
def polish(payload: PolishIn):
    try:
        polished = llm_service.polish_description(payload.description)
    except llm_service.LLMError as e:
        raise HTTPException(503, str(e))
    except Exception as e:
        raise HTTPException(502, f"描述优化失败：{e}")
    return PolishOut(polished=polished)


@router.post("/faq", response_model=FaqOut)
def faq(payload: FaqIn, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == payload.item_id).first()
    if not item:
        raise HTTPException(404, "物品不存在")
    try:
        answer = llm_service.faq_answer(_item_dict(item), payload.question)
    except Exception:
        answer = _local_faq(item, payload.question)
    return FaqOut(answer=answer)
