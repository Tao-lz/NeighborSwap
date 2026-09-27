"""生成演示数据。用法（在 backend 目录下）：.venv/Scripts/python seed.py"""
from datetime import datetime, timedelta

from app.database import SessionLocal
from app.models import (
    Comment,
    Item,
    ItemStatus,
    TradeType,
    User,
    Want,
    WantStatus,
)

db = SessionLocal()

# 按依赖顺序清空旧数据
db.query(Comment).delete()
db.query(Want).delete()
db.query(Item).delete()
db.query(User).delete()
db.commit()

now = datetime.now()

# 用户
users = {}
nicknames = [
    "3号楼小王", "2单元老李", "5号楼阿珍", "物业小陈",
    "6号楼KK", "1号楼大刘", "4号楼娜娜", "办公室李姐",
]
for nickname in nicknames:
    u = User(nickname=nickname)
    db.add(u)
    users[nickname] = u
db.commit()
for u in users.values():
    db.refresh(u)


def make_item(name, desc, trade_type, price, owner, hours_ago, given_after_hours=None):
    created = now - timedelta(hours=hours_ago)
    it = Item(
        name=name,
        description=desc,
        trade_type=TradeType(trade_type),
        price=price,
        status=ItemStatus.available,
        owner_id=owner.id,
        created_at=created,
    )
    if given_after_hours is not None:
        it.status = ItemStatus.given
        it.given_at = created + timedelta(hours=given_after_hours)
    db.add(it)
    db.flush()
    return it


items = [
    make_item("九成新电风扇", "搬家出，用了不到一年，风力大，3 号楼自提。", "priced", 30, users["3号楼小王"], 5),
    make_item("宜家白色台灯", "宜家购入，灯泡刚换新，免费送，自提。", "free", None, users["2单元老李"], 20),
    make_item("儿童自行车", "孩子长大了骑不了，八成新，随便给。", "offer", None, users["5号楼阿珍"], 30),
    make_item("小米空气净化器", "滤芯刚换，家里两台出一台，可刀。", "priced", 199, users["6号楼KK"], 50),
    make_item("一箱矿泉水", "公司发的喝不完，免费送，先到先得。", "free", None, users["物业小陈"], 2),
    make_item("折叠餐桌", "租房买的，搬走带不走，随便给。", "offer", None, users["1号楼大刘"], 80),
    make_item("戴森吸尘器 V8", "配件齐全，电池耐用，自提。", "priced", 450, users["4号楼娜娜"], 6),
    make_item("多肉植物一盆", "阳台放不下，免费送，带盆。", "free", None, users["办公室李姐"], 100),
    make_item("机械键盘", "青轴，用了一个月不习惯，出掉。", "priced", 120, users["6号楼KK"], 4, given_after_hours=1),
    make_item("瑜伽垫", "全新未拆封，搬家清。", "priced", 40, users["5号楼阿珍"], 60, given_after_hours=48),
    make_item("落地风扇", "夏末清仓，功能正常。", "priced", 55, users["1号楼大刘"], 150, given_after_hours=20),
]
db.commit()
for it in items:
    db.refresh(it)

# 最多人想要但未成交：电风扇 4 人想要
hot_item = items[0]
for nickname in ["2单元老李", "5号楼阿珍", "6号楼KK", "办公室李姐"]:
    db.add(Want(item_id=hot_item.id, user_id=users[nickname].id, status=WantStatus.wanted))

# 其它在售物品的想要
db.add(Want(item_id=items[3].id, user_id=users["3号楼小王"].id, status=WantStatus.wanted))
db.add(Want(item_id=items[6].id, user_id=users["1号楼大刘"].id, status=WantStatus.wanted))

# 已成交的意向（对应已送出物品）
db.add(Want(item_id=items[8].id, user_id=users["3号楼小王"].id, status=WantStatus.confirmed))

# 留言问答
comments = [
    (items[0].id, users["2单元老李"].id, "风扇还在吗？几成新？"),
    (items[0].id, users["3号楼小王"].id, "还在的，九成新，用了不到一年。"),
    (items[3].id, users["5号楼阿珍"].id, "滤芯是原装的吗？"),
    (items[6].id, users["1号楼大刘"].id, "能刀吗？最低多少？"),
]
for item_id, user_id, content in comments:
    db.add(Comment(item_id=item_id, user_id=user_id, content=content))

db.commit()
db.close()
print(f"种子数据完成：{len(nicknames)} 用户，{len(items)} 物品")
