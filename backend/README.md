habit-tracker/
├── run.py
├── requirements.txt
├── .env
└── app/
    ├── __init__.py
    ├── models/
    │   ├── db.py
    │   ├── user.py              ✅ done
    │   ├── habit.py             ✅ done (needs updates P1)
    │   ├── habit_log.py         🔨 Phase 1
    │   ├── category.py          🔨 Phase 1
    │   ├── habit_score.py       📊 Phase 2
    │   ├── partnership.py       👥 Phase 7
    │   ├── challenge.py         👥 Phase 7
    │   └── challenge_entry.py   👥 Phase 7
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