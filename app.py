import sqlite3
from flask import Flask, flash, redirect, render_template, request, url_for
from werkzeug.exceptions import abort
import jinja2

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_games(filter_cat, filter, order='title'):
    """
    retrieve the list of games from the database based on specified filters
    
    :param filter_cat: column to filter by in SELECT statement
    :param filter: value to filter by in SELECT statement
    :param order: column to sort the results by
    :return: list of games
    """
    
    conn = get_db_connection()
    if filter == 'All':
        games = conn.execute('SELECT * FROM games ORDER BY title').fetchall()
    else:
        games = conn.execute('SELECT * FROM games WHERE %s=? ORDER BY %s'
                             % (filter_cat, order),(filter,)).fetchall()
    conn.close()

    return games

def get_game_detail(game_id):
    """
    retrieve the information for a single game from the database
    
    :param game_id: id for game to be retrieved
    :return: information for the game
    """
    
    conn = get_db_connection()
    game = conn.execute('SELECT * FROM games WHERE id = ?',(game_id,))
    conn.close()

    if game is None:
        abort(404)

    return game

def get_counts (count_cat):
    """
    retrieve a count of all titles for the specified category

    :param count_cat: the column to aggregate count by in SELECT statement
    :return: information for the count values for the category.
    """
    conn = get_db_connection()
    counts = conn.execute('SELECT %s, COUNT(title) AS total FROM games GROUP BY %s ORDER BY %s'
                         % (count_cat, count_cat, count_cat)).fetchall()
    conn.close()

    return counts

def backlog_time(game_id = None, stat_cat = None):
    """
    calculates the time a game has been in backlog or the average time games of
    a specified category have been in backlog for all games and only current
    backlog. time is calculated by the difference between the date added and
    either the last update, date beaten, or date completed, based on the values
    in the beaten and completed columns.
    :param game: game_id for calculating a single game's backlog time
    :param stat_cat: aggregate category to use for calculating all games'
                     backlog times
    :return: time in backlog, avg time in backlog for all games, avg time in
             backlog for unplayed and unfinished games.
    """


    


app = Flask(__name__)
app.config.from_object('config')
app.config['SECRET_KEY']

@app.route('/')
def index():
    playing = get_games('playing', True, 'last_modified')
    statuses = get_counts('status')
    platforms = get_counts('platform')

    all_games = 0
    for status in statuses:
        all_games += status['total']

    return render_template('index.html', playing=playing, statuses=statuses,
                           platforms=platforms, all_games=all_games)

@app.route('/<string:filter_cat>/<string:filter>')
def games(filter_cat, filter):
    game_list = get_games(filter_cat, filter)

    return render_template('games.html', filter_cat=filter_cat, filter=filter,
                           game_list=game_list)

@app.route('/<int:game_id>')
def game_detail(game_id):
    game = get_game_detail(game_id)








if __name__ == "__main__":
    app.run(debug=True)



