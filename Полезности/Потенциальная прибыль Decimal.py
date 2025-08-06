#@dp.callback_query(lambda query: query.data == "buy")
@dp.message(F.text =="ЗАКУП")
#async def statistics(query):
async def statistics(message):
    sql.execute('SELECT c1, buy, sell, type FROM JIJI WHERE ((v1 IS NOT NULL AND c1 > 0))')
    rows = sql.fetchall()

    total_purchase = 0
    total_c1 = 0
    total_potential_profit = 0
    total_net_profit = 0 
    totals_per_type = {}
    
    for row in rows:
        c1_quantity = row[0]
        buy_price = Decimal(row[1])
        sell_price = Decimal(row[2])
        item_type = row[3]

        total_purchase += buy_price * c1_quantity
        total_purchase = total_purchase.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        total_c1 += c1_quantity

        potential_profit = sell_price * c1_quantity
        total_potential_profit += potential_profit

        net_profit = potential_profit - (buy_price * c1_quantity)
        total_net_profit += net_profit

        if item_type not in totals_per_type:
            totals_per_type[item_type] = {'total_sum': Decimal(0), 'total_quantity': 0, 'total_potential_profit': Decimal(0), 'total_net_profit': Decimal(0)}
        
        totals_per_type[item_type]['total_sum'] += buy_price * c1_quantity
        totals_per_type[item_type]['total_quantity'] += c1_quantity
        totals_per_type[item_type]['total_potential_profit'] += potential_profit
        totals_per_type[item_type]['total_net_profit'] += net_profit
    
    total_potential_profit = total_potential_profit.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    total_net_profit = total_net_profit.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    if total_potential_profit == total_potential_profit.to_integral():
        total_potential_profit = total_potential_profit.quantize(Decimal('1'))
    else:
        total_potential_profit = total_potential_profit.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    if total_net_profit == total_net_profit.to_integral():
        total_net_profit = total_net_profit.quantize(Decimal('1'))
    else:
        total_net_profit = total_net_profit.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    response_message = f"Общий\nЗакуп: {total_purchase}р\nКоличество: {total_c1}\n"
    response_message += f"Продажа: {total_potential_profit}р ({total_net_profit}р)\n\n"
    
    for item_type, totals in totals_per_type.items():
        total_sum = totals['total_sum'].quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        total_quantity = totals['total_quantity']
        total_potential_profit_type = totals['total_potential_profit'].quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        total_net_profit_type = totals['total_net_profit'].quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        if total_sum == total_sum.to_integral():
            total_sum = total_sum.quantize(Decimal('1'))
        else:
            total_sum = total_sum.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        if total_potential_profit_type == total_potential_profit_type.to_integral():
            total_potential_profit_type = total_potential_profit_type.quantize(Decimal('1'))
        else:
            total_potential_profit_type = total_potential_profit_type.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        if total_net_profit_type == total_net_profit_type.to_integral():
            total_net_profit_type = total_net_profit_type.quantize(Decimal('1'))
        else:
            total_net_profit_type = total_net_profit_type.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        response_message += f"{item_type}: {total_sum}р\nКоличество: {total_quantity} шт.\nПродажа: {total_potential_profit_type}р ({total_net_profit_type}р)\n\n"
    
    """await query.message.edit_text(response_message)
    await query.message.answer('Что делаем?', reply_markup=show_menu)"""
    await message.answer(response_message)
    await message.answer('Что делаем?', reply_markup=show_menu)
