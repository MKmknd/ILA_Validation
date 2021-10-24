import datetime
import sys

def make_gap_parameters(author_date, start_day, gap_days, end_gap_days=365, unit_days=30):

    END = max(author_date.values()) - datetime.timedelta(days=end_gap_days) # date (date - delta)

    start_gap_days = start_day - min(author_date.values()) # delta (date - date)

    experimental_days = END - (min(author_date.values())+ start_gap_days) # delta (date - (date + delta))
    first_training_days = experimental_days / 2 # delta
    first_training_gap_days = first_training_days + gap_days # delta (delta + delta)
    least_days = experimental_days - first_training_gap_days # delta (delta - delta)

    training_period = (least_days/unit_days).days

    return start_gap_days.days, end_gap_days, gap_days.days, unit_days, training_period

