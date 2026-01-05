from engine.cognitive import classify_daily_load
from storage.database import get_daily_summary

def print_daily_report():
    today, history = get_daily_summary()

    print("\n====== DAILY SUMMARY ======")
    if today:
        status = classify_daily_load(today[0])
        print(f"Today’s Load: {round(today[0], 2)} ({status})")
    else:
        print("No data for today yet.")

    print("\nLast 7 Days:")
    for d, load in history:
        print(f"{d} → {round(load, 2)}")

    print("===========================\n")
