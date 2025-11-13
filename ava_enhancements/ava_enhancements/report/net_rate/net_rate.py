# Copyright (c) 2025, Furqan Asghar and contributors
# For license information, please see license.txt

# import frappe

# import frappe
# import calendar
# from datetime import datetime
# from dateutil.relativedelta import relativedelta

# def execute(filters=None):
#     if not filters:
#         filters = {}

#     from_date = datetime.strptime(filters.get("from_date"), "%Y-%m-%d")
#     to_date = datetime.strptime(filters.get("to_date"), "%Y-%m-%d")

#     item_list = [
#         "6287016760027", "6287016760034", "6287016760041",
        
#     ]

#     # Generate month-year list (e.g., "Jan 2025", "Feb 2025")
#     month_years = []
#     current = from_date.replace(day=1)
#     while current <= to_date:
#         month_years.append(current.strftime("%b %Y"))
#         current += relativedelta(months=1)

#     # Columns
#     columns = [
#         {"label": "Item Code", "fieldname": "item_code", "fieldtype": "Data", "width": 150},
#         {"label": "Item Name", "fieldname": "item_name", "fieldtype": "Data", "width": 250},
#     ]
#     for month_year in month_years:
#         columns.append({
#             "label": month_year,
#             "fieldname": month_year.lower().replace(" ", "_"),
#             "fieldtype": "Currency",
#             "width": 100
#         })

#     # Get Item Names
#     item_names = frappe._dict({
#         d.name: d.item_name for d in frappe.db.get_all(
#             "Item",
#             filters={"name": ["in", item_list]},
#             fields=["name", "item_name"]
#         )
#     })

#     # Prepare result map
#     result_map = {}
#     for item in item_list:
#         row = {
#             "item_code": item,
#             "item_name": item_names.get(item, "")
#         }
#         for month_year in month_years:
#             row[month_year.lower().replace(" ", "_")] = 0
#         result_map[item] = row

#     # Fetch Stock Ledger Entry data
#     sle_data = frappe.db.sql("""
#         SELECT item_code, posting_date, valuation_rate
#         FROM `tabStock Ledger Entry`
#         WHERE item_code IN %(item_list)s
#           AND posting_date BETWEEN %(from_date)s AND %(to_date)s
#         ORDER BY posting_date DESC
#     """, {
#         "item_list": item_list,
#         "from_date": from_date,
#         "to_date": to_date
#     }, as_dict=True)

#     # Fill in latest valuation rate per month per item
#     filled = set()
#     for row in sle_data:
#         item = row.item_code
#         month_year = row.posting_date.strftime("%b %Y")
#         key = month_year.lower().replace(" ", "_")
#         unique_key = (item, key)
#         if unique_key not in filled:
#             result_map[item][key] = row.valuation_rate
#             filled.add(unique_key)

#     # Final data for report
#     final_data = list(result_map.values())
#     return columns, final_data


import frappe
from datetime import datetime
from dateutil.relativedelta import relativedelta

def execute(filters=None):
    if not filters:
        filters = {}

    from_date = datetime.strptime(filters.get("from_date"), "%Y-%m-%d")
    to_date = datetime.strptime(filters.get("to_date"), "%Y-%m-%d")

    item_list = [
        "6287016760027", "6287016760034", "6287016760041",
    ]

    # Generate month-year list (e.g., "Jan 2025", "Feb 2025")
    month_years = []
    current = from_date.replace(day=1)
    while current <= to_date:
        month_years.append(current.strftime("%b %Y"))
        current += relativedelta(months=1)

    # Columns for the report table
    columns = [
        {"label": "Item Code", "fieldname": "item_code", "fieldtype": "Data", "width": 150},
        {"label": "Item Name", "fieldname": "item_name", "fieldtype": "Data", "width": 250},
    ]
    for month_year in month_years:
        columns.append({
            "label": month_year,
            "fieldname": month_year.lower().replace(" ", "_"),
            "fieldtype": "Currency",
            "width": 100
        })

    # Get Item Names
    item_names = frappe._dict({
        d.name: d.item_name for d in frappe.db.get_all(
            "Item",
            filters={"name": ["in", item_list]},
            fields=["name", "item_name"]
        )
    })

    # Prepare result map with zeroes initially
    result_map = {}
    for item in item_list:
        row = {
            "item_code": item,
            "item_name": item_names.get(item, "")
        }
        for month_year in month_years:
            row[month_year.lower().replace(" ", "_")] = 0
        result_map[item] = row

    # Fetch Stock Ledger Entry data
    sle_data = frappe.db.sql("""
        SELECT item_code, posting_date, valuation_rate
        FROM `tabStock Ledger Entry`
        WHERE item_code IN %(item_list)s
          AND posting_date BETWEEN %(from_date)s AND %(to_date)s
        ORDER BY posting_date DESC
    """, {
        "item_list": item_list,
        "from_date": from_date,
        "to_date": to_date
    }, as_dict=True)

    # Fill in latest valuation rate per month per item
    filled = set()
    for row in sle_data:
        item = row.item_code
        month_year = row.posting_date.strftime("%b %Y")
        key = month_year.lower().replace(" ", "_")
        unique_key = (item, key)
        if unique_key not in filled:
            result_map[item][key] = row.valuation_rate
            filled.add(unique_key)

    # Prepare final data list
    final_data = list(result_map.values())

    # Calculate sum of each month column
    total_row = {
        "item_code": "Total",
        "item_name": "",
    }
    for month_year in month_years:
        key = month_year.lower().replace(" ", "_")
        total_row[key] = sum(row.get(key, 0) for row in final_data)

    # Calculate average of each month column
    avg_row = {
        "item_code": "Average",
        "item_name": "",
    }
    num_items = len(final_data)
    for month_year in month_years:
        key = month_year.lower().replace(" ", "_")
        avg_row[key] = round(total_row[key] / num_items, 2) if num_items else 0

    # Append total and average rows at the end of table data
    final_data.append(total_row)
    final_data.append(avg_row)

    # Prepare chart data for Total and Average per month
    labels = month_years
    datasets = [
        {
            "name": "Total",
            "values": [total_row[month.lower().replace(" ", "_")] for month in month_years]
        },
        {
            "name": "Average",
            "values": [avg_row[month.lower().replace(" ", "_")] for month in month_years]
        }
    ]

    chart = {
        "data": {
            "labels": labels,
            "datasets": datasets
        },
        "type": "bar",  # bar chart
        "fieldtype": "Currency",
        "height": 300,
        "colors": ["#28a745", "#007bff"],  # green for total, blue for average
        "title": "Monthly Total and Average Valuation Rate"
    }

    return columns, final_data, chart
