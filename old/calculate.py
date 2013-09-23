#!/usr/bin/env python
import MySQLdb
import MySQLdb.cursors
import sys

from itertools import cycle

db = MySQLdb.connect("localhost", "root", db="frisky-iskies",
        cursorclass=MySQLdb.cursors.DictCursor)
c = db.cursor()

JITA=60003760

c.execute("select * from items order by volume desc")
itemsResults = c.fetchall()
total = float(len(itemsResults))
done = 0
spinner = cycle("|/-\\")
for row in itemsResults:
    c.execute("""
        SELECT t1.price as value FROM (
        SELECT @rownum:=@rownum+d.volenter as `row_number`, d.price
          FROM transactions d,  (SELECT @rownum:=0) r
          WHERE
          station_id=%(jita)s and buy=1 and type_id=%(id)s
          ORDER BY d.price
        ) as t1, 
        (
          SELECT sum(volenter) as total_rows
          FROM transactions d
          WHERE
          station_id=%(jita)s and buy=1 and type_id=%(id)s
        ) as t2
        WHERE 1
        AND t1.row_number >= floor(total_rows * 0.95)
    """, dict(jita=JITA, id=row['id']))
    buy = c.fetchone()
    print buy
    sys.exit()
    if not buy:
        c.execute("update items set buy_med=null, sell_med=null where id=%(id)s", dict(
            id=row['id']))
        continue

    c.execute("""
        SELECT t1.price as value FROM (
        SELECT @rownum:=@rownum+1 as `row_number`, d.price
          FROM transactions d,  (SELECT @rownum:=0) r
          WHERE
          station_id=%(jita)s and buy=0 and type_id=%(id)s
          ORDER BY d.price
        ) as t1, 
        (
          SELECT count(*) as total_rows
          FROM transactions d
          WHERE
          station_id=%(jita)s and buy=0 and type_id=%(id)s
        ) as t2
        WHERE 1
        AND t1.row_number=floor(total_rows * 0.05)+1;
    """, dict(jita=JITA, id=row['id']))
    sell = c.fetchone()
    if not sell:
        c.execute("update items set buy_med=null, sell_med=null where id=%(id)s", dict(
            id=row['id']))
        continue

    c.execute("update items set buy_med=%(buy)s, sell_med=%(sell)s where id=%(id)s", dict(
        buy=buy['value'], sell=sell['value'], id=row['id']))
    done += 1

    sys.stdout.write("%s %.2f%%\r" % (spinner.next(), done / total * 100))
    sys.stdout.flush()

c.execute("update items set spread=sell_med-buy_med")
