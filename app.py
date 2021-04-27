import sqlite3
from flask import Flask, flash, redirect, render_template, request, url_for
from werkzeug.exceptions import abort
import jinja2

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_games(filter_type, filter, order='title'):
    conn = get_db_connection()
    if filter == 'All':
        games = conn.execute('SELECT * FROM games ORDER BY title').fetchall()
    else:
        games = conn.execute('SELECT * FROM games WHERE %s=? ORDER BY %s;'
                             % (filter_type, order),(filter,)).fetchall()
    conn.close()

    return games

def get_counts (count_var):
    conn = get_db_connection()
    counts = conn.execute('SELECT %s, COUNT(title) AS total FROM games GROUP BY %s ORDER BY %s;'
                         % (count_var, count_var, count_var)).fetchall()
    conn.close()

    return counts


app = Flask(__name__)
app.config.from_object('config')
app.config['SECRET_KEY']

@app.route('/')
def index():
    playing = get_games('playing', 'TRUE', 'last_modified')
    statuses = get_counts('status')
    platforms = get_counts('platform')

    all_games = 0
    for status in statuses:
        all_games += status['total']

    return render_template('index.html', playing=playing, statuses=statuses,
                           platforms=platforms, all_games=all_games)

@app.route('/<string:filter_type>/<string:filter>-games')
def games(filter_type, filter):
    game_list = get_games(filter_type, filter)

    return render_template('games.html', filter_type=filter_type, filter=filter,
                           game_list=game_list)








if __name__ == "__main__":
    app.run(debug=True)



