# 🗓️ Daily Habit Tracker — Flask Backend

A clean, modular Flask backend scaffold for a daily habit tracker. Built for easy extension with JWT auth, stats, filtering, and gamification.

---

## Project Structure

```
habit-tracker/
├── run.py                   # App entrypoint
├── requirements.txt
└── app/
    ├── __init__.py          # App factory (create_app)
    ├── models/
    │   ├── db.py            # SQLAlchemy instance
    │   ├── user.py          # User model
    │   └── habit.py         # Habit model
    ├── routes/
    │   ├── auth.py          # /api/auth/* endpoints
    │   └── habits.py        # /api/habits/* endpoints
    └── utils/
        └── responses.py     # success() / error() helpers + validators
```

---

## Setup

```bash
pip install -r requirements.txt
python run.py
```

The SQLite database (`instance/habit_tracker.db`) is created automatically on first run.

---

## API Reference

All responses follow this envelope:

```json
{ "success": true,  "message": "...", "data": { ... } }
{ "success": false, "message": "...", "errors": [ ... ] }
```

### Auth  `/api/auth`

| Method | Path        | Body fields                       | Description          |
|--------|-------------|-----------------------------------|----------------------|
| POST   | `/register` | `username`, `email`, `password`   | Create a new user    |
| POST   | `/login`    | `email`, `password`               | Login (sets session) |
| POST   | `/logout`   | —                                 | Clear session        |
| GET    | `/me`       | —                                 | Current user info    |

### Habits  `/api/habits`  *(requires login)*

| Method | Path    | Body fields (all optional on PATCH)              | Description          |
|--------|---------|--------------------------------------------------|----------------------|
| POST   | `/`     | `name`*, `description`, `frequency`              | Create habit         |
| GET    | `/`     | —                                                | List all habits      |
| GET    | `/<id>` | —                                                | Get single habit     |
| PATCH  | `/<id>` | `name`, `description`, `frequency`, `is_active` | Update habit         |
| DELETE | `/<id>` | —                                                | Delete habit         |

`frequency` accepts: `daily` | `weekly` | `monthly` (default: `daily`)

---

## Extension Hooks

| Feature        | Where to add it                                    |
|----------------|----------------------------------------------------|
| JWT auth       | Replace `session` in `routes/auth.py`; add middleware in `__init__.py` |
| Habit logs     | Add `HabitLog` model → new blueprint `routes/logs.py` |
| Stats / streaks| New blueprint `routes/stats.py`                    |
| Filtering      | Add query params to `GET /api/habits/`             |
| Gamification   | Add `streak`, `xp` columns to `Habit` / `User`    |
