#to subtract five days from current date
from datetime import date, timedelta
print(date.today() - timedelta(days=5))

#to print yesterday, today, tomorrow
from datetime import date, timedelta
t = date.today()
print(t - timedelta(days=1), t, t + timedelta(days=1))

#to drop microseconds from datetime
from datetime import datetime
print(datetime.now().replace(microsecond=0))

#to calculate two date difference in seconds
from datetime import datetime
d1 = datetime(2026, 2, 25, 22, 30)
d2 = datetime(2026, 2, 25, 22, 44)
print((d2 - d1).seconds)