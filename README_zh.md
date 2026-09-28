# Yearn · 岁岁念 — 使用与部署说明

> **Yearn** /jɜːn/ — v. to long for, to miss deeply
> **岁岁念** — 年年岁岁，惦念不忘
>
> 一个带农历支持、温暖现代的生日提醒应用（FastAPI + Vue 3）。

本文档以 **Linux / Ubuntu 局域网服务器部署** 为主线，Windows 仅作差异提示。

---

## 一、环境要求

| 依赖 | 版本 | 说明 |
| --- | --- | --- |
| Python | 3.11+ | 推荐 3.11/3.12，有预编译 wheel |
| Node.js | 18+ | 前端构建运行环境 |
| npm | 9+ | 随 Node 一起安装 |
| Git | 任意 | 拉取代码 |

---

## 二、项目结构

```
yearn/
├── backend/                # 后端（FastAPI + SQLite）
│   ├── app/
│   │   ├── core/           # config.py（提醒配置）、database.py
│   │   ├── models/         # ORM 模型
│   │   ├── schemas/        # Pydantic 模型（含字段校验）
│   │   ├── services/       # lunar（农历）、reminder（提醒）、birthday（CRUD）
│   │   ├── routers/        # REST 接口
│   │   ├── scheduler.py    # 每日提醒调度
│   │   └── main.py         # 入口
│   ├── requirements.txt
│   ├── reset_100.py        # 生成 100 条测试数据
│   └── birthday.db         # SQLite 数据库（首次运行自动生成）
├── frontend/               # 前端（Vue 3 + Vite）
│   ├── src/                # 源码
│   ├── vite.config.js      # 已配置 host / allowedHosts / /api 代理
│   └── package.json
├── README.md               # 英文说明
└── README_zh.md            # 本文件
```

---

## 三、快速启动（开发 / 局域网直接用）

> 默认约定：后端跑在 `0.0.0.0:8000`，前端 dev server 跑在 `0.0.0.0:5173`，
> 前端通过 `/api` 代理把请求转发到本机 `localhost:8000`。

### 1. 启动后端

```bash
cd /path/to/yearn/backend

# 创建并激活虚拟环境（首次）
python3 -m venv venv
source venv/bin/activate

# 安装依赖（首次）
pip install -r requirements.txt

# 启动（监听所有网卡，方便局域网访问）
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

- API 根地址：`http://<服务器IP或域名>:8000`
- 接口文档（Swagger）：`http://<服务器IP或域名>:8000/docs`
- 数据库 `birthday.db` 会在首次启动时自动创建。

> **Windows 差异**：用 PowerShell 时先 `cd backend`，再
> `python -m venv venv`、`.\venv\Scripts\Activate.ps1`、`pip install -r requirements.txt`、
> `uvicorn app.main:app --host 0.0.0.0 --port 8000`。
>
> **关于 PYTHONPATH**：只要在 `backend/` 目录下执行 `python -m uvicorn ...` 即可，
> 当前目录会自动加入 Python 路径，无需额外设置；若要从别的目录运行，
> 可 `export PYTHONPATH=/path/to/yearn/backend` 后再执行。

### 2. 启动前端

```bash
cd /path/to/yearn/frontend

# 安装依赖（首次）
npm install

# 启动开发服务器（已配置 host:true，监听 0.0.0.0）
npm run dev
```

- 应用地址：`http://<服务器IP或域名>:5173`
- 例如你这台机器：`http://roc-ubuntu.local:5173`

### 3. 初始化测试数据（可选）

```bash
cd /path/to/yearn/backend
source venv/bin/activate
python reset_100.py        # 清空并生成 100 条随机记录
```

> 该脚本会删除全部已有数据后重新随机生成，仅用于演示，**生产环境请勿执行**。

---

## 四、局域网 / 服务器访问说明

前端 `vite.config.js` 已经做了两件事，保证局域网可访问：

```js
server: {
  host: true,                                   // 监听 0.0.0.0，允许其他设备访问
  allowedHosts: ['roc-ubuntu.local', 'localhost', '127.0.0.1'],
  proxy: { '/api': { target: 'http://localhost:8000', changeOrigin: true } },
}
```

- 如果你用 **IP（如 `192.168.1.10:5173`）** 访问而不是 `.local` 域名，
  需要把 `allowedHosts` 改为 `true`（放行所有主机），否则浏览器会提示
  *“Blocked request. This host is not allowed”*。
- 生产环境**不建议**长期用 `npm run dev`，请走下面的「生产部署」方案。

---

## 五、生产部署建议（build + Nginx）

`npm run dev` 是开发服务器，不适合长期对外。建议构建静态文件并用 Nginx 反代后端：

```bash
cd /path/to/yearn/frontend
npm install
npm run build          # 产物在 frontend/dist/
```

Nginx 示例配置（`/etc/nginx/sites-available/yearn`）：

```nginx
server {
    listen 80;
    server_name roc-ubuntu.local;   # 或你的域名/IP

    # 前端静态文件
    root /path/to/yearn/frontend/dist;
    index index.html;
    try_files $uri $uri/ /index.html;

    # 后端 API 反代
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

后端用 systemd / nohup 常驻运行：

```bash
cd /path/to/yearn/backend
source venv/bin/activate
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

> 提醒调度（每日 09:00 Asia/Shanghai）需单独常驻运行：
> `python -m app.scheduler`（同样在 backend 目录下、venv 激活后执行）。

---

## 六、提醒系统

- **调度**：每天 09:00（Asia/Shanghai）
- **提前天数**：30、15、7、1 天
- **渠道**：邮件（SMTP）+ Server 酱
- **去重**：同一人的同一提前窗口不会重复通知

### 配置（`backend/app/core/config.py`）

```python
EMAIL_CONFIG = {
    "enabled": True,
    "smtp_host": "smtp.163.com",     # 或 smtp.qq.com / smtp.gmail.com
    "smtp_port": 587,
    "smtp_user": "your@email.com",
    "smtp_pass": "你的授权码",        # 注意：是邮箱授权码，不是登录密码
    "from_name": "🎂 生日提醒",
    "to_email": "notify@example.com",
}

SERVERCHAN_CONFIG = {
    "enabled": True,
    "sckey": "SCT...",               # 去 sc.ftqq.com 注册获取
}

REMIND_AHEAD_DAYS = [30, 15, 7, 1]
```

### 手动跑一次提醒检查

```bash
cd /path/to/yearn/backend
source venv/bin/activate
python -m app.scheduler
```

---

## 七、数据模型（birthdays 表）

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `id` | Integer PK | 主键 |
| `name` | String(100) | 姓名 |
| `solar_date` | String(10) | 公历日期 `YYYY-MM-DD` |
| `lunar_date` | String(20) | 农历日期 `YYYY-MM-DD`（农历生日才有） |
| `is_lunar` | Boolean | 是否农历生日 |
| `is_leap_month` | Boolean | 是否农历闰月 |
| `category` | String(50) | 分类：`家人/朋友/同事/同学/客户/other` |
| `remark` | Text | 备注 |
| `is_enabled` | Boolean | 提醒是否启用 |
| `created_at` / `updated_at` | DateTime | 时间戳 |

> 农历只存月、日，不存年份；计算「即将到来」时用当前年换算，这是有意设计。

---

## 八、接口一览

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/api/birthdays` | 列表（支持 `keyword`、`category` 筛选） |
| GET | `/api/birthdays/upcoming?days=30` | 未来 N 天内的生日 |
| GET | `/api/birthdays/stats` | 统计概览 |
| GET | `/api/birthdays/calendar?year=&month=` | 指定月日历数据 |
| GET | `/api/birthdays/{id}` | 单条详情 |
| POST | `/api/birthdays` | 新增 |
| PUT | `/api/birthdays/{id}` | 编辑 |
| DELETE | `/api/birthdays/{id}` | 删除 |

列表类响应都会附带实时计算的 `upcoming_date`（下一次生日公历日期）和 `days_until`（还有几天）。

---

## 九、常见问题

**Q1：浏览器提示 “Blocked request. This host is not allowed”**
A：Vite 拦截了非白名单主机。已在 `vite.config.js` 配好 `host: true` 与 `allowedHosts`。
若用 IP 访问，把 `allowedHosts` 改成 `true` 即可。

**Q2：列表 / 卡片没数据，控制台报 `/api/birthdays` 500**
A：通常是分类字段值不在白名单（`家人/朋友/同事/同学/客户/other`）导致响应校验失败。
代码已做容错（未知分类自动归一为 `other`）并修好了测试脚本的分类值，
**重启后端**即可恢复。若仍出现，检查数据库里是否有异常 `category` 值。

**Q3：pip install 报 pydantic-core 编译错误**
A：请用 Python 3.11+。若仍失败，先 `pip install --upgrade pip` 再装。

**Q4：端口 8000 / 5173 被占用**
Linux：
```bash
sudo lsof -i:8000      # 查占用进程
kill -9 <PID>          # 结束
```
Windows（PowerShell）：
```powershell
Get-NetTCPConnection -LocalPort 8000 -State Listen | Select OwningProcess | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }
```

**Q5：改了数据库表结构后启动报错**
A：删除 `backend/birthday.db` 重启即可（SQLAlchemy 会自动重建表）。
已有数据需保留时请用 Alembic 迁移。

**Q6：提醒没发出去**
A：依次检查：① `config.py` 里 `enabled=True`；② SMTP 授权码 / Server 酱 SCKEY 正确；
③ 调度器 `python -m app.scheduler` 在常驻运行；④ 该联系人 `is_enabled=True`。

---

## 十、开发指引（简）

- **加接口**：`services/birthday.py` 加方法 → `routers/birthday.py` 加路由 → 需要时在 `schemas/birthday.py` 加模型。
- **加页面**：`src/views/` 建 `.vue` → `src/router/index.js` 加路由 → `App.vue` 加导航。
- **改提醒逻辑**：发送在 `services/reminder.py`，调度在 `scheduler.py`，提前天数在 `core/config.py`。
- **加语言**：`src/locales/` 新建 `{lang}.json`，并在 `useI18n.js` 与 `App.vue` 注册。

---

## 许可证

MIT License · 用 🧡 制作，记住每一个重要的生日。
