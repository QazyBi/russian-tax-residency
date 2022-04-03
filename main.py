# Налоговый резидент РФ это физическое лицо,
# которое находится на территории России
# не менее 183 календарных дней в течение 12 месяцев идущих подряд.
# Эти 12 месяцев могут принадлежать разным календарным годам:
# начинаться в одном и заканчиваться в следующем.


# пользователь вводит даты въездов и выездов

# например:
# - 14.03.22 out
# - 10.01.22 in
# - 10.08.21 in
# - 27.12.21 out
# - 13.06.21 out
# - 05.03.21 in

from typing import Dict, List
from datetime import datetime, timedelta


def parse_record(record: str, date_format) -> Dict:
    record = record.split(' ')

    date = datetime.strptime(record[0], date_format).date()
    rec_type = record[1]

    return {'type': rec_type,
            'date': date}


class Entry:
    def __init__(self, r_type, date):
        self.type = r_type
        self.date = date

    @staticmethod
    def from_string(record, date_format):
        parsed = parse_record(record, date_format)

        r_type, date = parsed['type'], parsed['date']
        return Entry(r_type, date)

    def __repr__(self):
        if self.type == 'in':
            return f'Entered Russia {self.date}'
        else:
            return f'Exited Russia {self.date}'


def are_entries_valid(entries: List[Entry]) -> bool:
    """

    :param entries: sorted list of entries
    :type entries:
    :return:
    :rtype:
    """
    last = None
    for e in entries:
        current = e.type
        # validate
        if last is not None and last == current:
            return False
        last = current
    return True


def is_tax_resident(entries: List[Entry]) -> bool:
    if not are_entries_valid(entries):
        raise ValueError("Error in the list of entries")
    return calc_days_in_country_for_last_year(entries) > 183


def sort_entries(entries: List[Entry]):
    return sorted(entries, key=lambda x: x.date)


def calc_days_in_country_for_last_year(entries: List[Entry]) -> int:
    today = datetime.now().date()
    last_year = today.replace(year=today.year - 1)

    # find index of the last entry which occurred right before the last year
    target = None
    for e in entries:
        if e.date < last_year:
            target = e

    entries = [e for e in entries if e.date > last_year]
    if target is not None and target.type == 'in':
        new_entry = Entry('in', target.date)
        entries.insert(0, new_entry)

    if entries[0].type == 'out':
        del entries[0]

    if entries[-1].type == 'in':
        new_entry = Entry('out', today)
        entries.append(new_entry)

    n = len(entries)
    assert n % 2 == 0

    ins = [e for e in entries if e.type == 'in']
    outs = [e for e in entries if e.type =='out']

    total_days_in = 0
    for in_entry, out_entry in zip(ins, outs):
        days_in = (out_entry.date - in_entry.date).days
        total_days_in += days_in

    return total_days_in


def when_tax_residency_expires(days_in):
    remaining_days = 183 - days_in
    today = datetime.now().date()
    expirdation_date = today + timedelta(days=remaining_days)
    return expirdation_date


if __name__ == "__main__":
    border_crossing_records = [
        '14.03.22 out,'
        '10.01.22 in',
        '10.08.21 in',
        '27.12.21 out',
        '13.06.21 out',
        '05.03.21 in',
        '17.12.20 out',
    ]

    date_format = '%d.%m.%y'

    entries = [Entry.from_string(r, date_format) for r in border_crossing_records]
    entries = sort_entries(entries)

    for i, e in enumerate(entries, start=1):
        print(f"{i}. {e}")

    today = datetime.now().date()
    if is_tax_resident(entries):
        print(f"For {today} you're a tax resident of Russia")
        days_in = calc_days_in_country_for_last_year(entries)
        print(f"You tax residency expires: {when_tax_residency_expires(days_in)}")
    else:
        print(f"For {today} you're NOT a tax resident of Russia")

    print(calc_days_in_country_for_last_year(entries))
