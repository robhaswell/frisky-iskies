#!/usr/bin/env python
import json
import MySQLdb
import MySQLdb.cursors
import os
import sys
import urllib2

from collections import defaultdict, namedtuple
from itertools import cycle, islice
from xml.etree.cElementTree import fromstring

db = MySQLdb.connect("localhost", "root", db="frisky-iskies",
        cursorclass=MySQLdb.cursors.DictCursor)
c = db.cursor()

Station = namedtuple('Station', 'name prefix station_id region_id')

stations = [
    Station('Jita', 'jita', 60003760, 10000002),
    Station('Amarr', 'amarr', 60008494, 10000043),
]

def split_every(n, iterable):
    i = iter(iterable)
    piece = list(islice(i, n))
    while piece:
        yield piece
        piece = list(islice(i, n))

c.execute("select * from items")
itemsResults = c.fetchall()
total = len(itemsResults) / 100.0
done = 0
spinner = cycle("|/-\\")

def retryGet(url):
    for n in xrange(3):
        try:
            fp = urllib2.urlopen(url)
            return fp.read()
        except (urllib2.HTTPError, urllib2.URLError):
            continue
    raise Exception("Fetching %s failed" % (url,))

for items in split_every(100, ( row['id'] for row in itemsResults )):
    priceHistoryRow = defaultdict(lambda: {})
    for station in stations:
        volumes = defaultdict(lambda: [])
        buy5pcs = {}
        sell5pcs = {}

        url = ("http://api.eve-marketdata.com/api/item_history2.json?char_name=Agrakari+Saraki&"
         "region_ids=" + str(station.region_id) + "&days=7&type_ids=" + ",".join(map(str, items)))
        history = json.loads(retryGet(url))

        url = ("http://api.eve-marketdata.com/api/price_type_station_buy_5pct.xml?char_name=Agrakari+Saraki&"
         "station_id=" + str(station.station_id) + "&type_id=" + ",".join(map(str, items)))
        buy5pc = fromstring(retryGet(url))

        url = ("http://api.eve-marketdata.com/api/price_type_station_sell_5pct.xml?char_name=Agrakari+Saraki&"
         "station_id=" + str(station.station_id) + "&type_id=" + ",".join(map(str, items)))
        sell5pc = fromstring(retryGet(url))

# {u'emd': {u'columns': u'typeID,regionID,date,lowPrice,highPrice,avgPrice,volume,orders',
#           u'currentTime': u'2013-09-07T13:25:29Z',
#           u'key': u'typeID,regionID,date',
#           u'name': u'history',
#           u'result': [{u'row': {u'avgPrice': u'52.27',
#                                 u'date': u'2013-09-01',
#                                 u'highPrice': u'52.9',
#                                 u'lowPrice': u'50',
#                                 u'orders': u'669',
#                                 u'regionID': u'10000002',
#                                 u'typeID': u'209',
#                                 u'volume': u'11473267'}},
#                       {u'row': {u'avgPrice': u'8.55',
        for row in ( result['row'] for result in history['emd']['result'] ):
            volumes[row['typeID']].append(int(row['volume']))

        for val in buy5pc.findall('./val'):
            buy5pcs[val.get('type_id')] = val.text.strip()

        for val in sell5pc.findall('./val'):
            sell5pcs[val.get('type_id')] = val.text.strip()

        for type_id, allVolumes in volumes.iteritems():
            volume = int(float(sum(allVolumes)) / len(allVolumes))
            buy5pcValue = buy5pcs.get(type_id)
            sell5pcValue = sell5pcs.get(type_id)
            if not buy5pcValue or not sell5pcValue:
                continue
            c.execute("update items set volume=%(volume)s, buy_med=%(buy)s, sell_med=%(sell)s "
                "where id=%(id)s", dict(volume=volume, id=type_id,
                    buy=buy5pcValue, sell=sell5pcValue))

            # now the values for today
            buy = buy5pcs.get(type_id)
            sell = sell5pcs.get(type_id)
            volume = allVolumes[-1]
            priceHistoryRow[type_id][station.prefix + "_buy"] = buy
            priceHistoryRow[type_id][station.prefix + "_sell"] = sell
            priceHistoryRow[type_id][station.prefix + "_volume"] = volume

    for item_id, row in priceHistoryRow.iteritems():
        c.execute("insert into price_history (item_id, " + ", ".join(row.keys()) + ") "
            "values (%s, " + ", ".join(["%s"] * len(row)) + ")",
            [item_id] + row.values())

    done += 1
    if os.isatty(0):
        sys.stdout.write("%s %.2f%%\r" % (spinner.next(), done / total * 100))
        sys.stdout.flush()

c.execute("update items set spread=sell_med-buy_med, profit=spread*volume")
