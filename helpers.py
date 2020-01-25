from datetime import datetime


def is_night_now(night_starts_ts, night_ends_ts):
    now = datetime.now()
    pns = datetime.strptime(night_starts_ts, '%H:%M')
    pne = datetime.strptime(night_ends_ts, '%H:%M')
    night_starts = datetime.now().replace(hour=pns.hour, minute=pns.minute, second=0, microsecond=0)
    night_ends = datetime.now().replace(hour=pne.hour, minute=pne.minute, second=0, microsecond=0)
    # If it's later than night start timestamp.
    if night_starts <= now:
        # If night starts before midnight, it should end the next day.
        if night_starts > night_ends:
            night_ends = night_ends.replace(day=night_ends.day+1)
        # If the night not ended yet, say yes.
        if night_ends >= now:
            return True
    # Otherwise check if it's earlier than night end timestamp and exit if it is true.
    elif night_ends >= now:
        return True
    return False
