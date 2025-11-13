# import frappe
# from datetime import datetime

# def execute(filters=None):
#     filters = filters or {}

#     from_date = filters.get('from_date')
#     to_date = filters.get('to_date')

#     if not from_date or not to_date:
#         frappe.throw("Please set From Date and To Date")

#     item_codes = [
#         '6287016760027',
#         '6287016760034',
#         '6287016760041',
#         '6287016760058',
#         '6287016760119',
#         '6287016760157',
#         '6287016760164',
#     ]

#     months = get_month_list(from_date, to_date)

#     # Columns
#     columns = [
#         {"label": "Item Code", "fieldname": "item_code", "fieldtype": "Data", "width": 150},
#         {"label": "Item Name", "fieldname": "item_name", "fieldtype": "Data", "width": 200},
#     ]

#     for m in months:
#         columns.append({
#             "label": f"{m} Qty",
#             "fieldname": f"{m}_qty",
#             "fieldtype": "Float",
#             "precision": 2,
#             "width": 120,
#         })
#         columns.append({
#             "label": f"{m} Cases",
#             "fieldname": f"{m}_cases",
#             "fieldtype": "Data",
#             "width": 130,
#         })

#     placeholders = ','.join(['%s'] * len(item_codes))

#     query = f"""
#         SELECT 
#             sii.item_code,
#             sii.item_name,
#             DATE_FORMAT(si.posting_date, '%%b %%Y') as month,
#             SUM(sii.qty) as total_qty,
#             SUM(sii.cases) as total_cases
#         FROM
#             `tabSales Invoice` si
#         INNER JOIN
#             `tabSales Invoice Item` sii ON sii.parent = si.name
#         WHERE 
#             si.docstatus = 1
#             AND si.posting_date BETWEEN %s AND %s
#             AND sii.item_code IN ({placeholders})
#         GROUP BY
#             sii.item_code, sii.item_name, month
#         ORDER BY
#             sii.item_code, month
#     """

#     args = [from_date, to_date] + item_codes
#     data = frappe.db.sql(query, args, as_dict=True)

#     # Data Mapping
#     data_map = {}
#     raw_totals = {m: 0.0 for m in months}

#     for row in data:
#         key = row.item_code
#         if key not in data_map:
#             data_map[key] = {
#                 "item_code": row.item_code,
#                 "item_name": row.item_name,
#             }
#             for m in months:
#                 data_map[key][f"{m}_qty"] = 0.0
#                 data_map[key][f"{m}_cases"] = "0.00"

#         qty = round(row.total_qty or 0, 2)
#         cases = round(row.total_cases or 0, 2)

#         data_map[key][f"{row.month}_qty"] = qty
#         data_map[key][f"{row.month}_cases"] = "{:,.2f}".format(cases)

#         raw_totals[row.month] += cases

#     data_list = list(data_map.values())

#     # Total row
#     total_row = {
#         "item_code": "Total",
#         "item_name": "",
#     }

#     chart_values = []
#     for m in months:
#         total_qty = sum(d.get(f"{m}_qty", 0) for d in data_list)
#         total_cases = raw_totals[m]
#         total_row[f"{m}_qty"] = round(total_qty, 2)
#         total_row[f"{m}_cases"] = "{:,.2f}".format(total_cases)
#         chart_values.append(round(total_cases, 2))

#     data_list.append(total_row)

#     # Total of all months for chart title & big display
#     total_all_cases = sum(chart_values)
#     total_all_cases_formatted = "{:,.2f}".format(total_all_cases)

#     # Big bold HTML to show above chart
#     big_total_html = f"""
#     <div style='
#         font-size: 28px; 
#         font-weight: bold; 
#         color: #2c3e50; 
#         margin-bottom: 10px;
#         text-align: center;
#     '>
#         Total Cases = {total_all_cases_formatted}
#     </div>
#     """

#     # Chart config with plain title (optional)
#     chart = {
#         "data": {
#             "labels": months,
#             "datasets": [
#                 {
#                     "name": "Total Cases",
#                     "values": chart_values
#                 }
#             ]
#         },
#         "type": "bar",
#         "colors": ["#5e64ff"],
#         "title": f"Total Cases = {total_all_cases_formatted}"
#     }

#     return columns, data_list, big_total_html, chart


# def get_month_list(from_date, to_date):
#     start = datetime.strptime(from_date, "%Y-%m-%d")
#     end = datetime.strptime(to_date, "%Y-%m-%d")

#     months = []
#     current = start.replace(day=1)
#     while current <= end:
#         months.append(current.strftime("%b %Y"))
#         if current.month == 12:
#             current = current.replace(year=current.year + 1, month=1)
#         else:
#             current = current.replace(month=current.month + 1)
#     return months



# import frappe
# from datetime import datetime

# def execute(filters=None):
#     filters = filters or {}

#     from_date = filters.get('from_date')
#     to_date = filters.get('to_date')

#     if not from_date or not to_date:
#         frappe.throw("Please set From Date and To Date")

#     item_codes = [
#         '6287016760027',
#         '6287016760034',
#         '6287016760041',
#         '6287016760058',
#         '6287016760119',
#         '6287016760157',
#         '6287016760164',
#     ]

#     months = get_month_list(from_date, to_date)

#     # Columns
#     columns = [
#         {"label": "Item Code", "fieldname": "item_code", "fieldtype": "Data", "width": 150},
#         {"label": "Item Name", "fieldname": "item_name", "fieldtype": "Data", "width": 200},
#     ]

#     for m in months:
#         columns.append({
#             "label": f"{m} Qty",
#             "fieldname": f"{m}_qty",
#             "fieldtype": "Float",
#             "precision": 2,
#             "width": 120,
#         })
#         columns.append({
#             "label": f"{m} Cases",
#             "fieldname": f"{m}_cases",
#             "fieldtype": "Data",
#             "width": 130,
#         })

#     placeholders = ','.join(['%s'] * len(item_codes))

#     query = f"""
#         SELECT 
#             sii.item_code,
#             sii.item_name,
#             DATE_FORMAT(si.posting_date, '%%b %%Y') as month,
#             SUM(sii.qty) as total_qty,
#             SUM(sii.cases) as total_cases
#         FROM
#             `tabSales Invoice` si
#         INNER JOIN
#             `tabSales Invoice Item` sii ON sii.parent = si.name
#         WHERE 
#             si.docstatus = 1
#             AND si.posting_date BETWEEN %s AND %s
#             AND sii.item_code IN ({placeholders})
#         GROUP BY
#             sii.item_code, sii.item_name, month
#         ORDER BY
#             sii.item_code, month
#     """

#     args = [from_date, to_date] + item_codes
#     data = frappe.db.sql(query, args, as_dict=True)

#     # Data Mapping
#     data_map = {}
#     raw_totals = {m: 0.0 for m in months}

#     for row in data:
#         key = row.item_code
#         if key not in data_map:
#             data_map[key] = {
#                 "item_code": row.item_code,
#                 "item_name": row.item_name,
#             }
#             for m in months:
#                 data_map[key][f"{m}_qty"] = 0.0
#                 data_map[key][f"{m}_cases"] = "0.00"

#         qty = round(row.total_qty or 0, 2)
#         cases = round(row.total_cases or 0, 2)

#         data_map[key][f"{row.month}_qty"] = qty
#         data_map[key][f"{row.month}_cases"] = "{:,.2f}".format(cases)

#         raw_totals[row.month] += cases

#     data_list = list(data_map.values())

#     # Total row
#     total_row = {
#         "item_code": "Total",
#         "item_name": "",
#     }

#     chart_values = []
#     for m in months:
#         total_qty = sum(d.get(f"{m}_qty", 0) for d in data_list)
#         total_cases = raw_totals[m]
#         total_row[f"{m}_qty"] = round(total_qty, 2)
#         total_row[f"{m}_cases"] = "{:,.2f}".format(total_cases)
#         chart_values.append(round(total_cases, 2))

#     data_list.append(total_row)

#     # Calculate average only for months with data (non-zero)
#     months_with_data = [v for v in chart_values if v > 0]
#     total_cases_sum = sum(chart_values)
#     avg_cases = (sum(months_with_data) / len(months_with_data)) if months_with_data else 0

#     total_cases_formatted = "{:,.2f}".format(total_cases_sum)
#     avg_cases_formatted = "{:,.2f}".format(avg_cases)

#     # Improved big bold HTML to show above chart
#     big_total_html = f"""
#     <div style="
#         font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
#         font-size: 22px;
#         font-weight: 700;
#         color: #34495e;
#         background: #f0f4f8;
#         padding: 15px 25px;
#         border-radius: 8px;
#         text-align: center;
#         box-shadow: 0 4px 10px rgba(0,0,0,0.1);
#         max-width: 480px;
#         margin: 0 auto 20px auto;
#         user-select: none;
#     ">
#         <span style="color: #2980b9;">Total Cases:</span> <span style="color: #2c3e50;">{total_cases_formatted}</span> 
#         &nbsp;&nbsp;|&nbsp;&nbsp; 
#         <span style="color: #2980b9;">Average Cases:</span> <span style="color: #2c3e50;">{avg_cases_formatted}</span>
#     </div>
#     """

#     # Chart config
#     chart = {
#         "data": {
#             "labels": months,
#             "datasets": [
#                 {
#                     "name": "Total Cases",
#                     "values": chart_values
#                 }
#             ]
#         },
#         "type": "bar",
#         "colors": ["#5e64ff"],
#         "title": f"Total Cases = {total_cases_formatted} | Average Cases = {avg_cases_formatted}"
#     }

#     return columns, data_list, big_total_html, chart


# def get_month_list(from_date, to_date):
#     start = datetime.strptime(from_date, "%Y-%m-%d")
#     end = datetime.strptime(to_date, "%Y-%m-%d")

#     months = []
#     current = start.replace(day=1)
#     while current <= end:
#         months.append(current.strftime("%b %Y"))
#         if current.month == 12:
#             current = current.replace(year=current.year + 1, month=1)
#         else:
#             current = current.replace(month=current.month + 1)
#     return months



# import frappe
# from datetime import datetime

# def execute(filters=None):
#     filters = filters or {}

#     from_date = filters.get('from_date')
#     to_date = filters.get('to_date')

#     if not from_date or not to_date:
#         frappe.throw("Please set From Date and To Date")

#     item_codes = [
#         '6287016760027',
#         '6287016760034',
#         '6287016760041',
#         '6287016760058',
#         '6287016760119',
#         '6287016760157',
#         '6287016760164',
#     ]

#     months = get_month_list(from_date, to_date)

#     # Columns
#     columns = [
#         {"label": "Item Code", "fieldname": "item_code", "fieldtype": "Data", "width": 150},
#         {"label": "Item Name", "fieldname": "item_name", "fieldtype": "Data", "width": 200},
#     ]

#     for m in months:
#         columns.append({
#             "label": f"{m} Qty",
#             "fieldname": f"{m}_qty",
#             "fieldtype": "Float",
#             "precision": 2,
#             "width": 120,
#         })
#         columns.append({
#             "label": f"{m} Cases",
#             "fieldname": f"{m}_cases",
#             "fieldtype": "Data",
#             "width": 130,
#         })

#     placeholders = ','.join(['%s'] * len(item_codes))

#     query = f"""
#         SELECT 
#             sii.item_code,
#             sii.item_name,
#             DATE_FORMAT(si.posting_date, '%%b %%Y') as month,
#             SUM(sii.qty) as total_qty,
#             SUM(sii.cases) as total_cases
#         FROM
#             `tabSales Invoice` si
#         INNER JOIN
#             `tabSales Invoice Item` sii ON sii.parent = si.name
#         WHERE 
#             si.docstatus = 1
#             AND si.posting_date BETWEEN %s AND %s
#             AND sii.item_code IN ({placeholders})
#         GROUP BY
#             sii.item_code, sii.item_name, month
#         ORDER BY
#             sii.item_code, month
#     """

#     args = [from_date, to_date] + item_codes
#     data = frappe.db.sql(query, args, as_dict=True)

#     # Data Mapping
#     data_map = {}
#     raw_totals = {m: 0.0 for m in months}

#     for row in data:
#         key = row.item_code
#         if key not in data_map:
#             data_map[key] = {
#                 "item_code": row.item_code,
#                 "item_name": row.item_name,
#             }
#             for m in months:
#                 data_map[key][f"{m}_qty"] = 0.0
#                 data_map[key][f"{m}_cases"] = "0.00"

#         qty = round(row.total_qty or 0, 2)
#         cases = round(row.total_cases or 0, 2)

#         data_map[key][f"{row.month}_qty"] = qty
#         data_map[key][f"{row.month}_cases"] = "{:,.2f}".format(cases)

#         raw_totals[row.month] += cases

#     data_list = list(data_map.values())

#     # Total row
#     total_row = {
#         "item_code": "Total",
#         "item_name": "",
#     }

#     chart_values = []
#     for m in months:
#         total_qty = sum(d.get(f"{m}_qty", 0) for d in data_list)
#         total_cases = raw_totals[m]
#         total_row[f"{m}_qty"] = round(total_qty, 2)
#         total_row[f"{m}_cases"] = "{:,.2f}".format(total_cases)
#         chart_values.append(round(total_cases, 2))

#     data_list.append(total_row)

#     # Calculate average only for months with data (non-zero)
#     months_with_data = [v for v in chart_values if v > 0]
#     total_cases_sum = sum(chart_values)
#     avg_cases = (sum(months_with_data) / len(months_with_data)) if months_with_data else 0

#     total_cases_formatted = "{:,.2f}".format(total_cases_sum)
#     avg_cases_formatted = "{:,.2f}".format(avg_cases)

#     # Minimal HTML for bold and larger font
#     # big_total_text = f"<b style='font-size:18px;'>Total Cases = {total_cases_formatted} | Average Cases = {avg_cases_formatted}</b>"
#     big_total_text = f"Total Cases = {total_cases_formatted} | Average Cases = {avg_cases_formatted}"


#     # Chart config
#     chart = {
#         "data": {
#             "labels": months,
#             "datasets": [
#                 {
#                     "name": "Total Cases",
#                     "values": chart_values
#                 }
#             ]
#         },
#         "type": "bar",
#         "colors": ["#5e64ff"],
#         "title": f"Total Cases = {total_cases_formatted} | Average Cases = {avg_cases_formatted}"
#     }

#     return columns, data_list, big_total_text, chart


# def get_month_list(from_date, to_date):
#     start = datetime.strptime(from_date, "%Y-%m-%d")
#     end = datetime.strptime(to_date, "%Y-%m-%d")

#     months = []
#     current = start.replace(day=1)
#     while current <= end:
#         months.append(current.strftime("%b %Y"))
#         if current.month == 12:
#             current = current.replace(year=current.year + 1, month=1)
#         else:
#             current = current.replace(month=current.month + 1)
#     return months




# import frappe
# from datetime import datetime

# def execute(filters=None):
#     filters = filters or {}

#     from_date = filters.get('from_date')
#     to_date = filters.get('to_date')

#     if not from_date or not to_date:
#         frappe.throw("Please set From Date and To Date")

#     item_codes = [
#         '6287016760027',
#         '6287016760034',
#         '6287016760041',
#         '6287016760058',
#         '6287016760119',
#         '6287016760157',
#         '6287016760164',
#     ]

#     months = get_month_list(from_date, to_date)

#     # Columns
#     columns = [
#         {"label": "Item Code", "fieldname": "item_code", "fieldtype": "Data", "width": 150},
#         {"label": "Item Name", "fieldname": "item_name", "fieldtype": "Data", "width": 200},
#     ]

#     for m in months:
#         columns.append({
#             "label": f"{m} Qty",
#             "fieldname": f"{m}_qty",
#             "fieldtype": "Float",
#             "precision": 2,
#             "width": 120,
#         })
#         columns.append({
#             "label": f"{m} Cases",
#             "fieldname": f"{m}_cases",
#             "fieldtype": "Data",
#             "width": 130,
#         })

#     placeholders = ','.join(['%s'] * len(item_codes))

#     query = f"""
#         SELECT 
#             sii.item_code,
#             sii.item_name,
#             DATE_FORMAT(si.posting_date, '%%b %%Y') as month,
#             SUM(sii.qty) as total_qty,
#             SUM(sii.cases) as total_cases
#         FROM
#             `tabSales Invoice` si
#         INNER JOIN
#             `tabSales Invoice Item` sii ON sii.parent = si.name
#         WHERE 
#             si.docstatus = 1
#             AND si.posting_date BETWEEN %s AND %s
#             AND sii.item_code IN ({placeholders})
#         GROUP BY
#             sii.item_code, sii.item_name, month
#         ORDER BY
#             sii.item_code, month
#     """

#     args = [from_date, to_date] + item_codes
#     data = frappe.db.sql(query, args, as_dict=True)

#     # Data Mapping
#     data_map = {}
#     raw_totals = {m: 0.0 for m in months}

#     for row in data:
#         key = row.item_code
#         if key not in data_map:
#             data_map[key] = {
#                 "item_code": row.item_code,
#                 "item_name": row.item_name,
#             }
#             for m in months:
#                 data_map[key][f"{m}_qty"] = 0.0
#                 data_map[key][f"{m}_cases"] = "0.00"

#         qty = round(row.total_qty or 0, 2)
#         cases = round(row.total_cases or 0, 2)

#         data_map[key][f"{row.month}_qty"] = qty
#         data_map[key][f"{row.month}_cases"] = "{:,.2f}".format(cases)

#         raw_totals[row.month] += cases

#     data_list = list(data_map.values())

#     # Total row
#     total_row = {
#         "item_code": "Total",
#         "item_name": "",
#     }

#     chart_values = []
#     for m in months:
#         total_qty = sum(d.get(f"{m}_qty", 0) for d in data_list)
#         total_cases = raw_totals[m]
#         total_row[f"{m}_qty"] = round(total_qty, 2)
#         total_row[f"{m}_cases"] = "{:,.2f}".format(total_cases)
#         chart_values.append(round(total_cases, 2))

#     data_list.append(total_row)

#     # Total of all months for chart title & big display
#     total_all_cases = sum(chart_values)
#     total_all_cases_formatted = "{:,.2f}".format(total_all_cases)

#     # Big bold HTML to show above chart
#     big_total_html = f"""
#     <div style='
#         font-size: 28px; 
#         font-weight: bold; 
#         color: #2c3e50; 
#         margin-bottom: 10px;
#         text-align: center;
#     '>
#         Total Cases = {total_all_cases_formatted}
#     </div>
#     """

#     # Chart config with plain title (optional)
#     chart = {
#         "data": {
#             "labels": months,
#             "datasets": [
#                 {
#                     "name": "Total Cases",
#                     "values": chart_values
#                 }
#             ]
#         },
#         "type": "bar",
#         "colors": ["#5e64ff"],
#         "title": f"Total Cases = {total_all_cases_formatted}"
#     }

#     return columns, data_list, big_total_html, chart


# def get_month_list(from_date, to_date):
#     start = datetime.strptime(from_date, "%Y-%m-%d")
#     end = datetime.strptime(to_date, "%Y-%m-%d")

#     months = []
#     current = start.replace(day=1)
#     while current <= end:
#         months.append(current.strftime("%b %Y"))
#         if current.month == 12:
#             current = current.replace(year=current.year + 1, month=1)
#         else:
#             current = current.replace(month=current.month + 1)
#     return months

import frappe
from datetime import datetime

def execute(filters=None):
    filters = filters or {}

    from_date = filters.get('from_date')
    to_date = filters.get('to_date')

    if not from_date or not to_date:
        frappe.throw("Please set From Date and To Date")

    item_codes = [
        '6287016760027',
        '6287016760034',
        '6287016760041',
        '6287016760058',
        '6287016760119',
        '6287016760157',
        '6287016760164',
    ]

    months = get_month_list(from_date, to_date)

    # Columns
    columns = [
        {"label": "Item Code", "fieldname": "item_code", "fieldtype": "Data", "width": 150},
        {"label": "Item Name", "fieldname": "item_name", "fieldtype": "Data", "width": 200},
    ]

    for m in months:
        columns.append({
            "label": f"{m} Qty",
            "fieldname": f"{m}_qty",
            "fieldtype": "Float",
            "precision": 2,
            "width": 120,
        })
        columns.append({
            "label": f"{m} Cases",
            "fieldname": f"{m}_cases",
            "fieldtype": "Data",
            "width": 130,
        })

    placeholders = ','.join(['%s'] * len(item_codes))

    query = f"""
        SELECT 
            sii.item_code,
            sii.item_name,
            DATE_FORMAT(si.posting_date, '%%b %%Y') as month,
            SUM(sii.qty) as total_qty,
            SUM(sii.cases) as total_cases
        FROM
            `tabSales Invoice` si
        INNER JOIN
            `tabSales Invoice Item` sii ON sii.parent = si.name
        WHERE 
            si.docstatus = 1
            AND si.posting_date BETWEEN %s AND %s
            AND sii.item_code IN ({placeholders})
        GROUP BY
            sii.item_code, sii.item_name, month
        ORDER BY
            sii.item_code, month
    """

    args = [from_date, to_date] + item_codes
    data = frappe.db.sql(query, args, as_dict=True)

    # Data Mapping
    data_map = {}
    raw_case_totals = {m: 0.0 for m in months}
    raw_qty_totals = {m: 0.0 for m in months}

    for row in data:
        key = row.item_code
        if key not in data_map:
            data_map[key] = {
                "item_code": row.item_code,
                "item_name": row.item_name,
            }
            for m in months:
                data_map[key][f"{m}_qty"] = 0.0
                data_map[key][f"{m}_cases"] = "0.00"

        qty = round(row.total_qty or 0, 2)
        cases = round(row.total_cases or 0, 2)

        data_map[key][f"{row.month}_qty"] = qty
        data_map[key][f"{row.month}_cases"] = "{:,.2f}".format(cases)

        raw_case_totals[row.month] += cases
        raw_qty_totals[row.month] += qty

    data_list = list(data_map.values())

    # Total row
    total_row = {
        "item_code": "Total",
        "item_name": "",
    }

    chart_case_values = []
    chart_qty_values = []

    for m in months:
        total_qty = raw_qty_totals[m]
        total_cases = raw_case_totals[m]
        total_row[f"{m}_qty"] = round(total_qty, 2)
        total_row[f"{m}_cases"] = "{:,.2f}".format(total_cases)
        chart_case_values.append(round(total_cases, 2))
        chart_qty_values.append(round(total_qty, 2))

    data_list.append(total_row)

    # Sum of all months (overall totals)
    sum_total_cases = sum(chart_case_values)
    sum_total_qty = sum(chart_qty_values)

    # Append "Total" label for chart
    chart_labels = months + ["Total"]

    # Append totals to chart values
    chart_case_values.append(round(sum_total_cases, 2))
    chart_qty_values.append(round(sum_total_qty, 2))

    # Calculate average only for months with data (non-zero)
    months_with_data = [v for v in chart_case_values[:-1] if v > 0]  # exclude 'Total' bar
    total_cases_sum = sum(chart_case_values[:-1])
    avg_cases = (sum(months_with_data) / len(months_with_data)) if months_with_data else 0

    total_cases_formatted = "{:,.2f}".format(total_cases_sum)
    avg_cases_formatted = "{:,.2f}".format(avg_cases)

    big_total_html = f"""
    <div style="
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-size: 22px;
        font-weight: 700;
        color: #34495e;
        background: #f0f4f8;
        padding: 15px 25px;
        border-radius: 8px;
        text-align: center;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        max-width: 480px;
        margin: 0 auto 20px auto;
        user-select: none;
    ">
        <span style="color: #2980b9;">Total Cases:</span> <span style="color: #2c3e50;">{total_cases_formatted}</span> 
        &nbsp;&nbsp;|&nbsp;&nbsp; 
        <span style="color: #2980b9;">Average Cases:</span> <span style="color: #2c3e50;">{avg_cases_formatted}</span>
    </div>
    """

    chart = {
        "data": {
            "labels": chart_labels,
            "datasets": [
                {
                    "name": "Total Cases",
                    "values": chart_case_values
                },
                {
                    "name": "Total Qty",
                    "values": chart_qty_values
                }
            ]
        },
        "type": "bar",
        "colors": ["#5e64ff", "#00bcd4"],
        "title": f"Monthly Totals with Overall Total | Cases = {total_cases_formatted} | Average = {avg_cases_formatted}",
        "height": 500,
        "width": 900 
    }

    return columns, data_list, big_total_html, chart


def get_month_list(from_date, to_date):
    start = datetime.strptime(from_date, "%Y-%m-%d")
    end = datetime.strptime(to_date, "%Y-%m-%d")

    months = []
    current = start.replace(day=1)
    while current <= end:
        months.append(current.strftime("%b %Y"))
        if current.month == 12:
            current = current.replace(year=current.year + 1, month=1)
        else:
            current = current.replace(month=current.month + 1)
    return months
