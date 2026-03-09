from datetime import date, timedelta


def calculate_streaks(completed_dates: list[date]) -> dict:
    """
    Given a list of completed dates (date objects, any order),
    returns current_streak, longest_streak, and total_completions.

    Rules:
    - A streak is consecutive calendar days.
    - "Current" streak counts back from today. If today is not checked in,
      we allow yesterday to still count (so checking in at 11:59pm doesn't
      kill a streak if you haven't opened the app yet today).
    - Duplicate dates are deduplicated before calculation.
    """
    if not completed_dates:
        return {
            "current_streak": 0,
            "longest_streak": 0,
            "total_completions": 0,
        }

    # Deduplicate and sort descending
    unique_dates = sorted(set(completed_dates), reverse=True)
    total_completions = len(unique_dates)

    today = date.today()
    yesterday = today - timedelta(days=1)

    # --- Current streak ---
    # Start from today or yesterday (whichever is the most recent check-in anchor)
    current_streak = 0
    if unique_dates[0] == today:
        anchor = today
    elif unique_dates[0] == yesterday:
        anchor = yesterday
    else:
        # Most recent check-in is older than yesterday — streak is broken
        anchor = None

    if anchor is not None:
        expected = anchor
        for d in unique_dates:
            if d == expected:
                current_streak += 1
                expected -= timedelta(days=1)
            elif d < expected:
                # Gap found — streak ends
                break

    # --- Longest streak ---
    # Walk dates in ascending order, track consecutive runs
    sorted_asc = sorted(unique_dates)
    longest_streak = 1
    run = 1

    for i in range(1, len(sorted_asc)):
        if sorted_asc[i] == sorted_asc[i - 1] + timedelta(days=1):
            run += 1
            longest_streak = max(longest_streak, run)
        else:
            run = 1

    return {
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "total_completions": total_completions,
    }
