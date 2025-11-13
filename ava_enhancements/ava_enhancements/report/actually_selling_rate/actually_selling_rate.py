# Copyright (c) 2025, Furqan Asghar and contributors
# For license information, please see license.txt

# import frappe

def execute(filters=None):
	columns, data = [], []
	return columns, data


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
    return columns, data

def get_columns(year):
    months = [calendar.month_abbr[m] for m in range(1, 13)]  # Jan, Feb, ...
    columns = [
        {"label": "Item Code", "fieldname": "item_code", "fieldtype": "Data", "width": 140},
        {"label": "Item Name", "fieldname": "item_name", "fieldtype": "Data", "width": 250},
    ]
    for m in months:
        col_prefix = m.lower()
        columns.append({"label": f"{m} Sales", "fieldname": f"{col_prefix}_sales", "fieldtype": "Currency", "width": 100})
        columns.append({"label": f"{m} Qty", "fieldname": f"{col_prefix}_qty", "fieldtype": "Float", "width": 80})
        columns.append({"label": f"{m} Rate", "fieldname": f"{col_prefix}_rate", "fieldtype": "Currency", "width": 80})
        columns.append({"label": f"{m} Discount Rate", "fieldname": f"{col_prefix}_discount_rate", "fieldtype": "Float", "width": 110})
        columns.append({"label": f"{m} Net Rate", "fieldname": f"{col_prefix}_net_rate", "fieldtype": "Float", "width": 110})
    columns += [
        {"label": "Total Sales", "fieldname": "total_sales", "fieldtype": "Currency", "width": 110},
        {"label": "Total Qty", "fieldname": "total_qty", "fieldtype": "Float", "width": 90},
        {"label": "Total Rate", "fieldname": "total_rate", "fieldtype": "Currency", "width": 90},
    ]
    return columns

def get_data(year):
    start_date = f"{year}-01-01"
    end_date = f"{year}-12-31"

    item_codes = (
        '6287016760027', '6287016760041', '6287016760034',
        '6287016760058', '6287016760119', '6287016760157', '6287016760164'
    )

    deduction_accounts = {
        "REBATE": "41010105 - Sales Rebate/Trade Discount -حسم المبيعات /الخصم التجاري - ABNA",
        "REG_FEES": "516101 - Registerion Fees -رسوم التسجيل - ABNA",
        "LIST_FEES": "516102 - Listing Fees -رسوم أدخال اصناف - ABNA",
        "FLYER_FEES": "516107 - Flyer Fees -رسوم فلاير - ABNA",
        "DISC_ALLOW": "41010103 - Discount Allowance -الخصم المسموح به - ABNA"
    }

    months = range(1, 13)
    sales_data = defaultdict(lambda: defaultdict(lambda: {"sales": 0, "qty": 0}))
    totals_sales = defaultdict(float)
    totals_qty = defaultdict(float)

    sales_results = frappe.db.sql("""
        SELECT
            sii.item_code,
            sii.item_name,
            MONTH(si.posting_date) AS month,
            SUM(sii.qty) AS total_qty,
            SUM(sii.base_net_amount) AS total_sales
        FROM `tabSales Invoice` si
        JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
        WHERE
            si.docstatus = 1
            AND si.posting_date BETWEEN %s AND %s
            AND sii.item_code IN %s
        GROUP BY sii.item_code, month
    """, (start_date, end_date, item_codes), as_dict=True)

    for r in sales_results:
        sales_data[r.item_code][r.month]["sales"] += r.total_sales or 0
        sales_data[r.item_code][r.month]["qty"] += r.total_qty or 0
        sales_data[r.item_code]["item_name"] = r.item_name

    def get_gl_monthly(account):
        gl_rows = frappe.db.sql("""
            SELECT MONTH(posting_date) AS month, SUM(debit - credit) AS amount
            FROM `tabGL Entry`
            WHERE account = %s AND posting_date BETWEEN %s AND %s
            GROUP BY month
        """, (account, start_date, end_date), as_dict=True)
        return {row.month: row.amount or 0 for row in gl_rows}

    monthly_deductions = {code: get_gl_monthly(account) for code, account in deduction_accounts.items()}

    total_deduct_monthly = {}
    for m in months:
        total_deduct_monthly[m] = sum(monthly_deductions[code].get(m, 0) for code in deduction_accounts)

    # Calculate overall discount rate per month = total deduction / total qty of all items
    discount_rate_per_month = {}
    for m in months:
        total_qty_month = 0
        for item_code in sales_data:
            total_qty_month += sales_data[item_code][m]["qty"]
        if total_qty_month:
            discount_rate_per_month[m] = total_deduct_monthly.get(m, 0) / total_qty_month
        else:
            discount_rate_per_month[m] = 0

    data = []
    all_items = list(sales_data.keys())

    for item_code in all_items:
        row = {
            "item_code": item_code,
            "item_name": sales_data[item_code].get("item_name", ""),
        }
        total_sales_sum = 0
        total_qty_sum = 0

        for m in months:
            m_abbr = calendar.month_abbr[m].lower()
            sales = sales_data[item_code][m]["sales"]
            qty = sales_data[item_code][m]["qty"]
            rate = (sales / qty) if qty else 0

            totals_sales[m] += sales
            totals_qty[m] += qty

            discount_rate = discount_rate_per_month.get(m, 0)
            net_rate = rate - discount_rate

            row[f"{m_abbr}_sales"] = round(sales, 2)
            row[f"{m_abbr}_qty"] = round(qty, 2)
            row[f"{m_abbr}_rate"] = round(rate, 2)
            row[f"{m_abbr}_discount_rate"] = round(discount_rate, 4)
            row[f"{m_abbr}_net_rate"] = round(net_rate, 4)

            total_sales_sum += sales
            total_qty_sum += qty

        total_rate = (total_sales_sum / total_qty_sum) if total_qty_sum else 0
        total_discount = sum(discount_rate_per_month.get(m, 0) for m in months) / 12  # Average discount rate for year
        total_net_rate = total_rate - total_discount

        row["total_sales"] = round(total_sales_sum, 2)
        row["total_qty"] = round(total_qty_sum, 2)
        row["total_rate"] = round(total_rate, 2)
        row["total_net_rate"] = round(total_net_rate, 4)
        data.append(row)

    # Total row
    total_row = {
        "item_code": "TOTAL",
        "item_name": "Total of All Items"
    }
    total_sales_sum_all = 0
    total_qty_sum_all = 0
    for m in months:
        m_abbr = calendar.month_abbr[m].lower()
        sales = totals_sales[m]
        qty = totals_qty[m]
        rate = (sales / qty) if qty else 0
        discount_rate = discount_rate_per_month.get(m, 0)
        net_rate = rate - discount_rate

        total_row[f"{m_abbr}_sales"] = round(sales, 2)
        total_row[f"{m_abbr}_qty"] = round(qty, 2)
        total_row[f"{m_abbr}_rate"] = round(rate, 2)
        total_row[f"{m_abbr}_discount_rate"] = round(discount_rate, 4)
        total_row[f"{m_abbr}_net_rate"] = round(net_rate, 4)

        total_sales_sum_all += sales
        total_qty_sum_all += qty

    total_row["total_sales"] = round(total_sales_sum_all, 2)
    total_row["total_qty"] = round(total_qty_sum_all, 2)
    total_row["total_rate"] = round((total_sales_sum_all / total_qty_sum_all) if total_qty_sum_all else 0, 2)
    total_row["total_net_rate"] = round(total_row["total_rate"] - (sum(discount_rate_per_month.values())/12), 4)
    data.append(total_row)

    # Deduction rows
    def make_deduction_row(code, name, monthly_data):
        row = {
            "item_code": code,
            "item_name": name,
        }
        total_amt = 0
        for m in months:
            m_abbr = calendar.month_abbr[m].lower()
            amt = monthly_data.get(m, 0)
            row[f"{m_abbr}_sales"] = round(amt, 2)
            row[f"{m_abbr}_qty"] = 0
            row[f"{m_abbr}_rate"] = 0
            row[f"{m_abbr}_discount_rate"] = 0
            row[f"{m_abbr}_net_rate"] = 0
            total_amt += amt
        row["total_sales"] = round(total_amt, 2)
        row["total_qty"] = 0
        row["total_rate"] = 0
        row["total_net_rate"] = 0
        return row

    for code, monthly in monthly_deductions.items():
        data.append(make_deduction_row(code, code.replace("_", " ").title(), monthly))

    data.append(make_deduction_row("TOTAL_DEDUCT", "Total Deductions (All)", total_deduct_monthly))

    # Discount Rate summary row
    discount_rate_row = {
        "item_code": "DISCOUNT_RATE",
        "item_name": "Discount Rate = Total Deduct / Total Qty",
    }
    for m in months:
        m_abbr = calendar.month_abbr[m].lower()
        val = discount_rate_per_month.get(m, 0)
        discount_rate_row[f"{m_abbr}_sales"] = round(val, 4)
        discount_rate_row[f"{m_abbr}_qty"] = 0
        discount_rate_row[f"{m_abbr}_rate"] = 0
        discount_rate_row[f"{m_abbr}_discount_rate"] = 0
        discount_rate_row[f"{m_abbr}_net_rate"] = 0
    discount_rate_row["total_sales"] = 0
    discount_rate_row["total_qty"] = 0
    discount_rate_row["total_rate"] = 0
    discount_rate_row["total_net_rate"] = 0
    data.append(discount_rate_row)

    return data