from flask import Flask, render_template
import fdb

app = Flask(__name__)

con = fdb.connect(
	dsn='localhost/3050:/rdb/musik.fdb',
	user='sysdba',
	password='masterkey',
	charset='UTF8',
	fb_library_name='/opt/RedDatabase/lib/libfbclient.so'
)

@app.route('/')
def index():
	return render_template('index.html', username='Ганджубасик')

@app.route('/tracks')
def tracks():
	cur = con.cursor()
	cur.execute("SELECT ID, TITLE, DURATION FROM TRACKS ORDER BY ID")
	rows = cur.fetchall()
	cur.close()

	print("DEBUG: rows =", rows)

	tracks_list = []
	for row in rows:
		tracks_list.append({
			'id': row[0],
			'title': row[1],
			'duration': row[2]
		})

	print("DEBUG: tracks_list =", tracks_list)

	return render_template('tracks.html', tracks=tracks_list)

if __name__ == '__main__':
	app.run(debug=True)
