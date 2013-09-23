#!/usr/bin/env python
import csv
import MySQLdb
import os
import re
import sys

from datetime import datetime, timedelta
from twisted.python.filepath import FilePath

date = datetime.now() - timedelta(days=1)
datestr = date.strftime("%Y-%m-%d")

os.system("wget -c http://eve-central.com/dumps/%s.dump.gz" % (datestr,))
os.system("gunzip %s.dump.gz" % (datestr,))

transactionsFilePath = FilePath("%s.dump" % (datestr,))
#transactionsFilePath = FilePath("transactions.csv")
size = float(transactionsFilePath.getsize())
fp = transactionsFilePath.open("r")

db = MySQLdb.connect("localhost", "root", db="frisky-iskies")
c = db.cursor()

c.execute("truncate table transactions")
c.execute("alter table transactions disable keys")

durationRe = re.compile(r"\D.*")

with open("transactions.csv") as csvfile:
    csvreader = csv.reader(csvfile)
    csvreader.next()
    i = 0
    for row in csvreader:
        i += 1
        if i % 1000 == 0:
            sys.stdout.write("%.2f%%\r" % (csvfile.tell() / size * 100))
            sys.stdout.flush()
        row[11] = durationRe.sub("", row[11])
        try:
            c.execute("insert into transactions values "
                "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                row)
        except:
            print row
            raise

print "Done, re-indexing"
c.execute("alter table transactions enable keys")
