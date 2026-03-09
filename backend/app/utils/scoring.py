from datetime import date, timedelta


def calculate_score(completed_dates: list[date], mood_map: dict[date, int] = None) -> int:
    """
    Calculate a 0-100 habit score based on 4 weighted factors:
      - Completion rate last 30 days  → 40 pts
      - Current streak                → 30 pts
      - Mood average                  → 20 pts
      - Consistency (no big gaps)     → 10 pts

    Args:
        completed_dates: list of date objects when habit was completed
        mood_map: optional dict of {date: mood(1-5)} for mood scoring

    Returns:
        int score 0-100
    """
    if not completed_dates:
        return 0

    mood_map = mood_map or {}
    today = date.today()
    unique_dates = sorted(set(completed_dates))

    # ── Factor 1: Completion rate last 30 days (40 pts) ──────────────────────
    last_30_start = today - timedelta(days=29)
    days_in_window = 30
    completions_in_window = sum(
        1 for d in unique_dates if last_30_start <= d <= today
    )
    completion_rate = completions_in_window / days_in_window
    factor_completion = round(completion_rate * 40)

    # ── Factor 2: Current streak (30 pts) ────────────────────────────────────
    # Max streak for full score = 30 days
    MAX_STREAK_FOR_FULL = 30
    current_streak = _current_streak(unique_dates, today)
    factor_streak = round(min(current_streak / MAX_STREAK_FOR_FULL, 1.0) * 30)

    # ── Factor 3: Mood average (20 pts) ──────────────────────────────────────
    # Only count moods from last 30 days
    recent_moods = [
        mood_map[d] for d in unique_dates
        if d in mood_map and last_30_start <= d <= today
    ]
    if recent_moods:
        avg_mood = sum(recent_moods) / len(recent_moods)
        # Mood 1-5 → 0-1 scale
        mood_ratio = (avg_mood - 1) / 4
        factor_mood = round(mood_ratio * 20)
    else:
        # No mood data — give neutral score (half points)
        factor_mood = 10

    # ── Factor 4: Consistency — no big gaps (10 pts) ─────────────────────────
    # Look at last 30 days only. Penalize gaps > 3 days.
    recent_dates = [d for d in unique_dates if last_30_start <= d <= today]
    factor_consistency = _consistency_score(recent_dates, last_30_start, today)

    total = factor_completion + factor_streak + factor_mood + factor_consistency
    return max(0, min(100, total))


def _current_streak(sorted_dates: list[date], today: date) -> int:
    """Calculate current streak from sorted ascending dates."""
    if not sorted_dates:
        return 0

    yesterday = today - timedelta(days=1)
    last = sorted_dates[-1]

    if last == today:
        anchor = today
    elif last == yesterday:
        anchor = yesterday
    else:
        return 0

    streak = 0
    expected = anchor
    for d in reversed(sorted_dates):
        if d == expected:
            streak += 1
            expected -= timedelta(days=1)
        elif d < expected:
            break

    return streak


def _consistency_score(recent_dates: list[date], start: date, end: date) -> int:
    """
    Award 0-10 pts based on largest gap between check-ins.
    Gap <= 2 days → 10 pts (perfect)
    Gap <= 4 days → 7 pts
    Gap <= 7 days → 4 pts
    Gap >  7 days → 0 pts
    """
    if not recent_dates:
        return 0

    if len(recent_dates) == 1:
        return 5  # only one check-in, neutral

    max_gap = 0
    for i in range(1, len(recent_dates)):
        gap = (recent_dates[i] - recent_dates[i - 1]).days
        max_gap = max(max_gap, gap)

    # Also count gap from last check-in to today
    gap_to_today = (end - recent_dates[-1]).days
    max_gap = max(max_gap, gap_to_today)

    if max_gap <= 2:
        return 10
    elif max_gap <= 4:
        return 7
    elif max_gap <= 7:
        return 4
    else:
        return 0
