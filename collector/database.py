import sqlite3


def insert_into_db(db, table, data):
    connection = sqlite3.connect(db)

    with connection:
        cursor = connection.cursor()

        cursor.execute("delete from {0}".format(table))
        count = 0
        for row in data:
            sql = "insert into {0} ({1}) values({2});".format(table, ",".join(row), ",".join(map(lambda key: '"{0}"'.format(row[key]), row)))
            cursor.execute(sql)
            count += 1
        print "Inserted {0} rows into '{1}':'{2}'".format(count, db, table)