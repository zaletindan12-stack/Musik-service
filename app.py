from flask import Flask, render_template, redirect, request, url_for, session, flash
import fdb
import hashlib

app = Flask(__name__)
app.secret_key = 'musik-secret-key-2026'
def hash_password(password):
	return hashlib.sha256(password.encode()).hexdigest()

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

@app.route('/register', methods=['GET', 'POST'])
def register():
	if request.method == 'POST':
		login = request.form['login']
		email = request.form['email']
		password = request.form['password']

		cur = con.cursor()
		cur.execute("SELECT ID FROM USERS WHERE LOGIN = ?", (login,))
		
		if cur.fetchone() is not None:
			cur.close()
			flash('Этот логин уже занят')
			return redirect(url_for('register'))
		
		password_hash = hash_password(password)

		cur.execute("INSERT INTO USERS (LOGIN, PASSWORD_HASH, EMAIL, ROLE) " \
		"VALUES (?, ?, ?, 'user')", (login, password_hash, email))
		con.commit()
		cur.close()

		flash('Регистрация удалась! Теперь - войдите')
		return redirect(url_for('login'))

	return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		login_value = request.form['login']
		password = request.form['password']

		cur = con.cursor()
		cur.execute("SELECT ID, LOGIN, PASSWORD_HASH, ROLE " \
		"FROM USERS WHERE LOGIN = ?", (login_value,))
		user = cur.fetchone()
		cur.close()

		if user is None:
			flash('Неверный логин или пароль')
			return redirect(url_for('login'))

		user_id, user_login, password_hash, role = user

		if hash_password(password) != password_hash:
			flash('Неверный логин или пароль')
			return redirect(url_for('login'))

		session['user_id'] = user_id
		session['login'] = user_login
		session['role'] = role

		flash(f'Добро пожаловать, {user_login}!')
		return redirect(url_for('index'))

	return render_template('login.html')

@app.route('/logout')
def logout():
	session.clear()
	flash('Вы вышли из системы')
	return redirect(url_for('index'))

if __name__ == '__main__':
	app.run(debug=True)
