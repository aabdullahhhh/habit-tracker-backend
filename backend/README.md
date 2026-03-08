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
    │   ├── habits.py            ✅ done (needs updates P1)
    │   ├── logs.py              🔨 Phase 1
    │   ├── categories.py        🔨 Phase 1
    │   ├── stats.py             📊 Phase 2
    │   ├── ai_routes.py         🤖 Phase 3
    │   ├── partnerships.py      👥 Phase 7
    │   └── challenges.py        👥 Phase 7
    └── utils/
        ├── responses.py         ✅ done
        ├── streak.py            🔨 Phase 1
        ├── scoring.py           📊 Phase 2
        ├── scheduler.py         📊 Phase 2
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

### ✅ Phase 1 — Core Data Layer (Database Done)
- [x] `HabitLog` model — completed_date, mood (1–5), journal note
- [x] `Category` model — name, color, user-scoped
- [x] `HabitScore` model — 0–100 score, calculated_at
- [x] Habit updated — `category_id`, `frequency_type`, `frequency_days`, `is_archived`
- [x] Flask-Migrate set up — all 8 tables migrated ✅
- [ ] `logs.py` — check-in, undo, history endpoints
- [ ] `categories.py` — CRUD routes
- [ ] `streak.py` — current streak, longest streak logic
- [ ] Archive / unarchive endpoints

---

### 📊 Phase 2 — Stats & Insights Engine
- [ ] `stats.py` — 30-day graph, heatmap (365 days), best day of week, mood trend
- [ ] `habit_score.py` — 0–100 score model
- [ ] `scoring.py` — score calculation logic
- [ ] `scheduler.py` — APScheduler for daily score recalc + slip detection

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
| PATCH | `/:id/archive` | Archive habit | 🔨 P1 |
| PATCH | `/:id/unarchive` | Restore habit | 🔨 P1 |

### Logs — `/api/habits/:id/logs`
| Method | Endpoint | Description | Status |
|---|---|---|---|
| POST | `/` | Check in (mood + note) | 🔨 P1 |
| DELETE | `/` | Undo today's check-in | 🔨 P1 |
| GET | `/` | History + streak stats | 🔨 P1 |

### Categories — `/api/categories`
| Method | Endpoint | Description | Status |
|---|---|---|---|
| POST | `/` | Create category | 🔨 P1 |
| GET | `/` | List categories | 🔨 P1 |
| PATCH | `/:id` | Rename / recolor | 🔨 P1 |
| DELETE | `/:id` | Delete category | 🔨 P1 |

### Stats — `/api/habits/:id/stats`
| Method | Endpoint | Description | Status |
|---|---|---|---|
| GET | `/30-day` | Daily completions last 30 days | 📊 P2 |
| GET | `/heatmap` | 365 days of completion data | 📊 P2 |
| GET | `/best-day` | Best day of week insight | 📊 P2 |
| GET | `/mood-trend` | Mood over time | 📊 P2 |
| GET | `/score` | Current habit score (0–100) | 📊 P2 |

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
| 🔨 | Phase 1 — Core Data Layer |
| 📊 | Phase 2 — Stats & Insights |
| 🤖 | Phase 3 — AI Layer |
| 🌐 | Phase 4 — Frontend |
| 🔐 | Phase 5 — Auth Hardening |
| 📧 | Phase 6 — Notifications |
| 👥 | Phase 7 — Social |
| 🚀 | Phase 8 — Deployment |
| 📱 | Phase 9 — Mobile |