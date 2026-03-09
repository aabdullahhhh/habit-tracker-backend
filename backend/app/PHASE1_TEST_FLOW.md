# Phase 1 — Postman Test Flow

## 1. Register
POST /api/auth/register
{ "username": "alice", "email": "alice@test.com", "password": "secret123" }

## 2. Login
POST /api/auth/login
{ "email": "alice@test.com", "password": "secret123" }

## 3. Create a category
POST /api/categories/
{ "name": "Health", "color": "#22c55e" }
→ save the returned `id` as {{category_id}}

## 4. Create a habit (with category)
POST /api/habits/
{ "name": "Morning run", "category_id": {{category_id}}, "frequency_type": "daily" }
→ save returned `id` as {{habit_id}}

## 5. Check in today with mood + note
POST /api/habits/{{habit_id}}/logs/
{ "mood": 4, "note": "Felt great, did 5km" }
→ expect 201, current_streak: 1

## 6. Try duplicate check-in (should fail)
POST /api/habits/{{habit_id}}/logs/
{ "mood": 3 }
→ expect 409 "Already checked in today"

## 7. Get full log history + streaks
GET /api/habits/{{habit_id}}/logs/
→ expect logs array, streak numbers

## 8. Undo today's check-in
DELETE /api/habits/{{habit_id}}/logs/
→ expect 200

## 9. Archive habit
PATCH /api/habits/{{habit_id}}/archive
→ expect is_archived: true

## 10. Unarchive habit
PATCH /api/habits/{{habit_id}}/unarchive
→ expect is_archived: false

## 11. Rename category
PATCH /api/categories/{{category_id}}
{ "name": "Fitness", "color": "#3b82f6" }

## 12. Delete category
DELETE /api/categories/{{category_id}}
→ habit's category_id should be nulled, not deleted
