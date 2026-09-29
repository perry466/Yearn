# 🎂 Yearn · 岁岁念 — Usage Guide (English)

> This is the **"how to use it"** manual, for end users.
> For deployment / API / development, see the main docs: [README.md](../README.md) ｜ [中文](../README_zh.md)

Yearn is a birthday reminder app with **full lunar calendar support**: add friends & family birthdays (solar or lunar), and it tells you "how many days left" and reminds you via email / ServerChan as the date approaches.

---

## 📱 The Three Pages

The app has three main pages, switched from the top nav:

| Page | Purpose |
| --- | --- |
| 🏠 **Home** | "Upcoming" strip + all birthdays as list / cards |
| 📅 **Calendar** | Monthly calendar, solar + lunar side by side |
| 📊 **Stats** | Totals, by-category, distribution, with click-to-drill-down |

<p align="center">
  <img src="./screenshots/home_list.png" width="30%"/>
  <img src="./screenshots/calendar.png" width="30%"/>
  <img src="./screenshots/stats.png" width="30%"/>
</p>

---

## 🏠 Home

The default landing page.

### 1. Upcoming (horizontal strip)
A horizontally scrolling strip at the top shows **the next upcoming birthdays** — each card has the name, category, days-until, and next birthday date. Scroll / drag left-right to browse.

### 2. List / Card view toggle
Switch between **list view** and **card view** from the top-right. The choice is remembered (survives refresh).

- **List view**: one row per person — name, category badge, age, solar/lunar date, days-until.
- **Card view**: an avatar, name, category, and countdown per card — better on wide screens.

### 3. Category filter
Filter by category (Family / Friends / Colleagues / Classmates / Clients / Other) to see only one group.

### 4. Countdown
Every record shows a live "N days left". Birthdays today show "Today".

### 5. Pagination
Long lists paginate automatically; the pager is pinned to the bottom. Page size is a multiple of 3 (9 / 12 …).

### 6. Add birthday
Click "＋ Add Birthday" (top-right) to open the entry modal (see below).

---

## 📅 Calendar

Birthdays by month:

- Each day cell shows who has a birthday (name + small icon).
- **Solar + lunar shown together**: lunar birthdays highlight on the matching lunar day; solar birthdays are marked on the solar day.
- **Today highlighted**: the current date cell has a distinct background.
- Bottom shows "N people this month".
- Switch months with the prev / next controls.

> Lunar birthdays are stored as month + day and mapped to the current year, so the countdown stays correct every year.

---

## 📊 Stats

The Stats page gives you the big picture at a glance:

- **Overview cards (4)**:
  - 👥 **Total** — all birthday records
  - 🎂 **Within 30 days** — people with a birthday in the next 30 days
  - 📅 **This week** — within the next 7 days
  - 🎁 **Today** — people whose birthday is today
- **By-category bar chart**: head-count per category (6 categories).
- **Distribution pie**: category share (drawn as SVG).

### 🔍 Drill-down
Click **any overview card / category bar / pie slice or legend** to open a **detail list** for that dimension:

- Gender avatar + name + category badge + age + solar/lunar date + days-until.
- Cards, bars, and legends have hover feedback and a "click to view details" hint.
- The modal is browsable without leaving the current page.

> Drill-down is pure front-end filtering — no new backend endpoint needed.

---

## ➕ Add / Edit a Birthday

Click "＋ Add Birthday" to open the entry modal, organized into sections:

1. **Basics**: name (required), gender.
2. **Date picker**:
   - Toggle between **solar** and **lunar** with a unified segmented control.
   - Lunar mode: year + month + day dropdowns; days adjust dynamically (30 for big months, 29 for small); a **leap-month** switch is included.
   - Solar mode: max date is today.
3. **Category**: 6 categories as an Emoji icon grid (Family / Friends / Colleagues / Classmates / Clients / Other).
4. **Remark**: free text.
5. **Reminder**: enable/disable reminder (switch).

To edit: click the record in the list / card view — the same modal opens pre-filled.

---

## 🌗 Solar / Lunar

- **Solar birthday**: pick the solar date; same day every year.
- **Lunar birthday**: switch to lunar mode and pick the lunar year/month/day; the app maps it to the correct solar date each year for the countdown.
- **Leap month**: mark a lunar leap-month birthday with the "leap month" switch so it converts correctly.

---

## 🔔 Reminders

A backend scheduler checks daily at 09:00 (Asia/Shanghai) and sends reminders **30 / 15 / 7 / 1 days** ahead:

- **Channels**: Email (SMTP) + ServerChan.
- **Dedup**: the same person in the same lead window is never notified twice.
- **Toggle**: each record has its own reminder switch; the master switch lives in `backend/app/core/config.py`.
- **Setup**: fill in the SMTP app password / ServerChan SCKEY, then run the scheduler as a service: `python -m app.scheduler`.

See [README.md §6 (Reminder System)](../README.md#-6-reminder-system) for details.

---

## 💾 Data & Backup

- Data lives in `backend/birthday.db` (SQLite), auto-created on first start.
- If startup errors after a schema change, delete `birthday.db` and restart (rebuilds tables; existing data is wiped).
- Demo data: `backend/reset_100.py` (wipes then generates 100 random records — **not for production**).

---

## ❓ FAQ

- **List / cards empty?** Make sure the backend is up (default `:8000`) and the `/api` proxy works.
- **A birthday wasn't reminded?** Check that record's reminder switch, backend `enabled`, SMTP / SCKEY, and that the scheduler is running.
- **More troubleshooting**: see [README.md §9 (FAQ)](../README.md#-9-faq).

---

Made with 🧡 to remember every birthday that matters.
