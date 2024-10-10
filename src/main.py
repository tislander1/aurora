
import re
import ssl
import pytz
import datetime
import pandas as pd
import urllib.request
import matplotlib.pyplot as plt
from tzlocal import get_localzone

def set_local_timezone(date_and_time_string):
    format1 = '%b %d, %Y at %H:%M'
    my_timestamp = datetime.datetime.strptime(date_and_time_string, format1)

    # create both timezone objects
    old_timezone = pytz.timezone("UTC")
    local_tz = get_localzone()
    timezone_name = str(local_tz)
    new_timezone = local_tz

    # two-step process
    localized_timestamp = old_timezone.localize(my_timestamp)
    new_timezone_timestamp = localized_timestamp.astimezone(new_timezone)
    updated_date_and_time_string = new_timezone_timestamp.strftime(format1)
    return updated_date_and_time_string, timezone_name

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

data = urllib.request.urlopen('http://services.swpc.noaa.gov/text/3-day-forecast.txt', context=ctx).readlines()
data = [str(item).removeprefix("b'").removesuffix("\\n'") for item in data if str(item).strip() != "b'\\n'"]

start = 0
for ix in range(len(data)):
    if 'NOAA Kp index' in data[ix]:
        start = ix + 1
        break
for ix in range(start, len(data)):
    if 'Rationale' in data[ix]:
        stop = ix
        break
data = data[start:stop]

data2 = []

for ix in range(len(data)):
    split_dataline = re.split(r" {2,}", data[ix].strip())
    split_dataline = [item.split('(')[0].strip() for item in split_dataline]
    data2.append(split_dataline)

data2[0] = ['Time (UT)'] + data2[0]
for ix in range(len(data2)):
    data2[ix][0] = data2[ix][0].split('-')[0].strip()

df = pd.DataFrame(data2[1:], columns=data2[0]).astype(float)
df_dict = df.set_index('Time (UT)').to_dict()
data3 = []
for date in df_dict:
    for time_ut in df_dict[date]:
        data3.append([date, time_ut, df_dict[date][time_ut]])
df2 = pd.DataFrame(data3, columns = ['Date', 'Start time (UT)', 'NOAA Kp index'])

year = datetime.datetime.now(datetime.timezone.utc).year

df2['datetime_UT'] = df2['Date'] + ', ' + str(year) + ' at ' +df2['Start time (UT)'].astype(int).astype(str) +':00'

df2['datetime_local'] = ''
for index, row in df2.iterrows():
    row['datetime_UT']
    df2.at[index, 'datetime_local'] = set_local_timezone(row['datetime_UT'])[0]
local_timezone = set_local_timezone(row['datetime_UT'])[1]

df2 = df2[['datetime_local', 'NOAA Kp index']]

plt.barh(df2['datetime_local'], df2['NOAA Kp index'])
plt.xlabel('NOAA Kp Index')
plt.title('Kp index plot for ' + local_timezone)
plt.show()

#print(my_timestamp_str +' UTC is converted into ' + updated_date +' in the ' + timezone_name +' time zone.')
x = 2
