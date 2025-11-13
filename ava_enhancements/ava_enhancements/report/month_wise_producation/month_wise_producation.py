# Copyright (c) 2025, Furqan Asghar and contributors
# For license information, please see license.txt

# import frappe

# def execute(filters=None):
#     columns = [
#         {"label": "Item Code", "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 150},
#         {"label": "Item Name", "fieldname": "item_name", "fieldtype": "Data", "width": 200}
#     ]

#     months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
#     year = filters.get("year", 2025) if filters else 2025

#     for month in months:
#         columns.extend([
#             {"label": f"{month} {year} Qty", "fieldname": f"{month.lower()}_{year}_qty", "fieldtype": "Float", "width": 120, "precision": 2},
#             {"label": f"{month} {year} Cases", "fieldname": f"{month.lower()}_{year}_cases", "fieldtype": "Float", "width": 120, "precision": 2}
#         ])

#     columns.extend([
#         {"label": f"Total {year} Qty", "fieldname": f"total_{year}_qty", "fieldtype": "Float", "width": 120, "precision": 2},
#         {"label": f"Total {year} Cases", "fieldname": f"total_{year}_cases", "fieldtype": "Float", "width": 120, "precision": 2}
#     ])

#     month_cases = []
#     month_params = []
#     for i, month in enumerate(months, 1):
#         month_cases.extend([
#             f"SUM(CASE WHEN MONTH(se.posting_date) = {i} AND YEAR(se.posting_date) = %s THEN sed.qty ELSE 0 END) AS {month.lower()}_{year}_qty",
#             f"SUM(CASE WHEN MONTH(se.posting_date) = {i} AND YEAR(se.posting_date) = %s THEN sed.cases ELSE 0 END) AS {month.lower()}_{year}_cases"
#         ])
#         month_params.extend([year, year])

#     month_case_sql = ",\n                ".join(month_cases)

#     # Build the query using f-string for static parts and keep %s for parameters
#     query = f"""
#         SELECT * FROM (
#             SELECT
#                 sed.item_code AS item_code,
#                 sed.item_name AS item_name,
#                 {month_case_sql},
#                 SUM(CASE WHEN YEAR(se.posting_date) = %s THEN sed.qty ELSE 0 END) AS total_{year}_qty,
#                 SUM(CASE WHEN YEAR(se.posting_date) = %s THEN sed.cases ELSE 0 END) AS total_{year}_cases
#             FROM
#                 `tabStock Entry` se
#             JOIN
#                 `tabStock Entry Detail` sed ON se.name = sed.parent
#             WHERE
#                 se.stock_entry_type = 'Manufacture'
#                 AND sed.is_finished_item = 1
#                 AND YEAR(se.posting_date) = %s
#                 AND sed.item_code != '104000001'
#                 AND se.docstatus = 1
#             GROUP BY
#                 sed.item_code, sed.item_name

#             UNION ALL

#             SELECT
#                 '<b>Total</b>' AS item_code,
#                 '' AS item_name,
#                 {month_case_sql},
#                 SUM(CASE WHEN YEAR(se.posting_date) = %s THEN sed.qty ELSE 0 END) AS total_{year}_qty,
#                 SUM(CASE WHEN YEAR(se.posting_date) = %s THEN sed.cases ELSE 0 END) AS total_{year}_cases
#             FROM
#                 `tabStock Entry` se
#             JOIN
#                 `tabStock Entry Detail` sed ON se.name = sed.parent
#             WHERE
#                 se.stock_entry_type = 'Manufacture'
#                 AND sed.is_finished_item = 1
#                 AND YEAR(se.posting_date) = %s
#                 AND sed.item_code != '104000001'
#         ) AS final_result
#         ORDER BY
#             CASE
#                 WHEN item_code = '<b>Total</b>' THEN 1
#                 ELSE 0
#             END,
#             item_code
#     """

#     # 24 (main) + 24 (total) + 6 (year filters)
#     params = month_params + month_params + [year, year, year, year, year, year]

#     # Execute query
#     data = frappe.db.sql(query, params, as_dict=True)

#     return columns, data



import frappe

def execute(filters=None):
    # Define columns
    columns = [
        {"label": "Item Code", "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 150},
        {"label": "Item Name", "fieldname": "item_name", "fieldtype": "Data", "width": 200}
    ]

    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    year = filters.get("year", 2025) if filters else 2025

    for month in months:
        columns.extend([
            {"label": f"{month} {year} Qty", "fieldname": f"{month.lower()}_{year}_qty", "fieldtype": "Float", "width": 120, "precision": 2},
            {"label": f"{month} {year} Cases", "fieldname": f"{month.lower()}_{year}_cases", "fieldtype": "Float", "width": 120, "precision": 2}
        ])

    # Add total and average columns
    columns.extend([
        {"label": f"Total {year} Qty", "fieldname": f"total_{year}_qty", "fieldtype": "Float", "width": 120, "precision": 2},
        {"label": f"Total {year} Cases", "fieldname": f"total_{year}_cases", "fieldtype": "Float", "width": 120, "precision": 2},
        {"label": f"Avg {year} Qty", "fieldname": f"avg_{year}_qty", "fieldtype": "Float", "width": 120, "precision": 2},
        {"label": f"Avg {year} Cases", "fieldname": f"avg_{year}_cases", "fieldtype": "Float", "width": 120, "precision": 2}
    ])

    # Build SQL
    month_cases = []
    month_params = []
    for i, month in enumerate(months, 1):
        month_cases.extend([
            f"SUM(CASE WHEN MONTH(se.posting_date) = {i} AND YEAR(se.posting_date) = %s THEN sed.qty ELSE 0 END) AS {month.lower()}_{year}_qty",
            f"SUM(CASE WHEN MONTH(se.posting_date) = {i} AND YEAR(se.posting_date) = %s THEN sed.cases ELSE 0 END) AS {month.lower()}_{year}_cases"
        ])
        month_params.extend([year, year])

    month_case_sql = ",\n                ".join(month_cases)

    query = f"""
        SELECT * FROM (
            SELECT
                sed.item_code AS item_code,
                sed.item_name AS item_name,
                {month_case_sql},
                SUM(CASE WHEN YEAR(se.posting_date) = %s THEN sed.qty ELSE 0 END) AS total_{year}_qty,
                SUM(CASE WHEN YEAR(se.posting_date) = %s THEN sed.cases ELSE 0 END) AS total_{year}_cases,
                0 AS avg_{year}_qty,
                0 AS avg_{year}_cases
            FROM
                `tabStock Entry` se
            JOIN
                `tabStock Entry Detail` sed ON se.name = sed.parent
            WHERE
                se.stock_entry_type = 'Manufacture'
                AND sed.is_finished_item = 1
                AND YEAR(se.posting_date) = %s
                AND sed.item_code != '104000001'
                AND se.docstatus = 1
            GROUP BY
                sed.item_code, sed.item_name

            UNION ALL

            SELECT
                '<b>Total</b>' AS item_code,
                '' AS item_name,
                {month_case_sql},
                SUM(CASE WHEN YEAR(se.posting_date) = %s THEN sed.qty ELSE 0 END) AS total_{year}_qty,
                SUM(CASE WHEN YEAR(se.posting_date) = %s THEN sed.cases ELSE 0 END) AS total_{year}_cases,
                0 AS avg_{year}_qty,
                0 AS avg_{year}_cases
            FROM
                `tabStock Entry` se
            JOIN
                `tabStock Entry Detail` sed ON se.name = sed.parent
            WHERE
                se.stock_entry_type = 'Manufacture'
                AND sed.is_finished_item = 1
                AND YEAR(se.posting_date) = %s
                AND sed.item_code != '104000001'
                AND se.docstatus = 1
        ) AS final_result
        ORDER BY
            CASE WHEN item_code = '<b>Total</b>' THEN 1 ELSE 0 END,
            item_code
    """

    params = month_params + [year, year, year] + month_params + [year, year, year]
    data = frappe.db.sql(query, params, as_dict=True)

    # Calculate avg for total row
    total_row = next((row for row in data if row["item_code"] == "<b>Total</b>"), None)
    if total_row:
        non_zero_months_qty = []
        non_zero_months_cases = []

        for month in months:
            qty = total_row.get(f"{month.lower()}_{year}_qty", 0)
            cases = total_row.get(f"{month.lower()}_{year}_cases", 0)
            if qty > 0:
                non_zero_months_qty.append(qty)
            if cases > 0:
                non_zero_months_cases.append(cases)

        avg_qty = sum(non_zero_months_qty) / len(non_zero_months_qty) if non_zero_months_qty else 0
        avg_cases = sum(non_zero_months_cases) / len(non_zero_months_cases) if non_zero_months_cases else 0

        total_row[f"avg_{year}_qty"] = avg_qty
        total_row[f"avg_{year}_cases"] = avg_cases

    # Chart data
    chart_data = {
        "data": {
            "labels": months + ["Total"],
            "datasets": [
                {
                    "name": f"Total Quantity {year}",
                    "chartType": "bar",
                    "values": []
                },
                {
                    "name": f"Total Cases {year}",
                    "chartType": "bar",
                    "values": []
                }
            ]
        },
        "type": "bar",
        "colors": ["#4CAF50", "#2196F3"],
        "barOptions": {"stacked": False, "spaceRatio": 0.4}
    }

    if total_row:
        for month in months:
            chart_data["data"]["datasets"][0]["values"].append(total_row.get(f"{month.lower()}_{year}_qty", 0))
            chart_data["data"]["datasets"][1]["values"].append(total_row.get(f"{month.lower()}_{year}_cases", 0))

        # Append totals
        chart_data["data"]["datasets"][0]["values"].append(total_row.get(f"total_{year}_qty", 0))
        chart_data["data"]["datasets"][1]["values"].append(total_row.get(f"total_{year}_cases", 0))

        # Title with accounting formatting
        chart_data["title"] = (
            f"Monthly + Total & Avg Manufactured Qty & Cases - {year} | "
            f"Total Qty: {format(total_row[f'total_{year}_qty'], ',.2f')}, "
            f"Total Cases: {format(total_row[f'total_{year}_cases'], ',.2f')} | "
            f"Avg Qty: {format(total_row[f'avg_{year}_qty'], ',.2f')}, "
            f"Avg Cases: {format(total_row[f'avg_{year}_cases'], ',.2f')}"
        )

    return columns, data, None, chart_data