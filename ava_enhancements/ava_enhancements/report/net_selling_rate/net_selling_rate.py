# Copyright (c) 2025, Furqan Asghar and contributors
# For license information, please see license.txt

# Copyright (c) 2025, Furqan Asghar and contributors
# # For license information, please see license.txt

# import frappe
# from collections import defaultdict
# import calendar

# def execute(filters=None):
#     filters = filters or {}

#     year = filters.get("year")
#     if not year:
#         frappe.throw("Please select a year")

#     columns = get_columns(year)
#     data = get_data(year)

#     return columns, data

# def get_columns(year):
#     columns = [
#         {"label": "Item Code", "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 150},
#         {"label": "Item Name", "fieldname": "item_name", "fieldtype": "Data", "width": 200}
#     ]

#     for month in range(1, 13):
#         month_name = calendar.month_abbr[month]
#         columns.append({
#             "label": f"{month_name} Sales {year}",
#             "fieldname": f"sales_{month}",
#             "fieldtype": "Currency",
#             "width": 120
#         })
#         columns.append({
#             "label": f"{month_name} Cases {year}",
#             "fieldname": f"cases_{month}",
#             "fieldtype": "Float",
#             "width": 100
#         })
#         columns.append({
#             "label": f"{month_name} Rate {year}",
#             "fieldname": f"rate_{month}",
#             "fieldtype": "Float",
#             "precision": 2,
#             "width": 100
#         })

#     columns.append({
#         "label": f"Total Sales {year}",
#         "fieldname": "total_sales",
#         "fieldtype": "Currency",
#         "width": 150
#     })
#     columns.append({
#         "label": f"Total Cases {year}",
#         "fieldname": "total_cases",
#         "fieldtype": "Float",
#         "width": 120
#     })
#     columns.append({
#         "label": f"Total Rate {year}",
#         "fieldname": "total_rate",
#         "fieldtype": "Float",
#         "precision": 2,
#         "width": 120
#     })

#     return columns

# def get_data(year):
#     start_date = f"{year}-01-01"
#     end_date = f"{year}-12-31"

#     item_codes = (
#         '6287016760027', '6287016760034', '6287016760041',
#         '6287016760058', '6287016760119', '6287016760157',
#         '6287016760164'
#     )
#     placeholders = ','.join(['%s'] * len(item_codes))

#     sales_data = frappe.db.sql(f"""
#         SELECT
#             si_item.item_code,
#             si_item.item_name,
#             MONTH(si.posting_date) AS month,
#             SUM(si_item.base_net_amount) AS net_sales,
#             SUM(si_item.qty) AS qty_cases
#         FROM
#             `tabSales Invoice` si
#         JOIN
#             `tabSales Invoice Item` si_item ON si.name = si_item.parent
#         WHERE
#             si.docstatus = 1
#             AND si.posting_date BETWEEN %s AND %s
#             AND si_item.item_code IN ({placeholders})
#         GROUP BY
#             si_item.item_code, si_item.item_name, MONTH(si.posting_date)
#     """, (start_date, end_date, *item_codes), as_dict=True)

#     item_monthly_sales = defaultdict(lambda: {f"sales_{m}": 0 for m in range(1, 13)})
#     item_monthly_cases = defaultdict(lambda: {f"cases_{m}": 0 for m in range(1, 13)})

#     item_names = {}

#     monthly_sales_totals = {f"sales_{m}": 0 for m in range(1, 13)}
#     monthly_cases_totals = {f"cases_{m}": 0 for m in range(1, 13)}

#     grand_total_sales = 0
#     grand_total_cases = 0

#     for row in sales_data:
#         item_code = row.item_code
#         item_name = row.item_name
#         month = row.month

#         net_sales = row.net_sales or 0
#         qty_cases = row.qty_cases or 0

#         item_monthly_sales[item_code][f"sales_{month}"] += net_sales
#         item_monthly_cases[item_code][f"cases_{month}"] += qty_cases

#         item_names[item_code] = item_name

#         monthly_sales_totals[f"sales_{month}"] += net_sales
#         monthly_cases_totals[f"cases_{month}"] += qty_cases

#         grand_total_sales += net_sales
#         grand_total_cases += qty_cases

#     results = []
#     for item_code in item_monthly_sales:
#         row = {
#             "item_code": item_code,
#             "item_name": item_names.get(item_code)
#         }
#         total_sales = 0
#         total_cases = 0

#         for m in range(1, 13):
#             sales_val = item_monthly_sales[item_code].get(f"sales_{m}", 0)
#             cases_val = item_monthly_cases[item_code].get(f"cases_{m}", 0)

#             row[f"sales_{m}"] = sales_val
#             row[f"cases_{m}"] = cases_val

#             if cases_val:
#                 rate = sales_val / cases_val
#             else:
#                 rate = 0
#             row[f"rate_{m}"] = round(rate, 2)

#             total_sales += sales_val
#             total_cases += cases_val

#         row["total_sales"] = total_sales
#         row["total_cases"] = total_cases

#         # Calculate total rate per item safely
#         if total_cases:
#             total_rate = total_sales / total_cases
#         else:
#             total_rate = 0
#         row["total_rate"] = round(total_rate, 2)

#         results.append(row)

#     # Add total row
#     total_row = {
#         "item_code": "<b>Total</b>",
#         "item_name": ""
#     }

#     for m in range(1, 13):
#         total_row[f"sales_{m}"] = monthly_sales_totals[f"sales_{m}"]
#         total_row[f"cases_{m}"] = monthly_cases_totals[f"cases_{m}"]

#         cases_total = monthly_cases_totals[f"cases_{m}"]
#         sales_total = monthly_sales_totals[f"sales_{m}"]
#         if cases_total:
#             total_rate = sales_total / cases_total
#         else:
#             total_rate = 0
#         total_row[f"rate_{m}"] = round(total_rate, 2)

#     total_row["total_sales"] = grand_total_sales
#     total_row["total_cases"] = grand_total_cases
#     if grand_total_cases:
#         total_row["total_rate"] = round(grand_total_sales / grand_total_cases, 2)
#     else:
#         total_row["total_rate"] = 0

#     results.append(total_row)

#     return results


import frappe
from collections import defaultdict
import calendar

def execute(filters=None):
    filters = filters or {}

    year = filters.get("year")
    if not year:
        frappe.throw("Please select a year")

    columns = get_columns(year)
    data = get_data(year)
    chart = get_rate_chart(data, year)

    return columns, data, None, chart

def get_columns(year):
    columns = [
        {"label": "Item Code", "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 150},
        {"label": "Item Name", "fieldname": "item_name", "fieldtype": "Data", "width": 200}
    ]

    for month in range(1, 13):
        month_name = calendar.month_abbr[month]
        columns.append({
            "label": f"{month_name} Sales {year}",
            "fieldname": f"sales_{month}",
            "fieldtype": "Currency",
            "width": 120
        })
        columns.append({
            "label": f"{month_name} Cases {year}",
            "fieldname": f"cases_{month}",
            "fieldtype": "Float",
            "width": 100
        })
        columns.append({
            "label": f"{month_name} Rate {year}",
            "fieldname": f"rate_{month}",
            "fieldtype": "Float",
            "precision": 2,
            "width": 100
        })

    columns.append({
        "label": f"Total Sales {year}",
        "fieldname": "total_sales",
        "fieldtype": "Currency",
        "width": 150
    })
    columns.append({
        "label": f"Total Cases {year}",
        "fieldname": "total_cases",
        "fieldtype": "Float",
        "width": 120
    })
    columns.append({
        "label": f"Total Rate {year}",
        "fieldname": "total_rate",
        "fieldtype": "Float",
        "precision": 2,
        "width": 120
    })

    return columns

def get_data(year):
    start_date = f"{year}-01-01"
    end_date = f"{year}-12-31"

    item_codes = (
        '6287016760027', '6287016760034', '6287016760041',
        '6287016760058', '6287016760119', '6287016760157',
        '6287016760164'
    )
    placeholders = ','.join(['%s'] * len(item_codes))

    sales_data = frappe.db.sql(f"""
        SELECT
            si_item.item_code,
            si_item.item_name,
            MONTH(si.posting_date) AS month,
            SUM(si_item.base_net_amount) AS net_sales,
            SUM(si_item.qty) AS qty_cases
        FROM
            `tabSales Invoice` si
        JOIN
            `tabSales Invoice Item` si_item ON si.name = si_item.parent
        WHERE
            si.docstatus = 1
            AND si.posting_date BETWEEN %s AND %s
            AND si_item.item_code IN ({placeholders})
        GROUP BY
            si_item.item_code, si_item.item_name, MONTH(si.posting_date)
    """, (start_date, end_date, *item_codes), as_dict=True)

    item_monthly_sales = defaultdict(lambda: {f"sales_{m}": 0 for m in range(1, 13)})
    item_monthly_cases = defaultdict(lambda: {f"cases_{m}": 0 for m in range(1, 13)})
    item_names = {}

    monthly_sales_totals = {f"sales_{m}": 0 for m in range(1, 13)}
    monthly_cases_totals = {f"cases_{m}": 0 for m in range(1, 13)}

    grand_total_sales = 0
    grand_total_cases = 0

    for row in sales_data:
        item_code = row.item_code
        item_name = row.item_name
        month = row.month

        net_sales = row.net_sales or 0
        qty_cases = row.qty_cases or 0

        item_monthly_sales[item_code][f"sales_{month}"] += net_sales
        item_monthly_cases[item_code][f"cases_{month}"] += qty_cases

        item_names[item_code] = item_name

        monthly_sales_totals[f"sales_{month}"] += net_sales
        monthly_cases_totals[f"cases_{month}"] += qty_cases

        grand_total_sales += net_sales
        grand_total_cases += qty_cases

    results = []
    for item_code in item_monthly_sales:
        row = {
            "item_code": item_code,
            "item_name": item_names.get(item_code)
        }
        total_sales = 0
        total_cases = 0

        for m in range(1, 13):
            sales_val = item_monthly_sales[item_code].get(f"sales_{m}", 0)
            cases_val = item_monthly_cases[item_code].get(f"cases_{m}", 0)

            row[f"sales_{m}"] = sales_val
            row[f"cases_{m}"] = cases_val

            rate = (sales_val / cases_val) if cases_val else 0
            row[f"rate_{m}"] = round(rate, 2)

            total_sales += sales_val
            total_cases += cases_val

        row["total_sales"] = total_sales
        row["total_cases"] = total_cases
        row["total_rate"] = round(total_sales / total_cases, 2) if total_cases else 0

        results.append(row)

    # Total Row
    total_row = {
        "item_code": "<b>Total</b>",
        "item_name": ""
    }

    for m in range(1, 13):
        total_row[f"sales_{m}"] = monthly_sales_totals[f"sales_{m}"]
        total_row[f"cases_{m}"] = monthly_cases_totals[f"cases_{m}"]

        sales = monthly_sales_totals[f"sales_{m}"]
        cases = monthly_cases_totals[f"cases_{m}"]
        rate = (sales / cases) if cases else 0
        total_row[f"rate_{m}"] = round(rate, 2)

    total_row["total_sales"] = grand_total_sales
    total_row["total_cases"] = grand_total_cases
    total_row["total_rate"] = round(grand_total_sales / grand_total_cases, 2) if grand_total_cases else 0

    results.append(total_row)

    return results

def get_rate_chart(data, year):
    labels = [calendar.month_abbr[m] for m in range(1, 13)] + ['Total']
    datasets = []

    for row in data:
        if row["item_code"] == "<b>Total</b>":
            continue  # Skip total row in bar chart

        values = [row.get(f"rate_{m}", 0) for m in range(1, 13)]
        values.append(row.get("total_rate", 0))

        datasets.append({
            "name": row["item_code"],
            "values": values
        })

    return {
        "data": {
            "labels": labels,
            "datasets": datasets
        },
        "type": "bar",
        "colors": ["#7cd6fd", "#743ee2", "#ffa3ef", "#ffc4aa", "#5e64ff"]
    }
