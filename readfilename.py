import re
from datetime import datetime

def extract_date_time_from_filename(filename):
    match = re.search(r'(\d{2})-(\d{2})-(\d{4})-(\d{4})', filename)
    if match:
        day_str = match.group(1)
        month_str = match.group(2)
        year_str = match.group(3)
        time_str = match.group(4)
        date_time_str = day_str + month_str + year_str + time_str
        date_time_obj = datetime.strptime(date_time_str, '%d%m%Y%H%M')
        return date_time_obj
    else:
        return None

filename = "02-03-2024-0835.jpg"
date_time = extract_date_time_from_filename(filename)
if date_time:
    print(f"Date and time from filename: {date_time}")
else:
    print("No date and time found in filename.")