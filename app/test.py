from datetime import datetime, date, timedelta

begin_date = datetime.fromtimestamp(float(1768359600))
end_date = datetime.fromtimestamp(float(1768608000))
begin_for_date = begin_date.date()
end_for_date = end_date.date()
begin_time = begin_date.time()
end_time = end_date.time()

delta = end_for_date - begin_for_date 
date_list = []
for i in range(delta.days + 1):
    day = begin_date + timedelta(days=i)
    if i == 0:
        date_list.append({
            "date": day.strftime("%Y-%m-%d"),
            "begin_time": begin_time.strftime("%H:%M:%S"),
            "end_time": "23:59:59",
            "begin_in_day_timestamp": int(begin_date.timestamp()),
            "end_in_day_timestamp": int(datetime.combine(begin_for_date, datetime.max.time()).timestamp())
        })
    elif i == delta.days:
        date_list.append({
            "date": day.strftime("%Y-%m-%d"),
            "begin_time": "00:00:00",
            "end_time": end_time.strftime("%H:%M:%S"),
            "begin_in_day_timestamp": int(datetime.combine(end_for_date, datetime.min.time()).timestamp()),
            "end_in_day_timestamp": int(end_date.timestamp())
        })
    else:
        date_list.append({
            "date": day.strftime("%Y-%m-%d"),
            "begin_time": "00:00:00",
            "end_time": "23:59:59",
            "begin_in_day_timestamp": int(datetime.combine(day.date(), datetime.min.time()).timestamp()),
            "end_in_day_timestamp": int(datetime.combine(day.date(), datetime.max.time()).timestamp())
        })
print(date_list)