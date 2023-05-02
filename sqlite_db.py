import sqlite3 as sq

def sql_start():
  global base, cur
  base = sq.connect("bot.db")
  cur = base.cursor()

  if base:
    print("Data base connect OK!")

  base.execute('CREATE TABLE IF NOT EXISTS users2dicts(id INTEGER, word TEXT PRIMARY KEY, translation TEXT)')
  base.commit()

async def sql_add_command(user_id, state):
  async with state.proxy() as data:
    added = list(data.values())
    added.insert(0, user_id)
    print(added)
    cur.execute('INSERT INTO users2dicts VALUES (?, ?, ?)', tuple(added))
    base.commit()

async def sql_read(user_id):
  print(user_id)
  dict = cur.execute(f'SELECT * from users2dicts where id = {user_id}').fetchall()
  return dict

async def sql_delete(user_id, word2del):
  #check if exist
  exist = cur.execute(f'SELECT EXISTS(SELECT * FROM users2dicts WHERE id = {user_id} and word=\'{word2del}\')').fetchall()

  if not exist:
    return False
  
  cur.execute(f'DELETE from users2dicts where id = {user_id} and word = \'{word2del}\'')
  return True

