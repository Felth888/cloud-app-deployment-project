import sqlite3
from flask import Flask, flash, redirect, render_template, url_for, request
from werkzeug.exceptions import abort
from werkzeug.datastructures import MultiDict
from forms import NewGame, UpdateGame
from datetime import datetime, date
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
    sql = "SELECT * FROM games"
    if filter != 'All':
        sql = f"{sql} WHERE %s = ?"
    sql = f"{sql} ORDER BY %s"
    if filter == 'All':
        games = conn.execute(sql % (order)).fetchall()
    else:
        games = conn.execute(sql % (filter_cat, order),(filter,)).fetchall()
    conn.close()

    return games

def get_game_detail(game_id):
    """
    retrieve the information for a single game from the database
    
    :param game_id: id for game to be retrieved
    :return: information for the game
    """
    
    conn = get_db_connection()
    game = conn.execute("SELECT * "
                        "FROM games "
                        "WHERE id = ?",(game_id,)).fetchone()
    conn.close()

    if game is None:
        abort(404)

    return game

def add_game(form):
    params = []
    for field in form:
        if field.data is not None:
            params.append(field.data)
    params.pop()
    params.pop()
    sql = "INSERT INTO games (title, platform, genre, progress, status," \
                    " playing, added"
    if form.beaten.data is not None:
        sql = f"{sql}, beaten"
    if form.completed.data is not None:
        sql = f"{sql}, completed"

    sql = f"{sql}) VALUES (?, ?, ?, ?, ?, " \
        f"?, ?"
    if form.beaten.data is not None:
        sql = f"{sql}, ?"
    if form.completed.data is not None:
        sql = f"{sql}, ?"
    sql = f"{sql})"

    conn = get_db_connection()
    conn.execute(sql,params)
    conn.commit()
    conn.close()

def update_game(form, game_id):
    params = [date.today()]
    for field in form:
        if field.data is not None:
            params.append(field.data)
    params.pop()
    params.pop()
    params.append(game_id)

    sql = "UPDATE games SET updated = ?, progress = ?, status = ?, playing = ?"
    if form.beaten.data is not None:
        sql = f"{sql}, beaten = ?"
    if form.completed.data is not None:
        sql = f"{sql}, completed = ?"
    sql = f"{sql} WHERE id = ?"

    conn = get_db_connection()
    conn.execute(sql,params)
    conn.commit()
    conn.close()

def get_counts (count_cat, count_subcat = None):
    """
    retrieve a count of all titles for the specified category

    :param count_cat: the column to aggregate count by in SELECT statement
    :param count_subcat: the column to sub-aggregate count by in SELECT statement
    :return: information for the count values for the category.
    """
    conn = get_db_connection()
    sql = "SELECT %s, COUNT(title) AS total " \
          "FROM games " \
          "GROUP BY %s"
    if count_subcat != None:
        sql = f"{sql}, %s"
    sql = f"{sql} ORDER BY %s"

    if count_subcat != None:
        counts = conn.execute(sql % (count_cat, count_cat, count_subcat, count_cat)).fetchall()
    else:
        counts = conn.execute(sql % (count_cat, count_cat, count_cat)).fetchall()

    return counts

def backlog_times(game_id = None, stat_cat = None):
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
    conn = get_db_connection()
    sql = "CASE " \
            "WHEN completed IS NOT NULL " \
                "THEN JULIANDAY(completed) - JULIANDAY(added) " \
            "WHEN beaten IS NOT NULL " \
                "THEN JULIANDAY(beaten) - JULIANDAY(added) " \
            "ELSE JULIANDAY('now') - JULIANDAY(added) " \
            "END "

    # single game average
    if game_id is not None:
        sql = f"SELECT {sql} AS backlog_time FROM games WHERE id=?"
        game_time = conn.execute(sql,(game_id,)).fetchone()

        conn.close()
        return game_time
    # multiple games averages
    else:
        sql = f"SELECT AVG({sql}) AS backlog_time FROM games"
        current_sql = f"{sql} WHERE status IN ('Unplayed', 'Unfinished')"

        avg_total_time = conn.execute(sql).fetchone()
        avg_current_time = conn.execute(current_sql).fetchone()

        conn.close()
        return avg_current_time, avg_total_time

app = Flask(__name__)
app.config.from_object('config')
app.config['SECRET_KEY']
app.config['SESSION_COOKIE_SECURE']

@app.route('/')
def index():
    playing = get_games('playing', True, 'updated')
    statuses = get_counts('status')
    platforms = get_counts('platform')
    current_backlog, total_backlog = backlog_times()

    all_games = 0
    for status in statuses:
        all_games += status['total']

    return render_template('index.html', playing=playing, statuses=statuses,
                           platforms=platforms, all_games=all_games,
                           current_backlog=current_backlog,
                           total_backlog=total_backlog)

@app.route('/<string:filter_cat>/<string:filter>')
def games(filter_cat, filter):
    conn = get_db_connection()
    game_list = get_games(filter_cat, filter)

    return render_template('games.html', filter_cat=filter_cat, filter=filter,
                           game_list=game_list)

@app.route('/<int:game_id>', methods=["GET","POST"])
def game_detail(game_id):
    game = get_game_detail(game_id)
    game_time = backlog_times(game_id)

    defaults = MultiDict([('progress',game['progress']), ('status', game['status']),
                          ('playing', game['playing']),('added', added)])
    if game['beaten'] is not None:
        defaults.add('beaten', game['beaten'])
    if game['completed'] is not None:
        defaults.add('completed', game['completed'])

    if request.method == "GET":
        form = UpdateGame(formdata=defaults)
    else:
        form = UpdateGame()

    if form.validate_on_submit():
        update_game(form, game_id)
        return redirect(url_for('game_detail', game_id=game_id, game=game,
                           game_time=game_time, form=form))

    return render_template('game-detail.html', game_id=game_id, game=game,
                           game_time=game_time, form=form)

@app.route('/new-game', methods=["GET", "POST"])
def new_game():
    form = NewGame()

    if form.validate_on_submit():
        add_game(form)
        return redirect(url_for('games', filter_cat='None', filter='All'))

    return render_template('new-game.html', form=form)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)



