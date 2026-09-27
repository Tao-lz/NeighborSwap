import json

from ..config import settings


class LLMError(Exception):
    """LLM 不可用时的统一异常。"""


_client = None


def is_available() -> bool:
    return bool(settings.deepseek_api_key)


def _get_client():
    global _client
    if _client is None:
        from openai import OpenAI

        _client = OpenAI(
            api_key=settings.deepseek_api_key,
            base_url=settings.deepseek_base_url,
        )
    return _client


def _chat(messages, json_mode=False, temperature=0.3):
    client = _get_client()
    kwargs = dict(
        model=settings.deepseek_model,
        messages=messages,
        temperature=temperature,
        max_tokens=800,
    )
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}
    resp = client.chat.completions.create(**kwargs)
    return resp.choices[0].message.content


def suggest_price(name: str, description: str) -> dict:
    if not is_available():
        raise LLMError("未配置 DeepSeek API Key，无法使用智能定价")
    system = (
        "你是小区闲置物品估价助手。根据物品名称和描述，判断最合适的交易方式并给出建议。"
        '必须只输出 JSON，不要输出其它内容，格式：'
        '{"trade_type": "free|offer|priced", "price_min": 数字或null, "price_max": 数字或null, "reason": "简短理由"}'
        "trade_type 取值：free=建议免费送，offer=随便给（买家随意出价），priced=标价。"
        "若建议标价，price_min/price_max 给出价格区间（元，数字）；否则为 null。"
    )
    user = f"物品名称：{name}\n物品描述：{description}"
    content = _chat(
        [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        json_mode=True,
        temperature=0.2,
    )
    data = json.loads(content)
    data.setdefault("trade_type", "offer")
    data.setdefault("price_min", None)
    data.setdefault("price_max", None)
    data.setdefault("reason", "")
    if data["trade_type"] not in ("free", "offer", "priced"):
        data["trade_type"] = "offer"
    return data


def polish_description(description: str) -> str:
    if not is_available():
        raise LLMError("未配置 DeepSeek API Key，无法使用描述优化")
    system = (
        "你是小区闲置群文案润色师。把用户粗糙的描述改写成更适合发布的文案："
        "更清晰、友好、口语化；突出新旧程度和使用情况；提示自提地点；保持简洁（80 字以内）。"
        "直接输出润色后的文案，不要任何解释或引号。"
    )
    content = _chat(
        [
            {"role": "system", "content": system},
            {"role": "user", "content": description},
        ],
        temperature=0.6,
    )
    return content.strip()


def faq_answer(item: dict, question: str) -> str:
    if not is_available():
        raise LLMError("LLM 不可用")
    system = (
        "你是小区闲置物品的智能客服，根据提供的物品信息回答买家的问题。"
        "规则：优先结合物品信息回答。'还在吗/有没有'按状态回答（在售=还在，已送出=已送出）；"
        "'能刀吗/便宜点/优惠'结合交易方式和价格回答：标价=可以小刀商量，免费送=免费先到先得，随便给=买家随意出价；"
        "自提地点优先用描述里的信息，描述里没有（如具体时间、地址）就礼貌地请买家联系发布者确认；"
        "回答简洁、口语化、友好，直接回答，不要解释。"
    )
    item_text = json.dumps(item, ensure_ascii=False, default=str)
    user = f"物品信息：{item_text}\n问题：{question}"
    content = _chat(
        [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=0.4,
    )
    return content.strip()
