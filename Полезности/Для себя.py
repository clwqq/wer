# Для себя
sql.execute(f'''UPDATE JIJI SET c1=(?) WHERE name=(?) AND v1=(?) AND buy=(?) AND sell=(?) ''', (upd_count, name, flavor, buy, sell_db))
db.commit()
if str(sell) != str(0.0) or str(sell) != str('0.0'):
    sql.execute(f'''INSERT INTO Stat (name, type, x1, x2, v1, buy, sell, date, time) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?) ''',
                (name, type, x1, x2, flavor, buy, sell, date, time))
    db.commit()
    await message.answer(f"Продано:\n{type} - {name}\nВкус: {flavor}\nПрибыль: {gain}р", reply_markup=show_menu)
else:
    await message.answer(f"Для себя:\n{type} - {name}\nВкус: {flavor}", reply_markup=show_menu)
if upd_count == 0:
    await message.answer(f"{name} со вкусом {flavor}, ценой {buy}₽ закончился!")

#-------------------------------------------------------------------------------------------------------------------------------------------
sql.execute(f'''UPDATE JIJI SET c1=(?) WHERE name=(?) AND v1=(?) AND buy=(?) AND sell=(?) ''', (upd_count, name, flavor, buy, sell_db))
db.commit()
sql.execute(f'''INSERT INTO Stat (name, type, x1, x2, v1, buy, sell, date, time) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?) ''',
                (name, type, x1, x2, flavor, buy, sell, date, time))
db.commit()
await message.answer(f"Продано:\n{type} - {name}\nВкус: {flavor}\nПрибыль: {gain}р", reply_markup=show_menu)

if upd_count == 0:
    await message.answer(f"{name} со вкусом {flavor}, ценой {buy}₽ закончился!")


@dp.message(lambda message: re.match(r'^\d+(\.\d+)?$', message.text))
async def delete_price(message):
    if message.from_user.id not in admins:
        return await message.answer('Ты не мой братик!', reply_markup = show_menu)
    global del_type, del_name, del_flavor, del_price, del_flavor_list, status, name
    if del_price == False: return
    del_name = True
    del_price = False
    status = True

    sell = float(message.text)

    sql.execute('''SELECT name FROM WORK ''')
    name = str(sql.fetchall()[0][0])
   
    sql.execute('''SELECT type FROM WORK ''')
    type = str(sql.fetchall()[0][0])

    sql.execute('''SELECT x1 FROM WORK ''')
    x1 = str(sql.fetchall()[0][0])

    sql.execute('''SELECT x2 FROM WORK ''')
    x2 = str(sql.fetchall()[0][0])

    sql.execute('''SELECT v1 FROM WORK ''')
    flavor = str(sql.fetchall()[0][0])

    sql.execute('''SELECT c1 FROM WORK ''')
    c1 = int(sql.fetchall()[0][0])

    sql.execute('''SELECT buy FROM WORK ''')
    buy = float(sql.fetchall()[0][0])
    buy = int(buy) if buy.is_integer() else round(buy, 2)

    sql.execute('''SELECT sell_db FROM WORK ''')
    sell_db = float(sql.fetchall()[0][0])
    sell_db = int(sell_db) if sell_db.is_integer() else round(sell_db, 2)

    gain = sell - buy
    gain = int(gain) if gain.is_integer() else round(gain, 2)

    sell = str(sell)
    buy = str(buy)
    gain = str(gain)

    upd_count = c1 - 1
    
    date = datetime.now().strftime('%Y.%m.%d')
    time = datetime.now().strftime('%H:%M')

    sql.execute(f'''UPDATE JIJI SET c1=(?) WHERE name=(?) AND v1=(?) AND buy=(?) AND sell=(?) ''', (upd_count, name, flavor, buy, sell_db))
    db.commit()
    if str(sell) != str(0.0) or str(sell) != str('0.0'):
        sql.execute(f'''INSERT INTO Stat (name, type, x1, x2, v1, buy, sell, date, time) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?) ''',
                    (name, type, x1, x2, flavor, buy, sell, date, time))
        db.commit()
        await message.answer(f"Продано:\n{type} - {name}\nВкус: {flavor}\nПрибыль: {gain}р", reply_markup=show_menu)
    else:
        await message.answer(f"Для себя:\n{type} - {name}\nВкус: {flavor}", reply_markup=show_menu)
    if upd_count == 0:
        await message.answer(f"{name} со вкусом {flavor}, ценой {buy}₽ закончился!")
    
    sql.execute('''SELECT mess_id FROM WORK ''')
    mess_id = sql.fetchone()[0]
    sql.execute(f'''SELECT name, type, x1, x2, v1, sell from JIJI WHERE mess_id=(?) AND c1 > 0 ''', 
            (mess_id,))
    if sql.fetchone() is None:
        try:
            await bot.delete_message(chat_id=channel, message_id=mess_id)
        except:
            await net_v_nalichii(mess_id)
        await zakrep_edit(message)
        await message.answer(f"{name}, ценой {buy}₽ закончился!")
        return await delete_mess(message)
    sql.execute(f'''SELECT name, type, x1, x2, v1, sell from JIJI WHERE mess_id=(?) AND c1 > 0 ''', 
            (mess_id,))
    result = sql.fetchall()
    products = {}
    for row in result:
        name = row[0]
        type = row[1]
        x1 = str(row[2])
        x2 = str(row[3])
        v1 = row[4]
        sell = str(row[5])

        product_key = f"{name} {type} {x1} {x2} {sell}"
    
        if product_key not in products:
            products[product_key] = {
                'name': [],
                'type': [],
                'x1': [],
                'x2': [],
                'v1': [],
                'sell': [],
            }

        if v1:
            products[product_key]['name'].append(name)
            products[product_key]['type'].append(type)
            products[product_key]['x1'].append(x1)
            products[product_key]['x2'].append(x2)
            products[product_key]['v1'].append(v1)
            products[product_key]['sell'].append(sell)
            
    x1x2 = ''
    flavors = ''
    for product_key, details in products.items():
        name_set = set()
        x1_set = set()
        x2_set = set()
        sell_set = set()
        flavors_set = set()
        for name in details['name']:
            if name[0] not in name_set:
                name_set.add(name[0])
        for x1 in details['x1']:
            if x1[0] not in x1_set:
                if x1 != '0':
                    x1x2 = (f'{x1}\n')
                    
        for x2 in details['x2']:
            if x2[0] not in x2_set:
                if x2 != '0':
                    x1x2 = (f'{x2}\n')
                    
        if x2 != '0' and x1 != '0':
            x1x2 = (f'{x1}, {x2}\n')
            x1, x2 = x1x2.split(', ')
        
        feature = 'Вкусы'
        for type in details['type']:
            if type in features:  
                feature = features[type]
    
        for vkus in details['v1']:
            if vkus not in flavors_set:
                flavors += f'{vkus}\n'
                flavors_set.add(vkus)
        flavors_list = flavors.split('\n')

        for sell in details['sell']:
            if sell[0] not in sell_set:
                sell_set.add(sell[0])
        mess_text = (f"{name}\n{x1x2}\n{feature}\n{flavors}\nЦена: {sell} рублей")
        try:
            await bot.edit_message_caption(chat_id=channel, message_id=mess_id, caption=mess_text)
        except:
            print("delete_price | await bot.edit_message_caption(chat_id=channel, message_id=mess_id, caption=mess_text)")
    await delete_mess(message)
    await delete_name(message)

    
    