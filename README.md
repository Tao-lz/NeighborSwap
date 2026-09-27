# NeighborSwap 邻里交换

社区闲置物品流转平台 —— 让闲置物品在沉没之前被看到。

针对微信群闲置流转的痛点：消息刷新快、不知道物品是否还在、不知道怎么定价、沟通成本高。

技术栈：**Vue 3 + Element Plus** / **FastAPI + SQLAlchemy + SQLite** / **DeepSeek API**

## 功能

- 物品发布：名称、描述、交易方式（免费送 / 随便给 / 标价）、状态图片
- 新鲜度：24h 内「刚上架」、72h 内「新上架」、之后「已上架 X 天」
- 浏览检索：卡片流、按新鲜度排序、免费/标价筛选、关键词搜索
- 意向沟通：点「想要」、发布者查看谁想要、确认成交后物品变「已送出」、留言板问答
- 数据看板：本月发布/成交、当前在售、最快领走、最抢手未成交
- LLM 能力：智能定价建议、描述优化、交易 FAQ 自动回复（含本地兜底）

## 快速启动

### 1. 后端

```bash
cd backend
python -m venv .venv
source .venv/Scripts/activate        # Windows (Git Bash)
pip install -r requirements.txt
uvicorn app.main:app --port 8000
```

后端地址：http://127.0.0.1:8000 ，健康检查 http://127.0.0.1:8000/api/health

### 2. 前端

```bash
cd frontend
npm install
npm run dev
```

前端地址：http://localhost:5173 （已配置 `/api`、`/uploads` 代理到 8000）

### 3. 生成演示数据（可选，但推荐）

```bash
cd backend
.venv/Scripts/python seed.py
```

生成 8 个用户、11 件物品（含已送出、多人想要、留言），让首页和看板看起来真实。

### 4. 配置 LLM（可选）

LLM 功能（智能定价 / 描述优化 / FAQ 自动回复）需要 DeepSeek API Key：

```bash
cd backend
cp .env.example .env
# 编辑 .env，填入 DEEPSEEK_API_KEY=sk-xxx
```

不配置也能正常使用其它功能；FAQ 会自动走本地兜底回答，定价/润色会提示未配置。

## 目录结构

```
backend/
  app/
    main.py            # 应用入口，挂载路由/CORS/静态文件
    config.py          # 读取 .env 配置
    database.py        # engine / session
    models.py          # User / Item / Want / Comment
    schemas.py         # Pydantic 请求/响应模型
    serializers.py     # ORM -> 响应 序列化
    deps.py            # 用户身份依赖（X-User-Id）
    routers/           # users / items / wants / comments / images / me / dashboard / llm
    services/llm_service.py   # DeepSeek 封装 + 降级兜底
  uploads/             # 图片静态目录
  seed.py              # 演示数据脚本
frontend/
  src/
    api/               # axios 封装（自动带 X-User-Id）
    stores/user.js     # 用户状态（Pinia）
    components/        # ItemCard / FreshnessTag / LoginDialog
    views/             # Home / Publish / ItemDetail / Mine / Dashboard
```

## 设计要点

- **身份**：昵称即身份，无密码（熟人社区，不过度设计）
- **状态机**：物品只有 `available`（在售）/ `given`（已送出）两态，已送出保留记录但不可操作
- **新鲜度**：由 `created_at` 实时计算，不落库
- **时间**：统一本地时间（单时区应用），避免 UTC 偏移导致新鲜度错误
- **LLM 降级**：DeepSeek 不可用时 FAQ 本地兜底、定价/润色优雅报错，主流程不受影响

## 主要 API

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | `/api/users/login` | 昵称登录 |
| GET/POST | `/api/items` | 列表（q/trade_type/status 筛选）/ 发布 |
| GET/PATCH | `/api/items/{id}` | 详情 / 标记已送出 |
| POST | `/api/items/{id}/wants` | 表达想要 |
| POST | `/api/wants/{id}/confirm` | 确认成交 |
| GET/POST | `/api/items/{id}/comments` | 留言板 |
| GET | `/api/me/items` `/api/me/wants` | 我的发布 / 我想要的 |
| GET | `/api/dashboard` | 数据看板 |
| POST | `/api/llm/price-suggest` `/polish` `/faq` | LLM 三件套 |
| POST | `/api/images` | 图片上传 |
