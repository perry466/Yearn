# Yearn · 岁岁念

> **Yearn** /jɜːn/ — v. to long for, to miss deeply  
> **岁岁念** — 年年岁岁，惦念不忘

A warm, modern birthday reminder app with full lunar calendar support.  
一个带农历支持、温暖现代的生日提醒应用。

---

## ✨ Features · 功能特性

| EN | 中文 |
| --- | --- |
| Add / edit / delete birthdays (solar & lunar) | 增删改查生日（公历 + 农历） |
| Lunar date picker with leap month support | 农历选择器，支持闰月 |
| Auto solar ↔ lunar conversion | 公历 / 农历自动互转 |
| List view + Card view | 列表视图 + 卡片视图 |
| Calendar view (monthly) | 日历视图（按月） |
| "Upcoming" — next 30 days | 「即将到来」30 天提醒 |
| Stats overview with pie chart | 统计概览（含饼图） |
| Batch select & delete | 批量选择删除 |
| Pagination (page size persisted) | 分页（每页条数持久化） |
| Dark mode | 暗色模式 |
| i18n — Chinese / English toggle | 中英文切换 |
| Email + ServerChan reminders (30/15/7/1 days ahead) | 邮件 + Server酱提醒（提前 30/15/7/1 天） |
| Responsive design | 响应式布局 |

---

## 🧱 Tech Stack · 技术栈

| Layer | Technology |
| --- | --- |
| Backend | Python · FastAPI · SQLAlchemy · SQLite |
| Frontend | Vue 3 · Vite · TailwindCSS · Axios |
| Lunar | `lunardate` Python library |
| Scheduler | APScheduler (cron 09:00 Asia/Shanghai) |
| Reminders | SMTP Email + ServerChan (Server酱) |

---

## 🚀 Quick Start · 快速开始

### Prerequisites · 环境要求

- Python 3.11+ (tested on 3.11 & 3.14)
- Node.js 18+
- npm 9+

### Backend · 后端

```powershell
cd D:\project\yearn\backend
$env:PYTHONPATH = "D:\project\yearn\backend"
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

API runs at `http://localhost:8000`  
Swagger docs at `http://localhost:8000/docs`

### Frontend · 前端

```powershell
cd D:\project\yearn\frontend
npm install
npm run dev
```

App runs at `http://localhost:5173`

### Test Data · 测试数据

```powershell
cd D:\project\yearn\backend
$env:PYTHONPATH = "D:\project\yearn\backend"
python reset_100.py    # generates 100 random records
```

---

## 📁 Project Structure · 项目结构

```
yearn/
├── backend/
│   ├── app/
│   │   ├── core/
│   │   │   ├── config.py          # Settings (email, ServerChan, reminders)
│   │   │   └── database.py        # SQLite engine & session
│   │   ├── models/
│   │   │   └── birthday.py        # Birthday ORM model
│   │   ├── schemas/
│   │   │   └── birthday.py        # Pydantic schemas
│   │   ├── services/
│   │   │   ├── lunar.py           # Solar ↔ lunar conversion
│   │   │   ├── reminder.py        # Email + ServerChan sending
│   │   │   └── birthday.py        # CRUD + stats logic
│   │   ├── routers/
│   │   │   └── birthday.py        # REST API routes
│   │   ├── scheduler.py           # APScheduler daily check
│   │   └── main.py                # FastAPI app entry
│   ├── requirements.txt
│   ├── reset_100.py               # Generate test data
│   └── generate_test_data.py      # Generate 500 records
├── frontend/
│   ├── src/
│   │   ├── assets/
│   │   ├── components/
│   │   │   ├── BirthdayCard.vue
│   │   │   ├── BirthdayTable.vue
│   │   │   ├── BirthdayModal.vue
│   │   │   └── ConfirmModal.vue
│   │   ├── composables/
│   │   │   └── useApi.js          # Axios API wrapper
│   │   ├── views/
│   │   │   ├── HomeView.vue
│   │   │   ├── CalendarView.vue
│   │   │   └── StatsView.vue
│   │   ├── router/
│   │   │   └── index.js
│   │   ├── locales/
│   │   │   ├── zh.json            # Chinese strings
│   │   │   └── en.json            # English strings
│   │   ├── composables/
│   │   │   └── useI18n.js         # i18n composable
│   │   ├── App.vue
│   │   └── main.js
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── postcss.config.js
├── docs/
│   └── project_plan_20260928.md
└── README.md
```

---

## 📊 Data Model · 数据模型

### `birthdays` table

| Field | Type | Description · 说明 |
| --- | --- | --- |
| `id` | Integer PK | Primary key · 主键 |
| `name` | String(100) | Name · 姓名 |
| `solar_date` | String(10) | Solar date `YYYY-MM-DD` · 公历日期 |
| `lunar_date` | String(20) | Lunar date string · 农历日期 |
| `is_lunar` | Boolean | Whether birthday is lunar · 是否农历 |
| `is_leap_month` | Boolean | Whether lunar month is leap · 是否闰月 |
| `category` | String(50) | Category · 分类 (家人/朋友/同事/同学/客户/其他) |
| `remark` | Text | Notes · 备注 |
| `is_enabled` | Boolean | Reminder enabled · 是否启用提醒 |
| `created_at` | DateTime | Created time · 创建时间 |
| `updated_at` | DateTime | Updated time · 更新时间 |

> **Note · 说明**: Only month + day are stored from the lunar date; the year is not kept. When computing upcoming birthdays, the current year is used for conversion. This is a deliberate trade-off — most users remember birthdays by lunar month/day, not the lunar birth year.  
> 农历只保存月、日，不保存年份。计算即将到来时用当前年转换。这是有意设计——大多数人记得农历生日是几月几日，不记得农历出生年份。

---

## 🔌 API Reference · 接口列表

| Method | Path | Description · 说明 |
| --- | --- | --- |
| GET | `/api/birthdays` | List all · 列表 |
| GET | `/api/birthdays/upcoming?days=30` | Upcoming · 即将到来 |
| GET | `/api/birthdays/stats` | Statistics · 统计 |
| GET | `/api/birthdays/calendar?year=&month=` | Calendar · 日历 |
| GET | `/api/birthdays/{id}` | Get one · 详情 |
| POST | `/api/birthdays` | Create · 新增 |
| PUT | `/api/birthdays/{id}` | Update · 编辑 |
| DELETE | `/api/birthdays/{id}` | Delete · 删除 |

---

## ⏰ Reminder System · 描醒系统

- **Schedule · 调度**: Every day at 09:00 (Asia/Shanghai)  
  每天 09:00（Asia/Shanghai）
- **Advance days · 提前天数**: 30, 15, 7, 1 days before  
  提前 30/15/7/1 天
- **Channels · 提醒渠道**:
  - Email (SMTP) — needs config in `core/config.py`  
    邮件（SMTP）— 需在 `core/config.py` 配置
  - ServerChan (Server酱) — needs SCKEY  
    Server酱 — 需配置 SCKEY
- **Dedup · 去重**: Same person won't be notified twice for the same advance window  
  同一人同一提前窗口不重复通知

### Configuration · 配置

Edit `backend/app/core/config.py`:

```python
EMAIL_CONFIG = {
    "enabled": False,        # Set True to enable
    "smtp_host": "",
    "smtp_port": 465,
    "smtp_user": "",
    "smtp_pass": "",
    "from_addr": "",
    "to_addrs": [""],
}

SERVERCHAN_CONFIG = {
    "enabled": False,        # Set True to enable
    "sckey": "",
}

REMIND_AHEAD_DAYS = [30, 15, 7, 1]
```

---

## 🌍 Internationalization · 国际化

The app supports Chinese and English with a runtime toggle in the navbar.  
Language preference is persisted in `localStorage`.  
应用支持中英文运行时切换，导航栏有切换按钮，选择保存在 `localStorage`。

To add a new language:  
添加新语言：

1. Create `frontend/src/locales/{lang}.json`
2. Add `{lang}` to `useI18n.js` supported list
3. Add toggle option in `App.vue`

---

## 🎨 UI Design · 设计风格

- **Primary color · 主色**: Warm orange / coral (`#f97316` → `#fb7185`)  
  暖橙 / 珊瑚色
- **Style · 风格**: Clean, modern, rounded cards, gradient avatars  
  简洁现代，圆角卡片，渐变头像
- **Layout · 布局**: Sidebar + main content, responsive  
  侧边栏 + 主内容区，响应式
- **Dark mode · 暗色模式**: Toggle in navbar, persisted  
  导航栏切换，持久化

---

## 🛠️ Development Guide · 开发指南

### Add a new API endpoint · 新增接口

1. Add method in `services/birthday.py`
2. Add route in `routers/birthday.py`
3. Add schema in `schemas/birthday.py` if needed

### Add a new frontend view · 新增页面

1. Create `.vue` in `src/views/`
2. Add route in `src/router/index.js`
3. Add nav link in `App.vue`

### Modify reminder logic · 修改提醒逻辑

- Edit `services/reminder.py` for send logic  
  发送逻辑改 `reminder.py`
- Edit `scheduler.py` for schedule/timing  
  调度时间改 `scheduler.py`
- Edit `core/config.py` for advance days  
  提前天数改 `config.py`

---

## ❓ FAQ · 常见问题

<details>
<summary><b>pip install fails with pydantic-core compilation error · pip 安装报 pydantic-core 编译错误</b></summary>

Use Python 3.11+ with pre-built wheels. If on Python 3.14, ensure `pip` is upgraded:  
使用 Python 3.11+ 预编译 wheel。Python 3.14 用户请先升级 pip：

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```
</details>

<details>
<summary><b>Port 8000 / 5173 already in use · 端口被占用</b></summary>

```powershell
# Find and kill process using port 8000
Get-NetTCPConnection -LocalPort 8000 -State Listen | Select OwningProcess | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }
```
</details>

<details>
<summary><b>Reminders not sending · 提醒不发</b></summary>

1. Check `config.py` — `enabled` must be `True`
2. Verify SMTP credentials / ServerChan SCKEY
3. Check scheduler started (see backend logs)
4. Verify person's `is_enabled` is `True`
</details>

<details>
<summary><b>Database schema changed · 数据库结构变了</b></summary>

Delete `birthday.db` and restart — SQLAlchemy auto-creates tables.  
删除 `birthday.db` 重启即可，SQLAlchemy 会自动建表。

For production data migration, use Alembic.  
生产数据迁移请用 Alembic。
</details>

---

## 📄 License · 许可证

MIT License — feel free to use, modify, and share.  
MIT 许可证——自由使用、修改、分享。

---

## 🤝 Contributing · 贡献

Issues and PRs welcome at the project repository.  
欢迎在项目仓库提交 Issue 和 PR。

---

<p align="center">
  <strong>Yearn · 岁岁念</strong><br>
  Made with 🧡 for remembering every birthday that matters.<br>
  用 🧡 制作，记住每一个重要的生日。
</p>
