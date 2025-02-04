import sqlite3


def get_player(nick):
    with sqlite3.connect('Game.db') as db:
        cur = db.cursor()

        query = '''SELECT * FROM game WHERE nickname = (?)'''
        cur.execute(query, (nick,))

        res = cur.fetchall()
        if res:
            return [get_stat(nick, 'score'), get_stat(nick, 'money')]
        else:
            query = '''INSERT INTO game (score, money, nickname) VALUES (?, ?, ?)'''
            cur.execute(query, (0, 0, nick))

        db.commit()


def get_stat(nick, stat):
    with sqlite3.connect('Game.db') as db:
        cur = db.cursor()

        query = f'''SELECT {stat} FROM game WHERE nickname = (?)'''
        cur.execute(query, (nick,))

        res = cur.fetchone()

        db.commit()
        return res[0]


def update_player(nick, s, m, skin):
    with sqlite3.connect('Game.db') as db:
        cur = db.cursor()

        score = get_stat(nick, 'score')
        if score < s:
            score = s
        money = m
        if skin is not None:
            skins = get_stat(nick, 'skins')
            if skins is not None:
                skins = skins + f'{skin} '
            else:
                skins = f'{skin} '
            query = f'''UPDATE game SET score = ?, money = ?, skins = ? WHERE nickname = ?'''

            cur.execute(query, (score, money, skins, nick))
        else:
            query = f'''UPDATE game SET score = ?, money = ? WHERE nickname = ?'''

            cur.execute(query, (score, money, nick))
        db.commit()
        return


def get_top_10():
    with sqlite3.connect('Game.db') as db:
        cur = db.cursor()

        query = '''SELECT nickname, score FROM game'''

        cur.execute(query)

        res = sorted(cur.fetchall(), key=lambda x: x[1], reverse=True)

        return res[:10]


def get_player_place(nick):
    with sqlite3.connect('Game.db') as db:
        cur = db.cursor()

        query = '''SELECT nickname, score FROM game'''

        cur.execute(query)

        res = sorted(cur.fetchall(), key=lambda x: x[1], reverse=True)
        player_place = 1
        for n, s in res:
            if n == nick:
                return player_place
            else:
                player_place += 1
