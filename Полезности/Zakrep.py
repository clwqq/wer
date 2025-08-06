import sqlite3

db = sqlite3.connect('Jiji.db')
sql = db.cursor()

sql.execute('''SELECT DISTINCT x2 FROM JIJI WHERE ((v1 IS NOT NULL AND c1 > 0))''')
mg_values = sql.fetchall()

message = ''
for mg_value in mg_values:
    mg = mg_value[0]
    message += f'{mg}\n'
    name_set = set()
    sql.execute(f'''SELECT name FROM JIJI WHERE x2 = ? AND ((v1 IS NOT NULL AND c1 > 0))''', (mg,))
    names = sql.fetchall()
    for name in names:
        if name[0] not in name_set:
            message += f' - {name[0]}\n'
            name_set.add(name[0])
print(message)
        

