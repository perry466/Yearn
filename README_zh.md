# Yearn · 岁岁念

> **Yearn** /jɜːn/ — v. to long for, to miss deeply  
> **岁岁念** — 年年岁岁，惦念不忘

一个带农历支持、温暖现代的生日提醒应用。

**[English README](./README.md)**

---

## ✨ 功能特性

- 增删改查生日（公历 + 农历）
- 农历选择器，支持闰月
- 公历 / 农历自动互转
- 列表视图 + 卡片视图
- 日历视图（按月）
- 「即将到来」30 天提醒
- 统计概览（含饼图）
- 批量选择删除
- 分页（每页条数持久化到 localStorage）
- 暗色模式
- 中英文运行时切换
- 邮件 + Server酱提醒（提前 30/15/7/1 天）
- 响应式布局

---

## 🧱 技术栈

| 层级 | 技术 |
| --- | --- |
| 后端 | Python · FastAPI · SQLAlchemy · SQLite |
| 前端 | Vue 3 · Vite · TailwindCSS · Axios |
| 农历 | `lunardate` Python 库 |
| 调度器 | APScheduler（每天 09:00 Asia/Shanghai） |
| 提醒 | SMTP 邮件 + Server酱 |

---

## 🚀 快速开始

### 环境要求

- Python 3.11+
- Node.js 18+
- npm 9+

### 后端

```powershell
cd D:\project\yearn\backend
$env:PYTHONPATH = "D:\project\yearn\backend"
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

- API：`http://localhost:8000`
- Swagger 文档：`http://localhost:8000/docs`

### 前端

```powershell
cd D:\project\yearn\frontend
npm install
npm run dev
```

- 应用：`http://localhost:5173`

### 测试数据

```powershell
cd D:\project\yearn\backend
$env:PYTHONPATH = "D:\project\yearn\backend"
python reset_100.py    # 生成 100 条随机记录
```

---

## 📁 项目结构

```
yearn/
├── backend/
│   ├── app/
│   │   ├── core/
│   │   │   ├── config.py          # 邮件、Server酱、提醒配置
│   │   │   └── database.py        # SQLite 引擎和会话
│   │   ├── models/
│   │   │   └── birthday.py        # 生日 ORM 模型
│   │   ├── schemas/
│   │   │   └── birthday.py        # Pydantic 数据模型
│   │   ├── services/
│   │   │   ├── lunar.py           # 公历/农历互转
│   │   │   ├── reminder.py        # 邮件 + Server酱发送
│   │   │   └── birthday.py        # CRUD + 统计
│   │   ├── routers/
│   │   │   └── birthday.py        # REST API 路由
│   │   ├── scheduler.py           # APScheduler 每日检查
│   │   └── main.py                # FastAPI 入口
│   ├── requirements.txt
│   └── reset_100.py               # 生成 100 条测试记录
├── frontend/
│   ├── src/
│   │   ├── components/            # BirthdayCard, BirthdayTable 等
│   │   ├── views/                # HomeView, CalendarView, StatsView
│   │   ├── locales/               # zh.json, en.json
│   │   ├── composables/           # useApi.js, useI18n.js
│   │   ├── router/
│   │   ├── App.vue
│   │   └── main.js
│   ├── index.html
│   ├── vite.config.js             # /api 代理到 localhost:8000
│   ├── tailwind.config.js         # 主色：橙色
│   └── package.json
└── README_zh.md
```

---

## 📊 数据模型

### `birthdays` 表

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `id` | Integer PK | 主键 |
| `name` | String(100) | 姓名 |
| `solar_date` | String(10) | 公历日期 `YYYY-MM-DD` |
| `lunar_date` | String(20) | 农历日期字符串 |
| `is_lunar` | Boolean | 是否农历生日 |
| `is_leap_month` | Boolean | 是否农历闰月 |
| `category` | String(50) | 分类（家人/朋友/同事/同学/客户/其他） |
| `remark` | Text | 备注 |
| `is_enabled` | Boolean | 提醒是否启用 |
| `created_at` | DateTime | 创建时间 |
| `updated_at` | DateTime | 更新时间 |

> **注意**：农历只保存月、日，不保存年份。计算即将到来时用当前年份进行转换。这是有意设计——大多数人记得农历生日是几月几日，不记得农历出生年份。

---

## 🔌 接口列表

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/api/birthdays` | 列表（支持 `keyword` 和 `category` 筛选） |
| GET | `/api/birthdays/upcoming?days=30` | 即将到来的生日 |
| GET | `/api/birthdays/stats` | 统计 |
| GET | `/api/birthdays/calendar?year=&month=` | 指定月份的日历数据 |
| GET | `/api/birthdays/{id}` | 获取单条 |
| POST | `/api/birthdays` | 新增 |
| PUT | `/api/birthdays/{id}` | 编辑 |
| DELETE | `/api/birthdays/{id}` | 删除 |

所有列表响应均附带 `upcoming_date` 和 `days_until`（后端实时计算）。

---

## ⏰ 提醒系统

- **调度**：每天 09:00（Asia/Shanghai）
- **提前天数**：30、15、7、1 天
- **渠道**：邮件（SMTP）+ Server酱
- **去重**：同一人的同一提前窗口不重复通知

### 配置

编辑 `backend/app/core/config.py`：

```python
EMAIL_CONFIG = {
    "enabled": True,         # 改为 True 启用
    "smtp_host": "smtp.163.com",   # 或 smtp.qq.com / smtp.gmail.com
    "smtp_port": 587,
    "smtp_user": "your@email.com",
    "smtp_pass": "your_app_password",   # 不是登录密码！
    "from_name": "🎂 生日提醒",
    "to_email": "notify@example.com",
}

SERVERCHAN_CONFIG = {
    "enabled": True,         # 改为 True 启用
    "sckey": "SCT...",      # 去 sc.ftqq.com 注册获取
}

REMIND_AHEAD_DAYS = [30, 15, 7, 1]
```

### 手动运行调度器

```powershell
cd D:\project\yearn\backend
$env:PYTHONPATH = "D:\project\yearn\backend"
python -m app.scheduler
```

---

## 🌍 国际化

应用内置中英文支持，导航栏可随时切换，语言偏好保存在 `localStorage`。

添加新语言：
1. 创建 `frontend/src/locales/{lang}.json`
2. 在 `useI18n.js` 的支持列表中加入 `{lang}`
3. 在 `App.vue` 中添加切换选项

---

## 🎨 设计风格

- **主色**：暖橙 / 珊瑚色（`#f97316` → `#fb7185`）
- **风格**：简洁现代，圆角卡片，渐变头像
- **布局**：侧边栏 + 主内容区，完全响应式
- **暗色模式**：导航栏切换，持久化

---

## 🛠️ 开发指南

### 新增 API 接口

1. 在 `services/birthday.py` 添加方法
2. 在 `routers/birthday.py` 添加路由
3. 需要时在 `schemas/birthday.py` 添加 schema

### 新增前端页面

1. 在 `src/views/` 创建 `.vue` 文件
2. 在 `src/router/index.js` 添加路由
3. 在 `App.vue` 添加导航链接

### 修改提醒逻辑

- 发送逻辑 → `services/reminder.py`
- 调度/时间 → `scheduler.py`
- 提前天数 → `core/config.py`

---

## ❓ 常见问题

<details>
<summary><b>pip install 报 pydantic-core 编译错误</b></summary>

使用 Python 3.11+（有预编译 wheel）。Python 3.14 用户请先升级 pip：

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```
</details>

<details>
<summary><b>端口 8000 / 5173 被占用</b></summary>

```powershell
Get-NetTCPConnection -LocalPort 8000 -State Listen | Select OwningProcess | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }
```
</details>

<details>
<summary><b>提醒不发送</b></summary>

1. 检查 `config.py` — `enabled` 必须为 `True`
2. 确认 SMTP 凭证 / Server酱 SCKEY 正确
3. 确认调度器已启动（查看后端日志）
4. 确认该人的 `is_enabled` 为 `True`
</details>

<details>
<summary><b>改了数据库表结构后报错</b></summary>

删除 `birthday.db` 重启即可，SQLAlchemy 启动时会自动建表。  
有数据要保留时请用 Alembic 做迁移。
</details>

---

## 📄 许可证

MIT License

---

<p align="center">
  <strong>Yearn · 岁岁念</strong><br>
  用 🧡 制作，记住每一个重要的生日。
</p>
