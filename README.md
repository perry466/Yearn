# Yearn · 岁岁念

> **Yearn** /jɜːn/ — v. to long for, to miss deeply

A warm, modern birthday reminder app with full lunar calendar support.

**[中文说明](./README_zh.md)** | **[中文文档](./README_zh.md)**

---

## ✨ Features

- Add / edit / delete birthdays (solar & lunar)
- Lunar date picker with leap month support
- Auto solar ↔ lunar conversion
- List view + Card view
- Calendar view (monthly)
- "Upcoming" — next 30 days
- Stats overview with pie chart
- Batch select & delete
- Pagination (page size persisted in localStorage)
- Dark mode
- i18n — Chinese / English toggle at runtime
- Email + ServerChan reminders (30/15/7/1 days ahead)
- Responsive design

---

## 🧱 Tech Stack

| Layer | Technology |
| --- | --- |
| Backend | Python · FastAPI · SQLAlchemy · SQLite |
| Frontend | Vue 3 · Vite · TailwindCSS · Axios |
| Lunar | `lunardate` Python library |
| Scheduler | APScheduler (cron 09:00 Asia/Shanghai) |
| Reminders | SMTP Email + ServerChan |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- npm 9+

### Backend

```powershell
cd D:\project\yearn\backend
$env:PYTHONPATH = "D:\project\yearn\backend"
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

- API: `http://localhost:8000`
- Swagger docs: `http://localhost:8000/docs`

### Frontend

```powershell
cd D:\project\yearn\frontend
npm install
npm run dev
```

- App: `http://localhost:5173`

### Test Data

```powershell
cd D:\project\yearn\backend
$env:PYTHONPATH = "D:\project\yearn\backend"
python reset_100.py    # generates 100 random records
```

---

## 📁 Project Structure

```
yearn/
├── backend/
│   ├── app/
│   │   ├── core/
│   │   │   ├── config.py          # Email, ServerChan, reminder settings
│   │   │   └── database.py        # SQLite engine & session
│   │   ├── models/
│   │   │   └── birthday.py       # Birthday ORM model
│   │   ├── schemas/
│   │   │   └── birthday.py       # Pydantic schemas
│   │   ├── services/
│   │   │   ├── lunar.py          # Solar ↔ lunar conversion
│   │   │   ├── reminder.py       # Email + ServerChan
│   │   │   └── birthday.py       # CRUD + stats
│   │   ├── routers/
│   │   │   └── birthday.py      # REST API routes
│   │   ├── scheduler.py          # APScheduler daily check
│   │   └── main.py               # FastAPI entry point
│   ├── requirements.txt
│   └── reset_100.py              # Generate 100 test records
├── frontend/
│   ├── src/
│   │   ├── components/           # BirthdayCard, BirthdayTable, etc.
│   │   ├── views/                 # HomeView, CalendarView, StatsView
│   │   ├── locales/               # zh.json, en.json
│   │   ├── composables/           # useApi.js, useI18n.js
│   │   ├── router/
│   │   ├── App.vue
│   │   └── main.js
│   ├── index.html
│   ├── vite.config.js            # /api proxy → localhost:8000
│   ├── tailwind.config.js        # Primary color: orange
│   └── package.json
└── README.md
```

---

## 📊 Data Model

### `birthdays` table

| Field | Type | Description |
| --- | --- | --- |
| `id` | Integer PK | Primary key |
| `name` | String(100) | Name |
| `solar_date` | String(10) | Solar date `YYYY-MM-DD` |
| `lunar_date` | String(20) | Lunar date string |
| `is_lunar` | Boolean | Whether birthday is lunar calendar |
| `is_leap_month` | Boolean | Whether lunar month is leap |
| `category` | String(50) | Category |
| `remark` | Text | Notes |
| `is_enabled` | Boolean | Reminder enabled |
| `created_at` | DateTime | Created timestamp |
| `updated_at` | DateTime | Updated timestamp |

> **Note**: Only month + day are stored from the lunar date — the year is not kept. When computing upcoming birthdays, the current year is used for conversion. This is intentional — most users remember their lunar birthday by month/day, not the lunar birth year.

---

## 🔌 API Reference

| Method | Path | Description |
| --- | --- | --- |
| GET | `/api/birthdays` | List all (supports `keyword` & `category` filter) |
| GET | `/api/birthdays/upcoming?days=30` | Upcoming birthdays |
| GET | `/api/birthdays/stats` | Statistics |
| GET | `/api/birthdays/calendar?year=&month=` | Calendar view for a month |
| GET | `/api/birthdays/{id}` | Get one record |
| POST | `/api/birthdays` | Create |
| PUT | `/api/birthdays/{id}` | Update |
| DELETE | `/api/birthdays/{id}` | Delete |

All list responses include `upcoming_date` and `days_until` (computed in real-time).

---

## ⏰ Reminder System

- **Schedule**: Every day at 09:00 (Asia/Shanghai)
- **Advance days**: 30, 15, 7, 1 days before
- **Channels**: Email (SMTP) + ServerChan
- **Dedup**: Same person + same advance window → no duplicate notifications

### Configuration

Edit `backend/app/core/config.py`:

```python
EMAIL_CONFIG = {
    "enabled": True,         # Set True to enable
    "smtp_host": "smtp.163.com",   # or smtp.qq.com / smtp.gmail.com
    "smtp_port": 587,
    "smtp_user": "your@email.com",
    "smtp_pass": "your_app_password",   # Not your login password!
    "from_name": "🎂 Birthday Reminder",
    "to_email": "notify@example.com",
}

SERVERCHAN_CONFIG = {
    "enabled": True,         # Set True to enable
    "sckey": "SCT...",      # Get from sc.ftqq.com
}

REMIND_AHEAD_DAYS = [30, 15, 7, 1]
```

### Run Scheduler Manually

```powershell
cd D:\project\yearn\backend
$env:PYTHONPATH = "D:\project\yearn\backend"
python -m app.scheduler
```

---

## 🌍 Internationalization

The app supports Chinese and English with a runtime toggle in the navbar. Language preference is persisted in `localStorage`.

To add a new language:
1. Create `frontend/src/locales/{lang}.json`
2. Add `{lang}` to the supported list in `useI18n.js`
3. Add a toggle option in `App.vue`

---

## 🎨 Design

- **Primary color**: Warm orange/coral (`#f97316` → `#fb7185`)
- **Style**: Clean, modern, rounded cards, gradient avatars
- **Layout**: Sidebar + main content, fully responsive
- **Dark mode**: Toggle in navbar, persisted

---

## 🛠️ Development Guide

### Add a new API endpoint

1. Add method in `services/birthday.py`
2. Add route in `routers/birthday.py`
3. Add schema in `schemas/birthday.py` if needed

### Add a new frontend view

1. Create `.vue` in `src/views/`
2. Add route in `src/router/index.js`
3. Add nav link in `App.vue`

### Change reminder logic

- Send logic → `services/reminder.py`
- Schedule / timing → `scheduler.py`
- Advance days → `core/config.py`

---

## ❓ FAQ

<details>
<summary><b>pip install fails with pydantic-core compilation error</b></summary>

Use Python 3.11+ which has pre-built wheels. If on Python 3.14, upgrade pip first:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```
</details>

<details>
<summary><b>Port 8000 / 5173 already in use</b></summary>

```powershell
Get-NetTCPConnection -LocalPort 8000 -State Listen | Select OwningProcess | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }
```
</details>

<details>
<summary><b>Reminders not sending</b></summary>

1. Check `config.py` — `enabled` must be `True`
2. Verify SMTP credentials / ServerChan SCKEY
3. Confirm scheduler is running (check backend logs)
4. Verify the person's `is_enabled` is `True`
</details>

<details>
<summary><b>Database schema changed after code update</b></summary>

Delete `birthday.db` and restart — SQLAlchemy auto-creates tables on startup.  
For production with existing data, use Alembic for migrations.
</details>

---

## 📄 License

MIT License

---

<p align="center">
  <strong>Yearn · 岁岁念</strong><br>
  Made with 🧡 for remembering every birthday that matters.
</p>
