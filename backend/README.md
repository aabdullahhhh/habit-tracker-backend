# 🧠 Daily Habit Tracker

> A data-driven, AI-powered habit tracker that reveals behavioral patterns about yourself.

---

## 🚀 Tech Stack

| Layer | Technology |
|---|---|
| Backend | Flask + SQLAlchemy |
| Database | SQLite → PostgreSQL (Phase 8) |
| AI | Groq (Llama 3.1) — free |
| Frontend | React (Phase 4), React Native (Phase 9) |
| Auth | Session-based → JWT (Phase 5) |

---

## 📁 Project Structure

```
habit-tracker/
├── run.py
├── requirements.txt
├── .env
└── app/
    ├── __init__.py
    ├── models/
    │   ├── db.py                ✅ done
    │   ├── user.py              ✅ done
    │   ├── habit.py             ✅ done (updated P1)
    │   ├── habit_log.py         ✅ done (model + migration)
    │   ├── category.py          ✅ done (model + migration)
    │   ├── habit_score.py       ✅ done (model + migration)
    │   ├── partnership.py       👥 Phase 7 (skeleton)
    │   ├── challenge.py         👥 Phase 7 (skeleton)
    │   └── challenge_entry.py   👥 Phase 7 (skeleton)
    ├── routes/
    │   ├── auth.py              ✅ done
    │   ├── habits.py            ✅ done (archive/unarchive added P1)
    │   ├── logs.py              ✅ done (P1)
    │   ├── categories.py        ✅ done (P1)
    │   ├── stats.py             ✅ done (P2)
    │   ├── ai_routes.py         🤖 Phase 3
    │   ├── partnerships.py      👥 Phase 7
    │   └── challenges.py        👥 Phase 7
    └── utils/
        ├── responses.py         ✅ done
        ├── streak.py            ✅ done (P1)
        ├── scoring.py           ✅ done (P2)
        ├── scheduler.py         ✅ done (P2)
        ├── ai.py                🤖 Phase 3
        └── ai_context.py        🤖 Phase 3
```

---

## 🗺️ Build Phases

### ✅ Phase 0 — Foundation (Done)
- [x] User auth — register, login, logout, `/me`
- [x] Habits CRUD — create, list, get, update, delete
- [x] Input validation
- [x] Consistent `{ success, message, data }` response envelope

---

### ✅ Phase 1 — Core Data Layer (Done)
- [x] `HabitLog` model — completed_date, mood (1–5), journal note
- [x] `Category` model — name, color, user-scoped
- [x] `HabitScore` model — 0–100 score, calculated_at
- [x] Habit updated — `category_id`, `frequency_type`, `frequency_days`, `is_archived`
- [x] Flask-Migrate set up — all 8 tables migrated
- [x] `logs.py` — check-in, undo, history + streak endpoints
- [x] `categories.py` — full CRUD routes
- [x] `streak.py` — current streak, longest streak, total completions
- [x] Archive / unarchive endpoints in `habits.py`
- [x] Blueprints registered — logs, categories wired up in `__init__.py`

**Key decisions:**
- DATE not DATETIME for check-ins (timezone safety)
- "Not found" instead of "access denied" (prevents user enumeration)
- Soft delete for habits (`is_archived`) so history is preserved
- `frequency_days` stored as JSON string e.g. `[0,2,4]` = Mon/Wed/Fri
- Duplicate check-in blocked at route level + DB unique constraint

---

### ✅ Phase 2 — Stats & Insights Engine (Done)
- [x] `stats.py` — 5 endpoints: 30-day graph, 365-day heatmap, best day of week, mood trend, habit score
- [x] `scoring.py` — 0–100 habit score with 4 weighted factors:
  - Completion rate last 30 days → 40 pts
  - Current streak → 30 pts
  - Mood average → 20 pts
  - Consistency / no big gaps → 10 pts
- [x] `scheduler.py` — APScheduler background jobs:
  - Nightly score recalc at midnight
  - Slip detection at 8am (logs habits not checked in 2+ days)
- [x] Stats blueprint registered in `__init__.py`
- [x] APScheduler installed (`apscheduler==3.11.2`)

**Key decisions:**
- Score calculated live on GET + saved nightly by scheduler
- Scheduler skips during `flask db migrate/upgrade` to prevent crashes
- ISO date strings (`2026-03-10`) used throughout for frontend compatibility
- Mood trend includes direction: `improving`, `declining`, or `stable`

---

### 🤖 Phase 3 — AI Layer (Groq)
- [ ] `ai.py` — Groq API wrapper
- [ ] `ai_context.py` — formats DB data into prompts
- [ ] Check-in Companion — warm message on every check-in
- [ ] Personal Insight Coach — behavioral pattern analysis
- [ ] Smart Habit Setup — AI suggests habits from a user goal
- [ ] Slip Recovery Assistant — personalized bounce-back message
- [ ] Weekly Report Narrative — AI-written weekly summary

---

### 🌐 Phase 4 — Frontend (React Web)
- [ ] Auth screens (login, register)
- [ ] Dashboard — all habits, completion rings
- [ ] Habit detail — heatmap, streak, mood chart
- [ ] Check-in flow — mood slider + journal note + companion message
- [ ] Stats page — 30-day graph, bar charts, best day
- [ ] AI insight cards
- [ ] Weekly report screen
- [ ] Categories management
- [ ] Settings — profile, timezone, notification preferences

---

### 🔐 Phase 5 — Auth Hardening
- [ ] JWT + refresh tokens (replace sessions)
- [ ] Email verification on register
- [ ] Password reset flow
- [ ] Google OAuth
- [ ] Rate limiting on auth endpoints
- [ ] Timezone field on User model

---

### 📧 Phase 6 — Notifications
- [ ] Email via Resend (free tier)
- [ ] Slip detection emails
- [ ] Weekly report email delivery
- [ ] In-app notification center

---

### 👥 Phase 7 — Social
- [ ] Accountability Partners
- [ ] Challenges + Leaderboard
- [ ] Public shareable streak page

---

### 🚀 Phase 8 — Ship It
- [ ] SQLite → PostgreSQL migration
- [x] Flask-Migrate setup ✅
- [ ] Deploy to Render
- [ ] CI/CD via GitHub Actions
- [ ] Sentry error logging
- [ ] Health check endpoint `/api/health`
- [ ] Data export (CSV)
- [ ] Habit templates for onboarding

---

### 📱 Phase 9 — Mobile
- [ ] React Native app
- [ ] Shared API, same backend
- [ ] Push notifications
- [ ] Offline check-in sync

---

## 🔌 API Overview

### Auth — `/api/auth`
| Method | Endpoint | Description | Status |
|---|---|---|---|
| POST | `/register` | Create account | ✅ |
| POST | `/login` | Login | ✅ |
| POST | `/logout` | Logout | ✅ |
| GET | `/me` | Current user info | ✅ |

### Habits — `/api/habits`
| Method | Endpoint | Description | Status |
|---|---|---|---|
| POST | `/` | Create habit | ✅ |
| GET | `/` | List all habits | ✅ |
| GET | `/:id` | Get single habit | ✅ |
| PATCH | `/:id` | Update habit | ✅ |
| DELETE | `/:id` | Delete habit | ✅ |
| PATCH | `/:id/archive` | Archive habit | ✅ |
| PATCH | `/:id/unarchive` | Restore habit | ✅ |

### Logs — `/api/habits/:id/logs`
| Method | Endpoint | Description | Status |
|---|---|---|---|
| POST | `/` | Check in (mood + note) | ✅ |
| DELETE | `/` | Undo today's check-in | ✅ |
| GET | `/` | History + streak stats | ✅ |

### Categories — `/api/categories`
| Method | Endpoint | Description | Status |
|---|---|---|---|
| POST | `/` | Create category | ✅ |
| GET | `/` | List categories | ✅ |
| PATCH | `/:id` | Rename / recolor | ✅ |
| DELETE | `/:id` | Delete category | ✅ |

### Stats — `/api/habits/:id/stats`
| Method | Endpoint | Description | Status |
|---|---|---|---|
| GET | `/30-day` | Daily completions last 30 days | ✅ |
| GET | `/heatmap` | 365 days of completion data | ✅ |
| GET | `/best-day` | Best day of week insight | ✅ |
| GET | `/mood-trend` | Mood over time | ✅ |
| GET | `/score` | Current habit score (0–100) | ✅ |

### AI — `/api/ai`
| Method | Endpoint | Description | Status |
|---|---|---|---|
| POST | `/suggest` | Smart habit setup from a goal | 🤖 P3 |
| GET | `/habits/:id/insight` | Personal insight coach | 🤖 P3 |
| GET | `/habits/:id/slip-recovery` | Slip recovery message | 🤖 P3 |
| GET | `/weekly-report` | AI weekly narrative | 🤖 P3 |

### Social — `/api`
| Method | Endpoint | Description | Status |
|---|---|---|---|
| POST | `/partnerships` | Send partner request | 👥 P7 |
| PATCH | `/partnerships/:id` | Accept / reject | 👥 P7 |
| GET | `/partnerships` | List partners | 👥 P7 |
| POST | `/challenges` | Create challenge | 👥 P7 |
| POST | `/challenges/:id/join` | Join challenge | 👥 P7 |
| GET | `/challenges/:id/leaderboard` | Leaderboard | 👥 P7 |

---

## ⚡ Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/yourusername/habit-tracker.git
cd habit-tracker

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env

# 5. Run database migrations
set FLASK_APP=run.py        # Windows
# export FLASK_APP=run.py   # Mac/Linux
flask db upgrade

# 6. Run the server
python run.py
# Server runs at http://localhost:5000
```

---

## 📊 Response Format

Every API response follows this envelope:

```json
// Success
{ "success": true, "message": "Habit created.", "data": { ... } }

// Error
{ "success": false, "message": "Habit 'name' is required." }
```

---

## 🏷️ Legend

| Symbol | Meaning |
|---|---|
| ✅ | Done |
| 🤖 | Phase 3 — AI Layer |
| 🌐 | Phase 4 — Frontend |
| 🔐 | Phase 5 — Auth Hardening |
| 📧 | Phase 6 — Notifications |
| 👥 | Phase 7 — Social |
| 🚀 | Phase 8 — Deployment |
| 📱 | Phase 9 — Mobile |