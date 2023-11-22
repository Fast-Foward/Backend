import pymysql

conn = pymysql.connect(host='localhost', user='yeseong', password='qwer1234', db='fastfoward')
cur = conn.cursor()
cur.execute("SELECT * FROM Sports")
rows = cur.fetchall()
for row in rows:
    print(row)
conn.commit()
conn.close()