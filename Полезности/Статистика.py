@dp.callback_query(lambda query: query.data == "stat")
async def statistics(query):
    if query.from_user.id not in admins:
        return await query.message.answer('Ты не мой братик!', reply_markup = show_menu)
    await query.message.edit_text(f"Статистика", reply_markup=show_stat)

async def write_sales_this(sales_data, total_sales, total_profit, type_sales, type_profit):
    workbook = openpyxl.Workbook()
    sheet = workbook.active

    headers = ["Время", "Дата", "Название", "Тип", "Характеристика", "Цена", "Профит", "Приписка"]
    sheet.append(headers)

    for sale in sales_data:
        product_name, product_type, product_x1, product_x2, product_v1, purchase_price, selling_price, note, sale_date, sale_time = sale
        formatted_sale_date = datetime.strptime(sale_date, "%Y.%m.%d").strftime("%m.%d")
        profit = selling_price - purchase_price
        row_data = [sale_time, formatted_sale_date, product_name, product_type, product_v1, selling_price, profit, note]
        sheet.append(row_data)

    sheet.cell(row=1, column=10, value="Всего реализовано:")
    sheet.cell(row=1, column=11, value=total_sales)
    sheet.cell(row=2, column=10, value="Выручка (прибыль):")
    sheet.cell(row=2, column=11, value=total_profit)

    row_offset = 3
    sheet.cell(row=row_offset - 2, column=13, value="По типам продуктов")
    sheet.cell(row=row_offset - 1, column=13, value="Тип")
    sheet.cell(row=row_offset - 1, column=14, value="Количество")
    sheet.cell(row=row_offset - 1, column=15, value="Выручка")

    for i, (product_type, sales_count) in enumerate(type_sales.items(), start=row_offset):
        sheet.cell(row=i, column=13, value=f"{product_type}:")
        sheet.cell(row=i, column=14, value=sales_count)
        sheet.cell(row=i, column=15, value=type_profit[product_type])

    column_widths = [8, 8, 25, 23, 30, 8, 8, 30, 10, 23, 11, 10, 23, 13, 10]
    for i, width in enumerate(column_widths, start=1):
        sheet.column_dimensions[get_column_letter(i)].width = width

    excel_file_name = "this_stats.xlsx"
    workbook.save(excel_file_name)

    return excel_file_name

@dp.callback_query(lambda query: query.data == "this")
async def stat_this(query):
    if query.from_user.id not in admins:
        return await query.message.answer('Ты не мой братик!', reply_markup = show_menu)
    current_date = datetime.now()

    first_day_of_month = current_date.replace(day=1)
    last_day_of_month = first_day_of_month.replace(
        day=calendar.monthrange(current_date.year, current_date.month)[1]
    )

    first_day_of_month_str = first_day_of_month.strftime('%Y.%m.%d')
    last_day_of_month_str = last_day_of_month.strftime('%Y.%m.%d')

    sql_query = f"SELECT * FROM Stat WHERE date BETWEEN '{first_day_of_month_str}' AND '{last_day_of_month_str}'"
    sql.execute(sql_query)
    sales_data = sql.fetchall()

    total_sales = 0
    total_revenue = 0
    total_profit = 0

    if sales_data:
        response_message = f"Продажи за {current_date.strftime('%m.%y')}:\n"
        type_sales = defaultdict(int)
        type_revenue = defaultdict(float)
        type_profit = defaultdict(float)

        for sale in sales_data:
            product_name, product_type, product_x1, product_x2, product_v1, purchase_price, selling_price, note, sale_date, sale_time = sale
        
            total_sales += 1
            total_revenue += selling_price
            total_revenue = int(total_revenue) if total_revenue.is_integer() else round(total_revenue, 2)

            total_profit += (selling_price - purchase_price)
            total_profit = int(total_profit) if total_profit.is_integer() else round(total_profit, 2)

            type_sales[product_type] += 1

            type_revenue[product_type] += selling_price
            type_revenue[product_type] = int(type_revenue[product_type]) if type_revenue[product_type].is_integer() else round(type_revenue[product_type], 2)

            type_profit[product_type] += (selling_price - purchase_price)
            type_profit[product_type] = int(type_profit[product_type]) if type_profit[product_type].is_integer() else round(type_profit[product_type], 2)

        response_message += f"Всего реализовано: {total_sales}\n"
        response_message += f"Выручка (прибыль): {total_revenue}р ({total_profit}р)\n"

        response_message += "➖➖➖➖➖➖➖➖➖➖\n"
        for product_type, sales_count in type_sales.items():
            response_message += f"{product_type}\t: {sales_count}\t| {type_revenue[product_type]}р ({type_profit[product_type]}р)\n"

        excel_file = await write_sales_this(sales_data, total_sales, total_profit, type_sales, type_profit)

    else:
        response_message = "Нет продаж за текущий месяц."

    await query.message.answer_document(FSInputFile(excel_file), caption=response_message, parse_mode=ParseMode.MARKDOWN)
    await query.message.answer("Стартовое меню", reply_markup=show_menu)

async def write_sales_last(sales_data, total_sales, total_profit, type_sales, type_profit):
    workbook = openpyxl.Workbook()
    sheet = workbook.active

    headers = ["Время", "Дата", "Название", "Тип", "Характеристика", "Цена", "Профит", "Приписка"]
    sheet.append(headers)

    for sale in sales_data:
        product_name, product_type, product_x1, product_x2, product_v1, purchase_price, selling_price, note, sale_date, sale_time = sale
        formatted_sale_date = datetime.strptime(sale_date, "%Y.%m.%d").strftime("%m.%d")
        profit = selling_price - purchase_price
        row_data = [sale_time, formatted_sale_date, product_name, product_type, product_v1, selling_price, profit, note]
        sheet.append(row_data)

    sheet.cell(row=1, column=10, value="Всего продаж:")
    sheet.cell(row=1, column=11, value=total_sales)
    sheet.cell(row=2, column=10, value="Общая прибыль:")
    sheet.cell(row=2, column=11, value=total_profit)

    row_offset = 3
    sheet.cell(row=row_offset - 2, column=13, value="По типам продуктов")
    sheet.cell(row=row_offset - 1, column=13, value="Тип")
    sheet.cell(row=row_offset - 1, column=14, value="Количество")
    sheet.cell(row=row_offset - 1, column=15, value="Выручка")

    for i, (product_type, sales_count) in enumerate(type_sales.items(), start=row_offset):
        sheet.cell(row=i, column=13, value=f"{product_type}:")
        sheet.cell(row=i, column=14, value=sales_count)
        sheet.cell(row=i, column=15, value=type_profit[product_type])

    column_widths = [8, 8, 25, 23, 30, 8, 8, 30, 10, 23, 11, 10, 23, 13, 10, 30]
    for i, width in enumerate(column_widths, start=1):
        sheet.column_dimensions[get_column_letter(i)].width = width

    excel_file_name = "last_stats.xlsx"
    workbook.save(excel_file_name)

    return excel_file_name

@dp.callback_query(lambda query: query.data == "last")
async def stat_last(query):
    if query.from_user.id not in admins:
        return await query.message.answer('Ты не мой братик!', reply_markup = show_menu)
    current_date = datetime.now()

    first_day_of_previous_month = (current_date.replace(day=1) - timedelta(days=1)).replace(day=1)
    last_day_of_previous_month = first_day_of_previous_month.replace(
        day=calendar.monthrange(first_day_of_previous_month.year, first_day_of_previous_month.month)[1]
    )

    first_day_of_month_str = first_day_of_previous_month.strftime('%Y.%m.%d')
    last_day_of_month_str = last_day_of_previous_month.strftime('%Y.%m.%d')

    sql_query = f"SELECT * FROM Stat WHERE date BETWEEN '{first_day_of_month_str}' AND '{last_day_of_month_str}'"
    sql.execute(sql_query)
    sales_data = sql.fetchall()

    total_sales = 0
    total_revenue = 0
    total_profit = 0

    if sales_data:
        response_message = f"Продажи за {first_day_of_previous_month.strftime('%m.%y')}:\n"
        type_sales = defaultdict(int)
        type_revenue = defaultdict(float)
        type_profit = defaultdict(float)

        for sale in sales_data:
            product_name, product_type, product_x1, product_x2, product_v1, purchase_price, selling_price, note, sale_date, sale_time = sale
        
            total_sales += 1
            total_revenue += selling_price
            total_revenue = int(total_revenue) if total_revenue.is_integer() else round(total_revenue, 2)

            total_profit += (selling_price - purchase_price)
            total_profit = int(total_profit) if total_profit.is_integer() else round(total_profit, 2)

            type_sales[product_type] += 1

            type_revenue[product_type] += selling_price
            type_revenue[product_type] = int(type_revenue[product_type]) if type_revenue[product_type].is_integer() else round(type_revenue[product_type], 2)

            type_profit[product_type] += (selling_price - purchase_price)
            type_profit[product_type] = int(type_profit[product_type]) if type_profit[product_type].is_integer() else round(type_profit[product_type], 2)

        response_message += f"Всего реализовано: {total_sales}\n"
        response_message += f"Выручка (прибыль): {total_revenue}р ({total_profit}р)\n"

        response_message += "➖➖➖➖➖➖➖➖➖➖\n"
        for product_type, sales_count in type_sales.items():
            response_message += f"{product_type}\t: {sales_count}\t| {type_revenue[product_type]}р ({type_profit[product_type]}р)\n"

        excel_file = await write_sales_last(sales_data, total_sales, total_profit, type_sales, type_profit)

    else:
        response_message = "Нет продаж за предыдущий месяц."

    await query.message.answer_document(FSInputFile(excel_file), caption=response_message, parse_mode=ParseMode.MARKDOWN)
    await query.message.answer("Что делаем?", reply_markup=show_menu)

async def write_sales_to_excel(sales_data, total_sales, total_profit, first_sale_date, type_sales, type_profit):
    workbook = openpyxl.Workbook()
    sheet = workbook.active

    headers = ["Время", "Дата", "Название", "Тип", "Характеристика", "Цена", "Профит", "Приписка"]
    sheet.append(headers)

    for sale in sales_data:
        product_name, product_type, product_x1, product_x2, product_v1, purchase_price, selling_price, note, sale_date, sale_time = sale
        formatted_sale_date = datetime.strptime(sale_date, "%Y.%m.%d").strftime("%m.%d")
        profit = selling_price - purchase_price
        row_data = [sale_time, formatted_sale_date, product_name, product_type, product_v1, selling_price, profit, note]
        sheet.append(row_data)

    sheet.cell(row=1, column=10, value="Всего продаж:")
    sheet.cell(row=1, column=11, value=total_sales)
    sheet.cell(row=2, column=10, value="Общая прибыль:")
    sheet.cell(row=2, column=11, value=total_profit)
    sheet.cell(row=3, column=10, value="Дата первой продажи:")
    sheet.cell(row=3, column=11, value=first_sale_date)

    row_offset = 3
    sheet.cell(row=row_offset - 2, column=13, value="По типам продуктов")
    sheet.cell(row=row_offset - 1, column=13, value="Тип")
    sheet.cell(row=row_offset - 1, column=14, value="Количество")
    sheet.cell(row=row_offset - 1, column=15, value="Выручка")

    for i, (product_type, sales_count) in enumerate(type_sales.items(), start=row_offset):
        sheet.cell(row=i, column=13, value=f"{product_type}:")
        sheet.cell(row=i, column=14, value=sales_count)
        sheet.cell(row=i, column=15, value=type_profit[product_type])

    column_widths = [8, 8, 25, 23, 30, 8, 8, 30, 10, 23, 11, 10, 23, 13, 10, 30]
    for i, width in enumerate(column_widths, start=1):
        sheet.column_dimensions[get_column_letter(i)].width = width

    excel_file_name = "all_stats.xlsx"
    workbook.save(excel_file_name)

    return excel_file_name

@dp.callback_query(lambda query: query.data == "all")
async def stat_all(query):
    if query.from_user.id not in admins:
        return await query.message.answer('Ты не мой братик!', reply_markup = show_menu)
    sql_query = "SELECT * FROM Stat"
    sql.execute(sql_query)
    sales_data = sql.fetchall()

    total_sales = 0
    total_revenue = 0
    total_profit = 0

    if sales_data:
        first_sale_date = None
        type_sales = defaultdict(int)
        type_revenue = defaultdict(float)
        type_profit = defaultdict(float)

        for sale in sales_data:
            product_name, product_type, product_x1, product_x2, product_v1, purchase_price, selling_price, note, sale_date, sale_time = sale

            if first_sale_date is None or sale_date < first_sale_date:
                first_sale_date = sale_date
            response_message = f"Дата первой продажи: {first_sale_date}\n"
            total_sales += 1
            total_revenue += selling_price
            total_revenue = int(total_revenue) if total_revenue.is_integer() else round(total_revenue, 2)

            total_profit += (selling_price - purchase_price)
            total_profit = int(total_profit) if total_profit.is_integer() else round(total_profit, 2)

            type_sales[product_type] += 1

            type_revenue[product_type] += selling_price
            type_revenue[product_type] = int(type_revenue[product_type]) if type_revenue[product_type].is_integer() else round(type_revenue[product_type], 2)

            type_profit[product_type] += (selling_price - purchase_price)
            type_profit[product_type] = int(type_profit[product_type]) if type_profit[product_type].is_integer() else round(type_profit[product_type], 2)

        response_message += f"Всего продаж: {total_sales}\n"
        response_message += f"Выручка (прибыль):\n"
        response_message += f"{total_revenue}р ({total_profit}р)\n"

        response_message += "➖➖➖➖➖➖➖➖➖➖\n"
        for product_type, sales_count in type_sales.items():
            response_message += f"{product_type}\t: {sales_count}\t| {type_revenue[product_type]}р ({type_profit[product_type]}р)\n"

        excel_file = await write_sales_to_excel(sales_data, total_sales, total_profit, first_sale_date, type_sales, type_profit)

    else:
        response_message = "Нет продаж за все время."

    await query.message.answer_document(FSInputFile(excel_file), caption=response_message, parse_mode=ParseMode.MARKDOWN)
    await query.message.answer("Стартовое меню", reply_markup=show_menu)
