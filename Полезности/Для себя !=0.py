if str(sell) != str(0.0) or str(sell) != str('0.0'):
    sql.execute(f'''INSERT INTO Stat (name, type, x1, x2, v1, buy, sell, date, time) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?) ''',
                (name, type, x1, x2, flavor, buy, sell, date, time))
    db.commit()
    await message.answer(f"Продано:\n{type} - {name}\nВкус: {flavor}\nПрибыль: {gain}р", reply_markup=show_menu)
else:
    await message.answer(f"Для себя:\n{type} - {name}\nВкус: {flavor}", reply_markup=show_menu)