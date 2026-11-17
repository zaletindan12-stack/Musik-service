import fdb

con = fdb.connect(
	dsn='localhost:3050/rdb/musik.fdb',
	user='sysdba',
	password='masterkey',
	charset='UTF8',
	fb_library_name='/opt/RedDatabase/lib/libfbclient.so'
)

print("Подключение успешно!")

cur=con.cursor()
cur.execute("SELECT ID, TITLE, DURATION FROM TRACKS ORDER BY ID")

print("\nСписок треков:")
rows = cur.fetchall()
tracks = [{'id': row[0], 'title': row[1], 'duration': row[2]} for row in rows]
	return row

cur.close()
con.close()
print("\nСоединение закрыто.")
