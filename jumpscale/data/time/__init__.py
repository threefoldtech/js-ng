"""
Time helpers based on arrow

# TODO: add more explanation here.

```python
>>> j.data.time.get('2013-05-11T21:23:58.970460+07:00')
<Arrow [2013-05-11T21:23:58.970460+07:00]>

>>> utc = j.data.time.utcnow()
>>> utc
<Arrow [2013-05-11T21:23:58.970460+00:00]>

>>> utc = utc.shift(hours=-1)
>>> utc
<Arrow [2013-05-11T20:23:58.970460+00:00]>

>>> j.data.time.now()                                                                                         
<Arrow [2020-04-09T10:19:19.013636+02:00]>

>>> j.data.time.now().shift(hours=15)                                                                         
<Arrow [2020-04-10T01:19:23.225311+02:00]>


>>> local = utc.to('US/Pacific')
>>> local
<Arrow [2013-05-11T13:23:58.970460-07:00]>

>>> local.timestamp
1368303838

>>> local.format()
'2013-05-11 13:23:58 -07:00'

>>> local.format('YYYY-MM-DD HH:mm:ss ZZ')
'2013-05-11 13:23:58 -07:00'

>>> local.humanize()
'an hour ago'

>>> local.humanize(locale='ko_kr')
'1시간 전'


>>> j.data.time.utcnow()
<Arrow [2013-05-07T04:20:39.369271+00:00]>

>>> j.data.time.now()
<Arrow [2013-05-06T21:20:40.841085-07:00]>

>>> j.data.time.now('US/Pacific')
<Arrow [2013-05-06T21:20:44.761511-07:00]>

>>> j.data.time.get(1367900664)
<Arrow [2013-05-07T04:24:24+00:00]>

>>> j.data.time.get(1367900664.152325)
<Arrow [2013-05-07T04:24:24.152325+00:00]>

>>> j.data.time.get(datetime.utcnow())
<Arrow [2013-05-07T04:24:24.152325+00:00]>

>>> j.data.time.get(datetime(2013, 5, 5), 'US/Pacific')
<Arrow [2013-05-05T00:00:00-07:00]>

>>> from dateutil import tz
>>> j.data.time.get(datetime(2013, 5, 5), tz.gettz('US/Pacific'))
<Arrow [2013-05-05T00:00:00-07:00]>

>>> j.data.time.get(datetime.now(tz.gettz('US/Pacific')))
<Arrow [2013-05-06T21:24:49.552236-07:00]>

>>> j.data.time.get('2013-05-05 12:30:45', 'YYYY-MM-DD HH:mm:ss')
<Arrow [2013-05-05T12:30:45+00:00]>

>>> j.data.time.get('June was born in May 1980', 'MMMM YYYY')
<Arrow [1980-05-01T00:00:00+00:00]>


>>> arw = j.data.time.utcnow()
>>> arw
<Arrow [2013-05-12T03:29:35.334214+00:00]>

>>> arw.replace(hour=4, minute=40)
<Arrow [2013-05-12T04:40:35.334214+00:00]>

>>> arw.shift(weeks=+3)
<Arrow [2013-06-02T03:29:35.334214+00:00]>
```

"""

from arrow import *
