# Copyright (c) 2025, Furqan Asghar and contributors
# For license information, please see license.txt

# import frappe

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

#     columns = [
#         {"label": "Item Code", "fieldname": "item_code", "fieldtype": "Data", "width": 150},
#         {"label": "Item Name", "fieldname": "item_name", "fieldtype": "Data", "width": 200},
#         {"label": "Customer Group", "fieldname": "customer_group", "fieldtype": "Data", "width": 180},
#         {"label": "Channel", "fieldname": "channel", "fieldtype": "Data", "width": 150},
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

#     columns.append({
#         "label": "Total Qty",
#         "fieldname": "total_qty",
#         "fieldtype": "Float",
#         "precision": 2,
#         "width": 130,
#     })
#     columns.append({
#         "label": "Total Cases",
#         "fieldname": "total_cases",
#         "fieldtype": "Data",
#         "width": 130,
#     })

#     placeholders = ','.join(['%s'] * len(item_codes))

#     query = f"""
#         SELECT 
#             sii.item_code,
#             sii.item_name,
#             cust.customer_group,
#             custgrp.channel,
#             DATE_FORMAT(si.posting_date, '%%b %%Y') as month,
#             SUM(sii.qty) as total_qty,
#             SUM(sii.cases) as total_cases
#         FROM
#             `tabSales Invoice` si
#         INNER JOIN
#             `tabSales Invoice Item` sii ON sii.parent = si.name
#         INNER JOIN
#             `tabCustomer` cust ON cust.name = si.customer
#         LEFT JOIN
#             `tabCustomer Group` custgrp ON custgrp.name = cust.customer_group
#         WHERE 
#             si.docstatus = 1
#             AND si.posting_date BETWEEN %s AND %s
#             AND sii.item_code IN ({placeholders})
#         GROUP BY
#             sii.item_code, sii.item_name, cust.customer_group, custgrp.channel, month
#         ORDER BY
#             sii.item_code, month
#     """

#     args = [from_date, to_date] + item_codes
#     data = frappe.db.sql(query, args, as_dict=True)

#     data_map = {}
#     raw_case_totals = {m: 0.0 for m in months}
#     raw_qty_totals = {m: 0.0 for m in months}
#     channel_month_cases = {}

#     for row in data:
#         key = (row.item_code, row.customer_group or "", row.channel or "")

#         if key not in data_map:
#             data_map[key] = {
#                 "item_code": row.item_code,
#                 "item_name": row.item_name,
#                 "customer_group": row.customer_group or "",
#                 "channel": row.channel or ""
#             }
#             for m in months:
#                 data_map[key][f"{m}_qty"] = 0.0
#                 data_map[key][f"{m}_cases"] = "0.00"
#             data_map[key]["total_qty"] = 0.0
#             data_map[key]["total_cases"] = 0.0

#         qty = round(row.total_qty or 0, 2)
#         cases = round(row.total_cases or 0, 2)

#         data_map[key][f"{row.month}_qty"] = qty
#         data_map[key][f"{row.month}_cases"] = "{:,.2f}".format(cases)

#         raw_case_totals[row.month] += cases
#         raw_qty_totals[row.month] += qty

#         data_map[key]["total_qty"] += qty
#         data_map[key]["total_cases"] += cases

#         channel = row.channel or "Unknown"
#         if channel not in channel_month_cases:
#             channel_month_cases[channel] = {m: 0.0 for m in months}
#         channel_month_cases[channel][row.month] += cases

#     data_list = list(data_map.values())

#     for d in data_list:
#         d["total_qty"] = round(d["total_qty"], 2)
#         d["total_cases"] = "{:,.2f}".format(d["total_cases"])

#     total_row = {
#         "item_code": "Total",
#         "item_name": "",
#         "customer_group": "",
#         "channel": "",
#         "total_qty": 0.0,
#         "total_cases": 0.0
#     }

#     for m in months:
#         total_qty = raw_qty_totals[m]
#         total_cases = raw_case_totals[m]
#         total_row[f"{m}_qty"] = round(total_qty, 2)
#         total_row[f"{m}_cases"] = "{:,.2f}".format(total_cases)
#         total_row["total_qty"] += total_qty
#         total_row["total_cases"] += total_cases

#     total_row["total_qty"] = round(total_row["total_qty"], 2)
#     total_row["total_cases"] = "{:,.2f}".format(total_row["total_cases"])

#     data_list.append(total_row)

#     datasets = []
#     for channel, month_cases in channel_month_cases.items():
#         data_points = [round(month_cases[m], 2) for m in months]
#         datasets.append({
#             "name": channel,
#             "values": data_points
#         })

#     chart = {
#         "data": {
#             "labels": months,
#             "datasets": datasets
#         },
#         "type": "bar"
#     }

#     return columns, data_list, None, chart


# def get_month_list(from_date, to_date):
#     from datetime import datetime

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

    columns = [
        {"label": "Item Code", "fieldname": "item_code", "fieldtype": "Data", "width": 150},
        {"label": "Item Name", "fieldname": "item_name", "fieldtype": "Data", "width": 200},
        {"label": "Customer Group", "fieldname": "customer_group", "fieldtype": "Data", "width": 180},
        {"label": "Channel", "fieldname": "channel", "fieldtype": "Data", "width": 150},
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

    columns.append({
        "label": "Total Qty",
        "fieldname": "total_qty",
        "fieldtype": "Float",
        "precision": 2,
        "width": 130,
    })
    columns.append({
        "label": "Total Cases",
        "fieldname": "total_cases",
        "fieldtype": "Data",
        "width": 130,
    })

    placeholders = ','.join(['%s'] * len(item_codes))

    query = f"""
        SELECT 
            sii.item_code,
            sii.item_name,
            cust.customer_group,
            custgrp.channel,
            DATE_FORMAT(si.posting_date, '%%b %%Y') as month,
            SUM(sii.qty) as total_qty,
            SUM(sii.cases) as total_cases
        FROM
            `tabSales Invoice` si
        INNER JOIN
            `tabSales Invoice Item` sii ON sii.parent = si.name
        INNER JOIN
            `tabCustomer` cust ON cust.name = si.customer
        LEFT JOIN
            `tabCustomer Group` custgrp ON custgrp.name = cust.customer_group
        WHERE 
            si.docstatus = 1
            AND si.posting_date BETWEEN %s AND %s
            AND sii.item_code IN ({placeholders})
        GROUP BY
            sii.item_code, sii.item_name, cust.customer_group, custgrp.channel, month
        ORDER BY
            sii.item_code, month
    """

    args = [from_date, to_date] + item_codes
    data = frappe.db.sql(query, args, as_dict=True)

    data_map = {}
    raw_case_totals = {m: 0.0 for m in months}
    raw_qty_totals = {m: 0.0 for m in months}
    channel_month_cases = {}

    for row in data:
        key = (row.item_code, row.customer_group or "", row.channel or "")

        if key not in data_map:
            data_map[key] = {
                "item_code": row.item_code,
                "item_name": row.item_name,
                "customer_group": row.customer_group or "",
                "channel": row.channel or ""
            }
            for m in months:
                data_map[key][f"{m}_qty"] = 0.0
                data_map[key][f"{m}_cases"] = "0.00"
            data_map[key]["total_qty"] = 0.0
            data_map[key]["total_cases"] = 0.0

        qty = round(row.total_qty or 0, 2)
        cases = round(row.total_cases or 0, 2)

        data_map[key][f"{row.month}_qty"] = qty
        data_map[key][f"{row.month}_cases"] = "{:,.2f}".format(cases)

        raw_case_totals[row.month] += cases
        raw_qty_totals[row.month] += qty

        data_map[key]["total_qty"] += qty
        data_map[key]["total_cases"] += cases

        channel = row.channel or "Unknown"
        if channel not in channel_month_cases:
            channel_month_cases[channel] = {m: 0.0 for m in months}
        channel_month_cases[channel][row.month] += cases

    data_list = list(data_map.values())

    for d in data_list:
        d["total_qty"] = round(d["total_qty"], 2)
        d["total_cases"] = "{:,.2f}".format(d["total_cases"])

    total_row = {
        "item_code": "Total",
        "item_name": "",
        "customer_group": "",
        "channel": "",
        "total_qty": 0.0,
        "total_cases": 0.0
    }

    for m in months:
        total_qty = raw_qty_totals[m]
        total_cases = raw_case_totals[m]
        total_row[f"{m}_qty"] = round(total_qty, 2)
        total_row[f"{m}_cases"] = "{:,.2f}".format(total_cases)
        total_row["total_qty"] += total_qty
        total_row["total_cases"] += total_cases

    total_row["total_qty"] = round(total_row["total_qty"], 2)
    total_row["total_cases"] = "{:,.2f}".format(total_row["total_cases"])

    data_list.append(total_row)

    # Prepare chart datasets for channels
    channel_datasets = []
    for channel, month_cases in channel_month_cases.items():
        channel_datasets.append({
            "name": channel,
            "values": [round(month_cases[m], 2) for m in months]
        })

    # Add Total Cases dataset after all channels
    channel_datasets.append({
        "name": "Total Cases",
        "values": [round(raw_case_totals[m], 2) for m in months]
    })

    # Final chart
    chart = {
        "data": {
            "labels": months,
            "datasets": channel_datasets
        },
        "type": "bar"
    }

    return columns, data_list, None, chart


def get_month_list(from_date, to_date):
    from datetime import datetime

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
