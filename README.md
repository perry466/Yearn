<div align="center">

# 🎂 Yearn · 岁岁念
### 岁岁念 — 年年岁岁，惦念不忘

> A warm, modern birthday reminder app with full lunar calendar support · FastAPI + Vue 3

[![简体中文](https://img.shields.io/badge/简体中文-查看中文文档-ff6b9d?style=for-the-badge)](./README_zh.md)
![License: MIT](https://img.shields.io/badge/License-MIT-4a90d9?style=for-the-badge)

</div>

---

> 📘 **This guide is in English.** Prefer 中文? → **[查看中文文档 →](./README_zh.md)**

## 📸 Screenshots

<table>
  <tr>
    <td align="center" width="33%">
      <a href="./docs/screenshots/home_list.png"><img src="./docs/screenshots/home_list.png" alt="Home (List View)" width="100%"/></a>
      <br/><b>🏠 Home</b> · upcoming strip + list/cards + pagination
    </td>
    <td align="center" width="33%">
      <a href="./docs/screenshots/calendar.png"><img src="./docs/screenshots/calendar.png" alt="Calendar" width="100%"/></a>
      <br/><b>📅 Calendar</b> · lunar + solar, today highlighted
    </td>
    <td align="center" width="33%">
      <a href="./docs/screenshots/stats.png"><img src="./docs/screenshots/stats.png" alt="Stats" width="100%"/></a>
      <br/><b>📊 Stats</b> · totals, by-category, distribution
    </td>
  </tr>
</table>

> 🔎 **Drill-down tip**: on the Stats page, click any overview card, bar, or pie slice to open the matching records in a modal.

---

## 🚀 Local Setup (from scratch)

> 💡 **Easiest way to run the whole project** — one backend process serves the API **and** the built frontend, and the reminder scheduler starts automatically.

```bash
git clone https://github.com/perry466/Yearn.git
cd Yearn/backend
pip install -r requirements.txt        # 1) backend dependencies

cd ../frontend
npm install
npm run build                          # 2) IMPORTANT: builds frontend/dist (not in git)

cd ../backend
python run.py                          # 3) starts API + scheduler + serves frontend
```

Then open **http://localhost:8000**. Stop anytime with `python stop.py`.

> ⚠️ `frontend/dist` is git-ignored, so **you must run `npm run build` once** after cloning, or the web UI will be blank. Full walkthrough → [Usage Guide](./docs/USAGE.md).

---

## 📑 Table of Contents

> 📱 **New here?** Start with the **[Usage Guide (English)](./docs/USAGE.md)** · **[使用指南（中文）](./docs/USAGE_zh.md)** — screenshots + how to use every page.

- [📋 1. Requirements](#1-requirements)
- [📁 2. Project Structure](#2-project-structure)
- [🚀 3. Quick Start](#3-quick-start)
- [🌐 4. LAN Server Access](#4-lan-server-access)
- [🏭 5. Production Deployment](#5-production-deployment)
- [🔔 6. Reminder System](#6-reminder-system)
- [💾 7. Data Model](#7-data-model)
- [🔌 8. API Reference](#8-api-reference)
- [❓ 9. FAQ](#9-faq)
- [🔧 10. Development](#10-development)

---

## 📋 1. Requirements

| Dependency | Version | Notes |
| --- | --- | --- |
| Python | 3.11+ | 3.11/3.12 recommended (prebuilt wheels) |
| Node.js | 18+ | Frontend runtime |
| npm | 9+ | Ships with Node |
| Git | any | To clone the code |

---

## 📁 2. Project Structure

```
yearn/
├── backend/                # Backend (FastAPI + SQLite)
│   ├── app/
│   │   ├── core/           # config.py (reminders), database.py
│   │   ├── models/         # ORM models
│   │   ├── schemas/        # Pydantic models (field validation)
│   │   ├── services/       # lunar, reminder, birthday (CRUD)
│   │   ├── routers/        # REST endpoints
│   │   ├── scheduler.py    # daily reminder scheduler
│   │   └── main.py         # entry point
│   ├── requirements.txt
│   ├── reset_100.py        # generate 100 test records
│   └── birthday.db         # SQLite DB (auto-created on first run)
├── frontend/               # Frontend (Vue 3 + Vite)
│   ├── src/
│   ├── vite.config.js      # host / allowedHosts / /api proxy configured
│   └── package.json
├── README.md               # this file (English)
└── README_zh.md            # Chinese guide
```

---

## 🚀 3. Quick Start

> **Recommended — single service (one command):** install deps, build the frontend
> once, then a single backend process serves **both** the API and the built frontend,
> and the reminder scheduler starts automatically.

```bash
cd /path/to/yearn/backend
pip install -r requirements.txt
cd ../frontend && npm install && npm run build   # builds frontend/dist (required, not in git)
cd ../backend
python run.py            # API + scheduler + serves frontend on :8000
```

Open **http://localhost:8000**. Stop anytime with `python stop.py`.

> `frontend/dist` is git-ignored, so you must run `npm run build` once after cloning,
> otherwise the web UI is blank. Prefer editing reminders in the web **Settings** page
> (`/settings`) instead of config files.

### 3.1 Backend (standalone / dev API)

```bash
cd /path/to/yearn/backend

# create & activate a virtualenv (first time)
python3 -m venv venv
source venv/bin/activate

# install dependencies (first time)
pip install -r requirements.txt

# run (listen on all interfaces for LAN access)
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

- API root: `http://<server-ip-or-host>:8000`
- Swagger docs: `http://<server-ip-or-host>:8000/docs`
- `birthday.db` is created automatically on first start.
- When `frontend/dist` exists, this same process also serves the web UI at `/`.

> **Windows (PowerShell)** differences: `cd backend`, then
> `python -m venv venv`, `.\venv\Scripts\Activate.ps1`, `pip install -r requirements.txt`,
> `uvicorn app.main:app --host 0.0.0.0 --port 8000`.
>
> **About PYTHONPATH**: running from inside `backend/` already puts the current dir on
> the Python path, so no extra setup is needed. To run from another directory,
> `export PYTHONPATH=/path/to/yearn/backend` first. (Or just use `python run.py`, which
> sets the path for you.)

### 3.2 Frontend dev server (optional, hot-reload)

If you want live reload while developing, run the frontend separately on `:5173`
(it proxies `/api` to the backend on `:8000`):

```bash
cd /path/to/yearn/frontend
npm install
npm run dev
```

- App: `http://<server-ip-or-host>:5173`
- e.g. on your box: `http://roc-ubuntu.local:5173`

### 3.3 Seed test data (optional)

```bash
cd /path/to/yearn/backend
source venv/bin/activate
python reset_100.py        # wipes and generates 100 random records
```

> This script deletes all existing data first — **do not run it in production**.

---

## 🌐 4. LAN Server Access

`frontend/vite.config.js` is already configured for LAN access:

```js
server: {
  host: true,                                   // listen on 0.0.0.0
  allowedHosts: ['roc-ubuntu.local', 'localhost', '127.0.0.1'],
  proxy: { '/api': { target: 'http://localhost:8000', changeOrigin: true } },
}
```

- If you access via **IP** (e.g. `192.168.1.10:5173`) instead of a `.local` name,
  change `allowedHosts` to `true` (allow all hosts), otherwise the browser shows
  *“Blocked request. This host is not allowed”*.
- For long-term exposure, prefer the production deployment below over `npm run dev`.

---

## 🏭 5. Production Deployment

`npm run dev` is a dev server — not ideal to leave running. Build static files (the
backend serves `frontend/dist` automatically) and, optionally, put Nginx in front as
a reverse proxy:

```bash
cd /path/to/yearn/frontend
npm install
npm run build          # output in frontend/dist/
```

Nginx example (`/etc/nginx/sites-available/yearn`):

```nginx
server {
    listen 80;
    server_name roc-ubuntu.local;   # or your domain / IP

    root /path/to/yearn/frontend/dist;
    index index.html;
    try_files $uri $uri/ /index.html;

    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Run the backend as a service (systemd / nohup):

```bash
cd /path/to/yearn/backend
source venv/bin/activate
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

> The reminder scheduler (daily 09:00 Asia/Shanghai, plus an immediate check on
> startup) is started automatically by the app — no separate process needed. The same
> `uvicorn app.main:app` process also serves the built `frontend/dist`, so a single
> service covers API + web UI + scheduler.

---

## 🔔 6. Reminder System

Reminders are configured **in the app** — open **Settings (🔔)** in the web UI
(`http://localhost:8000/settings` when running the single service). No code edits needed.

- **Schedule**: daily 09:00 (Asia/Shanghai), plus an immediate check on app startup.
- **Lead times**: choose 30 / 15 / 7 / 1 days (or add custom) in the Settings page.
- **Channels**: Email (SMTP) + ServerChan — toggle and fill credentials in the UI.
- **Message template**: edit with variables `{name}`, `{days}`, `{date}`, `{age}`, `{category}`.
- **Dedup**: same person + same lead window → no duplicate.
- **Scheduler**: starts automatically with the app (via FastAPI lifespan) — you do **not**
  need to launch it separately.

> **Advanced / fallback**: default values live in `backend/app/core/config.py`; the
> first-run values are stored in the DB `settings` table (written by the Settings page).
> `python -m app.scheduler` can still run the checker as a standalone process if you want
> to separate scheduling from the API.

---

## 💾 7. Data Model

| Field | Type | Description |
| --- | --- | --- |
| `id` | Integer PK | primary key |
| `name` | String(100) | name |
| `solar_date` | String(10) | solar date `YYYY-MM-DD` |
| `lunar_date` | String(20) | lunar date `YYYY-MM-DD` (lunar birthdays) |
| `is_lunar` | Boolean | whether lunar |
| `is_leap_month` | Boolean | whether leap month |
| `category` | String(50) | `家人/朋友/同事/同学/客户/other` |
| `remark` | Text | notes |
| `is_enabled` | Boolean | reminder enabled |
| `created_at` / `updated_at` | DateTime | timestamps |

> Lunar stores month/day only, not the year; "upcoming" is computed with the
> current year. This is intentional.

---

## 🔌 8. API Reference

| Method | Path | Description |
| --- | --- | --- |
| GET | `/api/birthdays` | List (supports `keyword`, `category`) |
| GET | `/api/birthdays/upcoming?days=30` | Birthdays within N days |
| GET | `/api/birthdays/stats` | Statistics |
| GET | `/api/birthdays/calendar?year=&month=` | A month's calendar data |
| GET | `/api/birthdays/{id}` | Single record |
| POST | `/api/birthdays` | Create |
| PUT | `/api/birthdays/{id}` | Update |
| DELETE | `/api/birthdays/{id}` | Delete |

List responses include real-time `upcoming_date` and `days_until`.

---

## ❓ 9. FAQ

**Q1: Browser says "Blocked request. This host is not allowed"**
A: Vite blocked a non-allowlisted host. `vite.config.js` already sets `host: true`
and `allowedHosts`. If accessing by IP, set `allowedHosts: true`.

**Q2: List / cards empty, console shows `/api/birthdays` 500**
A: Usually a `category` value outside the allowlist
(`家人/朋友/同事/同学/客户/other`) failing response validation. The code now
tolerates unknown categories (normalized to `other`) and the test script's
category value was fixed — **restart the backend** to recover. If it persists,
check the DB for odd `category` values.

**Q3: `pip install` fails with pydantic-core compile error**
A: Use Python 3.11+. If it still fails, `pip install --upgrade pip` first.

**Q4: Port 8000 / 5173 already in use**
Linux:
```bash
sudo lsof -i:8000
kill -9 <PID>
```
Windows (PowerShell):
```powershell
Get-NetTCPConnection -LocalPort 8000 -State Listen | Select OwningProcess | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }
```

**Q5: Schema changed and startup errors out**
A: Delete `backend/birthday.db` and restart (SQLAlchemy recreates tables).
For keeping existing data, use Alembic migrations.

**Q6: Reminders not sending**
A: Open **Settings (`/settings`)** and check: ① the channel (Email / ServerChan) is
enabled and its credentials are correct (SMTP app password / ServerChan SCKEY); ② at
least one lead time is selected; ③ the contact's `is_enabled=True`. The scheduler starts
automatically with the app, so no separate process is required.

---

## 🔧 10. Development

- **Add an endpoint**: method in `services/birthday.py` → route in
  `routers/birthday.py` → schema in `schemas/birthday.py` if needed.
- **Add a page**: `.vue` in `src/views/` → route in `src/router/index.js` →
  nav link in `App.vue`.
- **Change reminder logic**: sending in `services/reminder.py`, scheduling in
  `scheduler.py`, lead days in `core/config.py`.
- **Add a language**: create `src/locales/{lang}.json`, register in `useI18n.js`
  and `App.vue`.

---

## License

MIT License · Made with 🧡 for remembering every birthday that matters.
