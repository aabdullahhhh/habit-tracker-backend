# Phase 2 — Stats Test Flow
# Make sure you're logged in and have habit id=1 with at least one check-in

## 1. 30-day graph
GET /api/habits/1/stats/30-day
→ expect: array of 30 days, each with date + completed boolean
→ expect: total_completions, completion_rate

## 2. 365-day heatmap
GET /api/habits/1/stats/heatmap
→ expect: array of 365 days, each with date + completed boolean

## 3. Best day of week
GET /api/habits/1/stats/best-day
→ expect: best_day, worst_day, breakdown per day of week

## 4. Mood trend
GET /api/habits/1/stats/mood-trend
→ expect: mood_trend array, average_mood, trend_direction

## 5. Habit score
GET /api/habits/1/stats/score
→ expect: score (0-100), last_saved_score, last_calculated_at
