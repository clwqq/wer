add_status = False

add_name = False
add_type = False
add_x1 = False
add_x2 = False
add_v1 = False
add_c1 = False
add_buy = False
add_sell = False

add_name2 = []
add_type2 = []
add_x12 = []
add_x22 = []
add_v12 = []
add_c12 = []
add_buy2 = []
add_sell2 = []

@dp.callback_query(lambda query: query.data == "add")
async def add_one(query):
    global add_status
    await query.message.edit_text('Формат:\n1) Раздел\n2) Название\n3) Вкус\n4) Характеристика 1\n5) Характеристика 2\n6) Цена покупки\n7) Цена продажи\n8) Количество товара', reply_markup=show_in_menu_button)
    add_status = True

async def add_one_m(message):
    global add_status
    await message.answer('Формат:\n1) Раздел\n2) Название\n3) Вкус\n4) Характеристика 1\n5) Характеристика 2\n6) Цена покупки\n7) Цена продажи\n8) Количество товара', reply_markup=show_in_menu_button)
    add_status = True

@dp.message(lambda message: add_status)
async def add_one_message(message):
    global add_status
    if add_status == False:
        return
    lines = message.text.splitlines()
    type, name, v1, x1, x2, buy, sell, count = map(str.strip, lines)
    count = int(count)

    sql.execute(f'''SELECT name from JIJI WHERE name=(?) AND type=(?) AND v1=(?) AND x1=(?) AND x2=(?) AND buy=(?) AND sell=(?) ''', 
                (name, type, v1, x1, x2, buy, sell))
    text1 = 'Товар добавлен в таблицу'
    text2 = 'Такой товар уже имеется, количество обновлено'
    if sql.fetchone() is None:
        sql.execute(f'''INSERT INTO JIJI (name, type, v1, x1, x2, c1, buy, sell) VALUES (?, ?, ?, ?, ?, ?, ?, ?) ''',
                    (name, type, v1, x1, x2, count, buy, sell))
        db.commit()

        sql.execute(f'''SELECT mess_id from JIJI WHERE name=(?) AND type=(?) AND x1=(?) AND x2=(?) AND sell=(?) ''', 
                (name, type, x1, x2, sell))
        message_id = sql.fetchone()[0]
        await message.answer(text1, reply_markup=show_menu)
        if sql.fetchone() is None:
            await send_new_post(name, type, x1, x2, v1, buy, sell, message_id)
            await zakrep_edit(message)
        else:
            await edit_post(name, type, x1, x2, v1, buy, sell, message_id)
    else:
        sql.execute('''SELECT c1 FROM JIJI WHERE name=(?) AND type=(?) AND x1=(?) AND x2=(?) AND v1=(?) AND buy=(?) AND sell=(?) ''', 
                (name, type, x1, x2, v1, buy, sell))
        c1 = int(sql.fetchone()[0])
        upd_count = c1 + count
        sql.execute(f'''UPDATE JIJI SET c1=(?) WHERE name=(?) AND type=(?) AND x1=(?) AND x2=(?) AND v1=(?) AND buy=(?) AND sell=(?) AND ((v1 IS NOT NULL AND c1 > 0))''', 
                    (upd_count, name, type, x1, x2, v1, buy, sell))
        db.commit()
        await message.answer(text2, reply_markup=show_menu)
    add_status = False
    await add_one_m(message)

async def send_new_post(name, type, x1, x2, v1, buy, sell, message_id):
    sql.execute(f'''SELECT name, type, x1, x2, v1, sell, mess_id from JIJI WHERE name=(?) AND type=(?) AND x1=(?) AND x2=(?) AND sell=(?) AND ((v1 IS NOT NULL AND c1 > 0))''', 
                (name, type, x1, x2, sell))
    result = sql.fetchall()

    products = {}
    for row in result:
        name = row[0]
        type = row[1]
        x1 = str(row[2])
        x2 = str(row[3])
        v1 = row[4]
        sell = str(row[5])
        message_id = str(row[6])

        product_key = f"{name} {type} {x1} {x2} {sell}"
    
        if product_key not in products:
            products[product_key] = {
                'name': [],
                'type': [],
                'x1': [],
                'x2': [],
                'v1': [],
                'sell': [],
                'mess_id': [],
            }

        if v1:
            products[product_key]['name'].append(name)
            products[product_key]['type'].append(type)
            products[product_key]['x1'].append(x1)
            products[product_key]['x2'].append(x2)
            products[product_key]['v1'].append(v1)
            products[product_key]['sell'].append(sell)
            products[product_key]['mess_id'].append(message_id)

    x1x2 = ''
    flavors = ''
    for product_key, details in products.items():
        name_set = set()
        x1_set = set()
        x2_set = set()
        sell_set = set()
        x1x2_set = set()
        flavors_set = set()
        message_id_set = set()

        for name in details['name']:
            if name[0] not in name_set:
                name_set.add(name[0])
        for x1 in details['x1']:
            if x1[0] not in x1_set:
                if x1 != '0':
                    x1_set.add(x1[0])
                    x1x2 = (f'{x1}\n')
                    
        for x2 in details['x2']:
            if x2[0] not in x2_set:
                if x2 != '0':
                    x2_set.add(x2[0])
                    x1x2 = (f'{x2}\n')
                    
        if x1 != '0' and x2 != '0':
            if x1x2[0] not in x1x2_set:
                x1x2 = (f'{x1}, {x2}\n')
                x1x2_set.add(x1x2[0])
                x1, x2 = x1x2.split(', ')
                x1_set.add(x1[0])
                x2_set.add(x2[0])
                
        for type in details['type']:
            feature = 'Вкусы:'
            if type == 'Расходник':
                feature = 'Сопротивление:'

        for vkus in details['v1']:
            flavors += f'{vkus}\n'
            flavors_set.add(vkus)
        flavors_list = flavors.split('\n')

        for sell in details['sell']:
            if sell[0] not in sell_set:
                sell_set.add(sell[0])

        for message_id in details['mess_id']:
            if message_id[0] not in message_id_set:
                message_id_set.add(message_id[0])
                
    text = (f"{name}\n{x1x2}\n{feature}\n{flavors}\nЦена: {sell} рублей")
    try:
        pic = f'pic/{name}.jpg'
        sent_message = await bot.send_photo(channel, FSInputFile(pic), caption=text, disable_notification=True)
        message_id = sent_message.message_id
        for flavor in flavors_list:
            sql.execute('''UPDATE JIJI SET mess_id = ? WHERE name = ? AND type = ? AND v1 = ? AND buy = ? AND sell = ? AND ((v1 IS NOT NULL AND c1 > 0)) ''', # AND x1 = ? AND x2 = ?
                    (message_id, name, type, flavor, buy, sell)) # x1, x2,
            db.commit()
    except:
        pic = 'pic/pic.jpg'
        sent_message = await bot.send_photo(channel, FSInputFile(pic), caption=text, disable_notification=True)
        message_id = sent_message.message_id
        for flavor in flavors_list:
            sql.execute('''UPDATE JIJI SET mess_id = ? WHERE name = ? AND type = ? AND v1 = ? AND buy = ? AND sell = ? AND ((v1 IS NOT NULL AND c1 > 0)) ''',
                    (message_id, name, type, flavor, buy, sell))
            db.commit()

async def edit_post(name, type, x1, x2, v1, buy, sell, message_id):
    try:
        sql.execute(f'''SELECT mess_id from JIJI WHERE name=(?) AND type=(?) AND x1=(?) AND x2=(?) AND sell=(?) ''', 
                    (name, type, x1, x2, sell))
        message_id = sql.fetchone()[0]
        sql.execute(f'''SELECT name, type, x1, x2, v1, sell from JIJI WHERE name=(?) AND type=(?) AND x1=(?) AND x2=(?) AND sell=(?) AND ((v1 IS NOT NULL AND c1 > 0)) ''', 
                (name, type, x1, x2, sell))
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
            x1x2_set = set()
            flavors_set = set()
            for name in details['name']:
                if name[0] not in name_set:
                    name_set.add(name[0])
            for x1 in details['x1']:
                if x1[0] not in x1_set:
                    if x1 != '0':
                        x1_set.add(x1[0])
                        x1x2 = (f'{x1}\n')
                        
            for x2 in details['x2']:
                if x2[0] not in x2_set:
                    if x2 != '0':
                        x2_set.add(x2[0])
                        x1x2 = (f'{x2}\n')
                        
            if x1 != '0' and x2 != '0':
                if x1x2[0] not in x1x2_set:
                    x1x2 = (f'{x1}, {x2}\n')
                    x1x2_set.add(x1x2[0])
                    x1, x2 = x1x2.split(', ')
                    x1_set.add(x1[0])
                    x2_set.add(x2[0])
                    
            for type in details['type']:
                feature = 'Вкусы:'
                if type == 'Расходник':
                    feature = 'Сопротивление:'

            for vkus in details['v1']:
                if vkus not in flavors_set:
                    flavors += f'{vkus}\n'
                    flavors_set.add(vkus)
            flavors_list = flavors.split('\n')

            for sell in details['sell']:
                if sell[0] not in sell_set:
                    sell_set.add(sell[0])
                    
            text = (f"{name}\n{x1x2}\n{feature}\n{flavors}\nЦена: {sell} рублей")
            await bot.edit_message_caption(chat_id=channel, message_id=message_id, caption=text)
            for flavor in flavors_list:
                sql.execute('''UPDATE JIJI SET mess_id = ? WHERE name = ? AND type = ? AND v1 = ? AND buy = ? AND sell = ? AND ((v1 IS NOT NULL AND c1 > 0))''', # AND x1 = ? AND x2 = ?
                        (message_id, name, type, flavor, buy, sell)) # x1, x2,
                db.commit()
    except:
        for flavor in flavors_list:
            sql.execute('''UPDATE JIJI SET mess_id = ? WHERE name = ? AND type = ? AND v1 = ? AND buy = ? AND sell = ? AND ((v1 IS NOT NULL AND c1 > 0))''', # AND x1 = ? AND x2 = ?
                    (message_id, name, type, flavor, buy, sell)) # x1, x2,
            db.commit()

@dp.callback_query(lambda query: query.data == "varios")
async def add_varios(message):
    global add_name, add_type, add_x1, add_x2, add_v1, add_c1, add_buy, add_sell, add_name2, add_type2, add_x12, add_x22, add_v12, add_c12, add_buy2, add_sell2
    await message.answer('Название?', reply_markup=show_in_menu_button)
    add_name = True

@dp.message(lambda message: add_name)
async def add_varios_name(message):
    global add_name, add_type, add_x1, add_x2, add_v1, add_c1, add_buy, add_sell, add_name2, add_type2, add_x12, add_x22, add_v12, add_c12, add_buy2, add_sell2
    if add_name == False:
        return
    add_name2 = str(message.text)
    await message.answer('Тип?', reply_markup=show_in_menu_button)
    add_name = False
    add_type = True

@dp.message(lambda message: add_type)
async def add_varios_type(message):
    global add_name, add_type, add_x1, add_x2, add_v1, add_c1, add_buy, add_sell, add_name2, add_type2, add_x12, add_x22, add_v12, add_c12, add_buy2, add_sell2
    if add_type == False:
        return
    add_type = False
    add_x1 = True

    add_type2 = str(message.text)
    await message.answer('x1?', reply_markup=show_in_menu_button)

@dp.message(lambda message: add_x1)
async def add_varios_x1(message):
    global add_name, add_type, add_x1, add_x2, add_v1, add_c1, add_buy, add_sell, add_name2, add_type2, add_x12, add_x22, add_v12, add_c12, add_buy2, add_sell2
    if add_x1 == False:
        return
    add_x12 = int(message.text)
    await message.answer('x2?', reply_markup=show_in_menu_button)
    add_x1 = False
    add_x2 = True

@dp.message(lambda message: add_x2)
async def add_varios_x2(message):
    global add_name, add_type, add_x1, add_x2, add_v1, add_c1, add_buy, add_sell, add_name2, add_type2, add_x12, add_x22, add_v12, add_c12, add_buy2, add_sell2
    if add_x2 == False:
        return
    add_x22 = int(message.text)
    await message.answer('Вкус?', reply_markup=show_in_menu_button)
    add_x2 = False
    add_v1 = True

@dp.message(lambda message: add_v1)
async def add_varios_v1(message):
    global add_name, add_type, add_x1, add_x2, add_v1, add_c1, add_buy, add_sell, add_name2, add_type2, add_x12, add_x22, add_v12, add_c12, add_buy2, add_sell2
    if add_v1 == False:
        return
    add_v12 = str(message.text)
    await message.answer('Закуп?', reply_markup=show_in_menu_button)
    add_v1 = False
    add_buy = True

@dp.message(lambda message: add_buy)
async def add_varios_buy(message):
    global add_name, add_type, add_x1, add_x2, add_v1, add_c1, add_buy, add_sell, add_name2, add_type2, add_x12, add_x22, add_v12, add_c12, add_buy2, add_sell2
    if add_buy == False:
        return
    add_buy2 = float(message.text)
    await message.answer('Продажа?', reply_markup=show_in_menu_button)
    add_buy = False
    add_sell = True

@dp.message(lambda message: add_sell)
async def add_varios_sell(message):
    global add_name, add_type, add_x1, add_x2, add_v1, add_c1, add_buy, add_sell, add_name2, add_type2, add_x12, add_x22, add_v12, add_c12, add_buy2, add_sell2
    if add_sell == False:
        return
    add_sell2 = float(message.text)
    await message.answer('Количество?', reply_markup=show_in_menu_button)
    add_sell = False
    add_c1 = True
    
@dp.message(lambda message: add_c1)
async def add_varios_c1(message):
    global add_name, add_type, add_x1, add_x2, add_v1, add_c1, add_buy, add_sell, add_name2, add_type2, add_x12, add_x22, add_v12, add_c12, add_buy2, add_sell2
    if add_c1 == False:
        return
    add_c12 = float(message.text)

    sql.execute(f'''SELECT name from JIJI WHERE name=(?) AND type=(?) AND x1=(?) AND x2=(?) AND v1=(?) AND buy=(?) AND sell=(?) ''', 
                (add_name2, add_type2, add_x12, add_x22, add_v12, add_buy2, add_sell2))
    text1 = 'Товар добавлен в таблицу'
    text2 = 'Такой товар уже имеется, количество обновлено'
    if sql.fetchone() is None:
        sql.execute(f'''INSERT INTO JIJI(name, type, x1, x2, v1, c1, buy, sell) VALUES (?, ?, ?, ?, ?, ?, ?, ?) ''',
                (add_name2, add_type2, add_x12, add_x22, add_v12, add_c12, add_buy2, add_sell2))
        db.commit()
        await message.answer(text1, reply_markup=show_menu)
    else:
        sql.execute('''SELECT c1 FROM JIJI WHERE name=(?) AND type=(?) AND x1=(?) AND x2=(?) AND v1=(?) AND buy=(?) AND sell=(?) ''', 
                (add_name2, add_type2, add_x12, add_x22, add_v12, add_buy2, add_sell2))
        c1 = int(sql.fetchall()[0][0])
        upd_count = c1 + add_c12
        sql.execute(f'''UPDATE JIJI SET c1=(?) WHERE name=(?) AND type=(?) AND x1=(?) AND x2=(?) AND v1=(?) AND buy=(?) AND sell=(?) ''', 
                    (upd_count, add_name2, add_type2, add_x12, add_x22, add_v12, add_buy2, add_sell2))
        db.commit()
        await message.answer(text2, reply_markup=show_menu)

    add_name = False
    add_type = False
    add_x1 = False
    add_x2 = False
    add_v1 = False
    add_c1 = False
    add_buy = False
    add_sell = False

    add_name2 = []
    add_type2 = []
    add_x12 = []
    add_x22 = []
    add_v12 = []
    add_c12 = []
    add_buy2 = []
    add_sell2 = []

async def clear():
    global add_status
    global add_name, add_type, add_x1, add_x2, add_v1, add_c1, add_buy, add_sell, add_name2, add_type2, add_x12, add_x22, add_v12, add_c12, add_buy2, add_sell2
    global del_name_list, del_flavor_list, del_type_list
    global del_type, del_name, del_flavor, del_price

    del_name_list = []
    del_flavor_list = []
    del_type_list = []

    add_status = False

    add_name = False
    add_type = False
    add_x1 = False
    add_x2 = False
    add_v1 = False
    add_c1 = False
    add_buy = False
    add_sell = False

    add_name2 = []
    add_type2 = []
    add_x12 = []
    add_x22 = []
    add_v12 = []
    add_c12 = []
    add_buy2 = []
    add_sell2 = []

    del_type = False
    del_name = False
    del_flavor = False
    del_price = False

    sql.execute('''DELETE FROM WORK ''')
    db.commit()