from settings.config_store import load_settings


def calculate_session_load(difficulty, duration_minutes,
                           context_switches, break_recovery):
    base = difficulty * duration_minutes
    penalty = context_switches * 2
    load = base + penalty - break_recovery
    return round(max(load, 0), 2)


def classify_daily_load(load):
    settings = load_settings()
    overload = settings["overload_threshold"]

    if load < 50:
        return "Light"
    elif load < 120:
        return "Moderate"
    elif load < overload:
        return "Heavy"
    else:
        return "Overload"
