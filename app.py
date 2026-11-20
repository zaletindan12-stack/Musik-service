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

@app.route('/track/<int:track_id>')
def track_page(track_id):
	cur = con.cursor()
	cur.execute(""" SELECT T.ID, T.TITLE, T.DURATION, T.AUDIO_URL, 
	A.NAME AS ARTIST_NAME, AL.TITLE AS ALBUM_TITLE, G.NAME AS GENRE_NAME
	FROM TRACKS T
	JOIN ARTISTS A ON T.ARTIST_ID = A.ID
	JOIN ALBUMS AL ON T.ALBUM_ID = AL.ID
	JOIN GENRES G ON T.GENRE_ID = G.ID
	WHERE T.ID = ?
	""", (track_id,))
	row = cur.fetchone()
	cur.close

	if row is None:
		return "Трек не найден", 404

	track = {
		'id': row[0],
		'title': row[1],
		'duration': row[2],
		'audio_url': row[3],
		'artist': row[4],
		'album': row[5],
		'genre': row[6]
	}

	return render_template('track.html', track=track)

if __name__ == '__main__':
	app.run(debug=True)
