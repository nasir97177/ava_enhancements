# import frappe
# from datetime import datetime

# def execute(filters=None):
#     filters = filters or {}

#     from_date = filters.get('from_date')
#     to_date = filters.get('to_date')

#     if not from_date or not to_date:
#         frappe.throw("Please set From Date and To Date")

#     item_codes = [
#         '6287016760027', '6287016760034', '6287016760041',
#         '6287016760058', '6287016760119', '6287016760157',
#         '6287016760164',
#     ]

#     months = get_month_list(from_date, to_date)

#     columns = [
#         {"label": "Item Code", "fieldname": "item_code", "fieldtype": "Data", "width": 150},
#         {"label": "Item Name", "fieldname": "item_name", "fieldtype": "Data", "width": 200},
#         {"label": "Warehouse", "fieldname": "warehouse", "fieldtype": "Data", "width": 200},
#         {"label": "Branch", "fieldname": "branch", "fieldtype": "Data", "width": 150},
#     ]

#     for m in months:
#         columns.append({"label": f"{m} Qty", "fieldname": f"{m}_qty", "fieldtype": "Float", "precision": 2, "width": 120})
#         columns.append({"label": f"{m} Cases", "fieldname": f"{m}_cases", "fieldtype": "Float", "precision": 2, "width": 130})

#     placeholders = ','.join(['%s'] * len(item_codes))

#     query = f"""
#         SELECT 
#             sii.item_code, sii.item_name, sii.warehouse,
#             DATE_FORMAT(si.posting_date, '%%b %%Y') as month,
#             SUM(sii.qty) as total_qty, SUM(sii.cases) as total_cases
#         FROM `tabSales Invoice` si
#         INNER JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
#         WHERE si.docstatus = 1
#             AND si.posting_date BETWEEN %s AND %s
#             AND sii.item_code IN ({placeholders})
#         GROUP BY sii.item_code, sii.item_name, sii.warehouse, month
#         ORDER BY sii.item_code, sii.warehouse, month
#     """

#     args = [from_date, to_date] + item_codes
#     data = frappe.db.sql(query, args, as_dict=True)

#     dammam_warehouses = [
#         "D-1 - ABNA", "D-2 - ABNA", "D-5 - ABNA", "D-7 - ABNA",
#         "Finished Goods-DMM - ABNA", "Quality Control Damage -DMM  - ABNA"
#     ]
#     jeddah_warehouses = [
#         "Finished Goods-JED - ABNA", "J-1 - ABNA", "J-2 - ABNA", "J-3 - ABNA", "J-4 - ABNA",
#         "J-5 - ABNA", "J-6 - ABNA", "J-7 - ABNA", "Quality Control Damage -JED  - ABNA"
#     ]
#     riyadh_warehouses = [
#         "Finished Goods-RYD - ABNA", "Quality Control Damage -RYD  - ABNA",
#         "R-1-ABNA", "R-2 - ABNA", "R-3 - ABNA", "R-4 - ABNA", "R-5 - ABNA", "R-6 - ABNA",
#         "R-7 -ABNA", "R-8 - ABNA", "R-9 - ABNA", "R-10 - ABNA", "R-11 - ABNA", "R-12 - ABNA",
#         "R-13 - ABNA", "R-14 - ABNA", "R-15- ABNA", "R-16 - ABNA", "R-17 - ABNA",
#         "R-18 - ABNA", "R-19 - ABNA"
#     ]
#     factory_warehouses = [
#         "Distributor Warehouse - ABNA", "Finished Goods-Central Warehouse - ABNA"
#     ]

#     data_map = {}
#     raw_case_totals = {m: 0.0 for m in months}
#     raw_qty_totals = {m: 0.0 for m in months}

#     for row in data:
#         key = (row.item_code, row.warehouse)
#         if key not in data_map:
#             if row.warehouse in dammam_warehouses:
#                 branch = "Dammam"
#             elif row.warehouse in jeddah_warehouses:
#                 branch = "Jeddah"
#             elif row.warehouse in riyadh_warehouses:
#                 branch = "Riyadh"
#             elif row.warehouse in factory_warehouses:
#                 branch = "Factory"
#             else:
#                 branch = "Unknown"

#             data_map[key] = {
#                 "item_code": row.item_code,
#                 "item_name": row.item_name,
#                 "warehouse": row.warehouse,
#                 "branch": branch,
#             }
#             for m in months:
#                 data_map[key][f"{m}_qty"] = 0.0
#                 data_map[key][f"{m}_cases"] = 0.0

#         qty = round(row.total_qty or 0, 2)
#         cases = round(row.total_cases or 0, 2)

#         data_map[key][f"{row.month}_qty"] = qty
#         data_map[key][f"{row.month}_cases"] = cases

#         raw_case_totals[row.month] += cases
#         raw_qty_totals[row.month] += qty

#     data_list = list(data_map.values())

#     total_row = {
#         "item_code": "Total", "item_name": "", "warehouse": "", "branch": "",
#     }

#     chart_case_values = []
#     chart_qty_values = []

#     for m in months:
#         total_qty = raw_qty_totals[m]
#         total_cases = raw_case_totals[m]
#         total_row[f"{m}_qty"] = round(total_qty, 2)
#         total_row[f"{m}_cases"] = round(total_cases, 2)
#         chart_case_values.append(round(total_cases, 2))
#         chart_qty_values.append(round(total_qty, 2))

#     data_list.append(total_row)

#     # Branch-wise monthly case distribution
#     branch_month_case_map = {}
#     branch_list = set()

#     for row in data_list:
#         branch = row.get("branch")
#         if not branch or branch == "Total":
#             continue
#         branch_list.add(branch)
#         for m in months:
#             key = (branch, m)
#             if key not in branch_month_case_map:
#                 branch_month_case_map[key] = 0.0
#             branch_month_case_map[key] += row.get(f"{m}_cases", 0.0)

#     branch_list = sorted(list(branch_list))

#     chart_datasets = []
#     for branch in branch_list:
#         dataset = {
#             "name": branch,
#             "values": [round(branch_month_case_map.get((branch, m), 0.0), 2) for m in months]
#         }
#         chart_datasets.append(dataset)

#     chart = {
#         "data": {
#             "labels": months,
#             "datasets": chart_datasets
#         },
#         "type": "bar",
#         "colors": ["#5e64ff", "#ff5858", "#36cfc9", "#ffa940", "#9b59b6", "#1abc9c"],
#         "title": "Branch-wise Monthly Case Distribution",
#         "height": 500,
#         "width": 1000
#     }

#     # Summary Box
#     months_with_data = [v for v in chart_case_values if v > 0]
#     total_cases_sum = sum(chart_case_values)
#     avg_cases = (sum(months_with_data) / len(months_with_data)) if months_with_data else 0

#     total_cases_formatted = "{:,.2f}".format(total_cases_sum)
#     avg_cases_formatted = "{:,.2f}".format(avg_cases)

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
#         '6287016760027', '6287016760034', '6287016760041',
#         '6287016760058', '6287016760119', '6287016760157',
#         '6287016760164',
#     ]

#     months = get_month_list(from_date, to_date)

#     columns = [
#         {"label": "Item Code", "fieldname": "item_code", "fieldtype": "Data", "width": 150},
#         {"label": "Item Name", "fieldname": "item_name", "fieldtype": "Data", "width": 200},
#         {"label": "Warehouse", "fieldname": "warehouse", "fieldtype": "Data", "width": 200},
#         {"label": "Branch", "fieldname": "branch", "fieldtype": "Data", "width": 150},
#     ]

#     # Add monthly qty and cases columns
#     for m in months:
#         columns.append({"label": f"{m} Qty", "fieldname": f"{m}_qty", "fieldtype": "Float", "precision": 2, "width": 120})
#         columns.append({"label": f"{m} Cases", "fieldname": f"{m}_cases", "fieldtype": "Float", "precision": 2, "width": 130})

#     # Add Total Qty and Total Cases columns at the end
#     columns.append({"label": "Total Qty", "fieldname": "total_qty", "fieldtype": "Float", "precision": 2, "width": 120})
#     columns.append({"label": "Total Cases", "fieldname": "total_cases", "fieldtype": "Float", "precision": 2, "width": 130})

#     placeholders = ','.join(['%s'] * len(item_codes))

#     query = f"""
#         SELECT 
#             sii.item_code, sii.item_name, sii.warehouse,
#             DATE_FORMAT(si.posting_date, '%%b %%Y') as month,
#             SUM(sii.qty) as total_qty, SUM(sii.cases) as total_cases
#         FROM `tabSales Invoice` si
#         INNER JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
#         WHERE si.docstatus = 1
#             AND si.posting_date BETWEEN %s AND %s
#             AND sii.item_code IN ({placeholders})
#         GROUP BY sii.item_code, sii.item_name, sii.warehouse, month
#         ORDER BY sii.item_code, sii.warehouse, month
#     """

#     args = [from_date, to_date] + item_codes
#     data = frappe.db.sql(query, args, as_dict=True)

#     dammam_warehouses = [
#         "D-1 - ABNA", "D-2 - ABNA", "D-5 - ABNA", "D-7 - ABNA",
#         "Finished Goods-DMM - ABNA", "Quality Control Damage -DMM  - ABNA"
#     ]
#     jeddah_warehouses = [
#         "Finished Goods-JED - ABNA", "J-1 - ABNA", "J-2 - ABNA", "J-3 - ABNA", "J-4 - ABNA",
#         "J-5 - ABNA", "J-6 - ABNA", "J-7 - ABNA", "Quality Control Damage -JED  - ABNA"
#     ]
#     riyadh_warehouses = [
#         "Finished Goods-RYD - ABNA", "Quality Control Damage -RYD  - ABNA",
#         "R-1-ABNA", "R-2 - ABNA", "R-3 - ABNA", "R-4 - ABNA", "R-5 - ABNA", "R-6 - ABNA",
#         "R-7 -ABNA", "R-8 - ABNA", "R-9 - ABNA", "R-10 - ABNA", "R-11 - ABNA", "R-12 - ABNA",
#         "R-13 - ABNA", "R-14 - ABNA", "R-15- ABNA", "R-16 - ABNA", "R-17 - ABNA",
#         "R-18 - ABNA", "R-19 - ABNA"
#     ]
#     factory_warehouses = [
#         "Distributor Warehouse - ABNA", "Finished Goods-Central Warehouse - ABNA"
#     ]

#     data_map = {}
#     raw_case_totals = {m: 0.0 for m in months}
#     raw_qty_totals = {m: 0.0 for m in months}

#     for row in data:
#         key = (row.item_code, row.warehouse)
#         if key not in data_map:
#             if row.warehouse in dammam_warehouses:
#                 branch = "Dammam"
#             elif row.warehouse in jeddah_warehouses:
#                 branch = "Jeddah"
#             elif row.warehouse in riyadh_warehouses:
#                 branch = "Riyadh"
#             elif row.warehouse in factory_warehouses:
#                 branch = "Factory"
#             else:
#                 branch = "Unknown"

#             data_map[key] = {
#                 "item_code": row.item_code,
#                 "item_name": row.item_name,
#                 "warehouse": row.warehouse,
#                 "branch": branch,
#             }
#             for m in months:
#                 data_map[key][f"{m}_qty"] = 0.0
#                 data_map[key][f"{m}_cases"] = 0.0

#         qty = round(row.total_qty or 0, 2)
#         cases = round(row.total_cases or 0, 2)

#         data_map[key][f"{row.month}_qty"] = qty
#         data_map[key][f"{row.month}_cases"] = cases

#         raw_case_totals[row.month] += cases
#         raw_qty_totals[row.month] += qty

#     # Calculate total qty and cases per item & warehouse (sum of all months)
#     for key, row in data_map.items():
#         total_qty = sum(row[f"{m}_qty"] for m in months)
#         total_cases = sum(row[f"{m}_cases"] for m in months)
#         row["total_qty"] = round(total_qty, 2)
#         row["total_cases"] = round(total_cases, 2)

#     data_list = list(data_map.values())

#     total_row = {
#         "item_code": "Total", "item_name": "", "warehouse": "", "branch": "",
#     }

#     chart_case_values = []
#     chart_qty_values = []

#     total_qty_per_month = []
#     total_cases_per_month = []

#     for m in months:
#         total_qty = raw_qty_totals[m]
#         total_cases = raw_case_totals[m]
#         total_row[f"{m}_qty"] = round(total_qty, 2)
#         total_row[f"{m}_cases"] = round(total_cases, 2)
#         chart_case_values.append(round(total_cases, 2))
#         chart_qty_values.append(round(total_qty, 2))
#         total_qty_per_month.append(round(total_qty, 2))
#         total_cases_per_month.append(round(total_cases, 2))

#     # Sum totals for Total Qty and Total Cases columns in total_row
#     total_row["total_qty"] = round(sum(total_qty_per_month), 2)
#     total_row["total_cases"] = round(sum(total_cases_per_month), 2)

#     data_list.append(total_row)

#     # Branch-wise monthly case distribution
#     branch_month_case_map = {}
#     branch_list = set()

#     for row in data_list:
#         branch = row.get("branch")
#         if not branch or branch == "Total":
#             continue
#         branch_list.add(branch)
#         for m in months:
#             key = (branch, m)
#             if key not in branch_month_case_map:
#                 branch_month_case_map[key] = 0.0
#             branch_month_case_map[key] += row.get(f"{m}_cases", 0.0)

#     branch_list = sorted(list(branch_list))

#     chart_datasets = []
#     for branch in branch_list:
#         dataset = {
#             "name": branch,
#             "values": [round(branch_month_case_map.get((branch, m), 0.0), 2) for m in months]
#         }
#         chart_datasets.append(dataset)

#     # Add Total Cases dataset to the chart
#     chart_datasets.append({
#         "name": "Total Cases",
#         "values": total_cases_per_month,
#         "color": "#34495e"
#     })

#     chart = {
#         "data": {
#             "labels": months,
#             "datasets": chart_datasets
#         },
#         "type": "bar",
#         "colors": ["#5e64ff", "#ff5858", "#36cfc9", "#ffa940", "#9b59b6", "#1abc9c", "#34495e"],
#         "title": "Branch-wise Monthly Case Distribution with Total Cases",
#         "height": 500,
#         "width": 1000
#     }

#     # Summary Box
#     months_with_data = [v for v in chart_case_values if v > 0]
#     total_cases_sum = sum(chart_case_values)
#     avg_cases = (sum(months_with_data) / len(months_with_data)) if months_with_data else 0

#     total_cases_formatted = "{:,.2f}".format(total_cases_sum)
#     avg_cases_formatted = "{:,.2f}".format(avg_cases)

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
        '6287016760027', '6287016760034', '6287016760041',
        '6287016760058', '6287016760119', '6287016760157',
        '6287016760164',
    ]

    months = get_month_list(from_date, to_date)

    columns = [
        {"label": "Item Code", "fieldname": "item_code", "fieldtype": "Data", "width": 150},
        {"label": "Item Name", "fieldname": "item_name", "fieldtype": "Data", "width": 200},
        {"label": "Warehouse", "fieldname": "warehouse", "fieldtype": "Data", "width": 200},
        {"label": "Branch", "fieldname": "branch", "fieldtype": "Data", "width": 150},
    ]

    # Add monthly qty and cases columns
    for m in months:
        columns.append({"label": f"{m} Qty", "fieldname": f"{m}_qty", "fieldtype": "Float", "precision": 2, "width": 120})
        columns.append({"label": f"{m} Cases", "fieldname": f"{m}_cases", "fieldtype": "Float", "precision": 2, "width": 130})

    # Add Total Qty and Total Cases columns at the end
    columns.append({"label": "Total Qty", "fieldname": "total_qty", "fieldtype": "Float", "precision": 2, "width": 120})
    columns.append({"label": "Total Cases", "fieldname": "total_cases", "fieldtype": "Float", "precision": 2, "width": 130})

    placeholders = ','.join(['%s'] * len(item_codes))

    query = f"""
        SELECT 
            sii.item_code, sii.item_name, sii.warehouse,
            DATE_FORMAT(si.posting_date, '%%b %%Y') as month,
            SUM(sii.qty) as total_qty, SUM(sii.cases) as total_cases
        FROM `tabSales Invoice` si
        INNER JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
        WHERE si.docstatus = 1
            AND si.posting_date BETWEEN %s AND %s
            AND sii.item_code IN ({placeholders})
        GROUP BY sii.item_code, sii.item_name, sii.warehouse, month
        ORDER BY sii.item_code, sii.warehouse, month
    """

    args = [from_date, to_date] + item_codes
    data = frappe.db.sql(query, args, as_dict=True)

    dammam_warehouses = [
        "D-1 - ABNA", "D-2 - ABNA","D-3 - ABNA","D-4 - ABNA","D-5 - ABNA","D-6 - ABNA", "D-7 - ABNA",
        "Finished Goods-DMM - ABNA", "Quality Control Damage -DMM  - ABNA"
    ]
    jeddah_warehouses = [
        "Finished Goods-JED - ABNA", "J-1 - ABNA", "J-2 - ABNA", "J-3 - ABNA", "J-4 - ABNA",
        "J-5 - ABNA", "J-6 - ABNA", "J-7 - ABNA","J-8 - ABNA","J-9 - ABNA","J-10 - ABNA","J-11 - ABNA", "Quality Control Damage -JED  - ABNA"
    ]
    riyadh_warehouses = [
        "Finished Goods-RYD - ABNA", "Quality Control Damage -RYD  - ABNA",
        "R-1-ABNA", "R-2 - ABNA", "R-3 - ABNA", "R-4 - ABNA", "R-5 - ABNA", "R-6 - ABNA",
        "R-7 -ABNA", "R-8 - ABNA", "R-9 - ABNA", "R-10 - ABNA", "R-11 - ABNA", "R-12 - ABNA",
        "R-13 - ABNA", "R-14 - ABNA", "R-15- ABNA", "R-16 - ABNA", "R-17 - ABNA",
        "R-18 - ABNA", "R-19 - ABNA"
    ]
    factory_warehouses = [
        "Distributor Warehouse - ABNA", "Finished Goods-Central Warehouse - ABNA"
    ]

    data_map = {}
    raw_case_totals = {m: 0.0 for m in months}
    raw_qty_totals = {m: 0.0 for m in months}

    for row in data:
        key = (row.item_code, row.warehouse)
        if key not in data_map:
            if row.warehouse in dammam_warehouses:
                branch = "Dammam"
            elif row.warehouse in jeddah_warehouses:
                branch = "Jeddah"
            elif row.warehouse in riyadh_warehouses:
                branch = "Riyadh"
            elif row.warehouse in factory_warehouses:
                branch = "Factory"
            else:
                branch = "Unknown"

            data_map[key] = {
                "item_code": row.item_code,
                "item_name": row.item_name,
                "warehouse": row.warehouse,
                "branch": branch,
            }
            for m in months:
                data_map[key][f"{m}_qty"] = 0.0
                data_map[key][f"{m}_cases"] = 0.0

        qty = round(row.total_qty or 0, 2)
        cases = round(row.total_cases or 0, 2)

        data_map[key][f"{row.month}_qty"] = qty
        data_map[key][f"{row.month}_cases"] = cases

        raw_case_totals[row.month] += cases
        raw_qty_totals[row.month] += qty

    # Calculate total qty and cases per item & warehouse (sum of all months)
    for key, row in data_map.items():
        total_qty = sum(row[f"{m}_qty"] for m in months)
        total_cases = sum(row[f"{m}_cases"] for m in months)
        row["total_qty"] = round(total_qty, 2)
        row["total_cases"] = round(total_cases, 2)

    data_list = list(data_map.values())

    total_row = {
        "item_code": "Total", "item_name": "", "warehouse": "", "branch": "",
    }

    chart_case_values = []
    chart_qty_values = []

    total_qty_per_month = []
    total_cases_per_month = []

    for m in months:
        total_qty = raw_qty_totals[m]
        total_cases = raw_case_totals[m]
        total_row[f"{m}_qty"] = round(total_qty, 2)
        total_row[f"{m}_cases"] = round(total_cases, 2)
        chart_case_values.append(round(total_cases, 2))
        chart_qty_values.append(round(total_qty, 2))
        total_qty_per_month.append(round(total_qty, 2))
        total_cases_per_month.append(round(total_cases, 2))

    # Sum totals for Total Qty and Total Cases columns in total_row
    total_row["total_qty"] = round(sum(total_qty_per_month), 2)
    total_row["total_cases"] = round(sum(total_cases_per_month), 2)

    data_list.append(total_row)

    # Branch-wise monthly case distribution
    branch_month_case_map = {}
    branch_list = set()

    for row in data_list:
        branch = row.get("branch")
        if not branch or branch == "Total":
            continue
        branch_list.add(branch)
        for m in months:
            key = (branch, m)
            if key not in branch_month_case_map:
                branch_month_case_map[key] = 0.0
            branch_month_case_map[key] += row.get(f"{m}_cases", 0.0)

    branch_list = sorted(list(branch_list))

    chart_datasets = []
    for branch in branch_list:
        dataset = {
            "name": branch,
            "values": [round(branch_month_case_map.get((branch, m), 0.0), 2) for m in months]
        }
        chart_datasets.append(dataset)

    # Add Total Cases dataset to the chart
    # chart_datasets.append({
    #     "name": "Total Cases",
    #     "values": total_cases_per_month,
    #     "color": "#34495e"
    # })

    # Calculate sum and average of cases for title
    months_with_data = [v for v in chart_case_values if v > 0]
    total_cases_sum = sum(chart_case_values)
    avg_cases = (sum(months_with_data) / len(months_with_data)) if months_with_data else 0

    total_cases_formatted = "{:,.2f}".format(total_cases_sum)
    avg_cases_formatted = "{:,.2f}".format(avg_cases)

    chart_title = f"Branch-wise Monthly Total Cases (Sum: {total_cases_formatted}, Avg: {avg_cases_formatted})"

    chart = {
        "data": {
            "labels": months,
            "datasets": chart_datasets
        },
        "type": "bar",
        "colors": ["#5e64ff", "#ff5858", "#36cfc9", "#ffa940", "#9b59b6", "#1abc9c", "#34495e"],
        "title": chart_title,
        "height": 500,
        "width": 1000
    }

    # Summary Box HTML
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

    # Return columns, data, summary box HTML, and chart config
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
