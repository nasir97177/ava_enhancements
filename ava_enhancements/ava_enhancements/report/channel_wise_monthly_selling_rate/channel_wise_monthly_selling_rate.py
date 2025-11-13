# # import frappe
# # from collections import defaultdict
# # import calendar

# # CHANNEL_MAPPING = {
# #     "DIRECT DISTRIBUTION DD": [
# #         "EATRIES", "LARGE GROCERY", "MINIMARKET", "SMALL GROCERY",
# #         "SUPERMARKET B", "WATER SHOP", "DIRECT DISTRIBUTION DD"
# #     ],
# #     "DISTRIBUTOR": [
# #         "DISTRIBUTOR A", "DISTRIBUTOR B", "DISTRIBUTOR C", "DISTRIBUTOR"
# #     ],
# #     "HOME DELIVERY HD": [
# #         "HOUSE", "MOSQUE", "OFFICE", "SCHOOL", "HOME DELIVERY HD"
# #     ],
# #     "HORECA HO": [
# #         "CAFÉ", "CARE", "CATERING", "COMMERCIAL", "GOVERNMENTAL",
# #         "HOTEL", "INSTITUTIONAL", "RESTAURANT", "HORECA HO", "CAFE"
# #     ],
# #     "KEY ACCOUNT KA": [
# #         "E-COMMERCE", "HYPERMARKET", "SUPERMARKET-A", "SUPERMARKET-B", "KEY ACCOUNT  KA"
# #     ],
# #     "MARKETING": [
# #         "MARKETING", "DONATION", "EVENT", "SPONSORSHIP"
# #     ],
# #     "OTHER MISCELLANEOUS": [
# #         "OTHER MISCELLANEOUS", "OTHER  MISCELLANEOUS"
# #     ],
# #     "WHOLESALE": [
# #         "WHOLESALE WS", "WAREHOUSE", "WHOLESALE A", "WHOLESALE-B", "WHOLESALE-C"
# #     ]
# # }

# # def get_channel(customer_group):
# #     if not customer_group:
# #         return ""
# #     customer_group_upper = customer_group.strip().upper()
# #     for channel, groups in CHANNEL_MAPPING.items():
# #         if customer_group_upper in (g.upper() for g in groups):
# #             return channel
# #     return ""

# # def execute(filters=None):
# #     filters = filters or {}
# #     year = filters.get("year")
# #     if not year:
# #         frappe.throw("Please select a year")

# #     columns = get_columns()
# #     data = get_data(year)
# #     return columns, data

# # def get_columns():
# #     months = [calendar.month_abbr[m] for m in range(1, 13)]
# #     columns = [
# #         {"label": "Channel", "fieldname": "channel", "fieldtype": "Data", "width": 150},
# #         {"label": "Item Code", "fieldname": "item_code", "fieldtype": "Data", "width": 140},
# #         {"label": "Item Name", "fieldname": "item_name", "fieldtype": "Data", "width": 250},
# #     ]
# #     for m in months:
# #         col_prefix = m.lower()
# #         columns.append({"label": f"{m} Sales", "fieldname": f"{col_prefix}_sales", "fieldtype": "Currency", "width": 100})
# #         columns.append({"label": f"{m} Qty", "fieldname": f"{col_prefix}_qty", "fieldtype": "Float", "width": 80})
# #         columns.append({"label": f"{m} Rate", "fieldname": f"{col_prefix}_rate", "fieldtype": "Currency", "width": 80})
# #         columns.append({"label": f"{m} Discount Rate", "fieldname": f"{col_prefix}_discount_rate", "fieldtype": "Float", "width": 110})
# #         columns.append({"label": f"{m} Net Rate", "fieldname": f"{col_prefix}_net_rate", "fieldtype": "Float", "width": 110})
# #     columns += [
# #         {"label": "Total Sales", "fieldname": "total_sales", "fieldtype": "Currency", "width": 110},
# #         {"label": "Total Qty", "fieldname": "total_qty", "fieldtype": "Float", "width": 90},
# #         {"label": "Total Rate", "fieldname": "total_rate", "fieldtype": "Currency", "width": 90},
# #         {"label": "Total Net Rate", "fieldname": "total_net_rate", "fieldtype": "Currency", "width": 110},
# #     ]
# #     return columns

# # def get_data(year):
# #     start_date = f"{year}-01-01"
# #     end_date = f"{year}-12-31"

# #     item_codes = (
# #         '6287016760027', '6287016760041', '6287016760034',
# #         '6287016760058', '6287016760119', '6287016760157', '6287016760164'
# #     )

# #     deduction_accounts = {
# #         "41010105": "41010105 - Sales Rebate/Trade Discount -حسم المبيعات /الخصم التجاري - ABNA",
# #         "516101": "516101 - Registerion Fees -رسوم التسجيل - ABNA",
# #         "516102": "516102 - Listing Fees -رسوم أدخال اصناف - ABNA",
# #         "516107": "516107 - Flyer Fees -رسوم فلاير - ABNA",
# #         "41010103": "41010103 - Discount Allowance -الخصم المسموح به - ABNA"
# #     }

# #     months = range(1, 13)

# #     # Aggregate data keyed by (channel, item_code)
# #     sales_data = defaultdict(lambda: defaultdict(lambda: {"sales": 0, "qty": 0}))
# #     meta_data = {}

# #     # Query sales invoices grouped by item_code, customer_group, month (to get customer_group for channel mapping)
# #     sales_results = frappe.db.sql("""
# #         SELECT
# #             sii.item_code,
# #             sii.item_name,
# #             si.customer_group,
# #             MONTH(si.posting_date) AS month,
# #             SUM(sii.qty) AS total_qty,
# #             SUM(sii.base_net_amount) AS total_sales
# #         FROM `tabSales Invoice` si
# #         JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
# #         WHERE
# #             si.docstatus = 1
# #             AND si.posting_date BETWEEN %s AND %s
# #             AND sii.item_code IN %s
# #         GROUP BY sii.item_code, si.customer_group, month
# #     """, (start_date, end_date, item_codes), as_dict=True)

# #     for r in sales_results:
# #         channel = get_channel(r.customer_group)
# #         key = (channel, r.item_code)
# #         sales_data[key][r.month]["sales"] += r.total_sales or 0
# #         sales_data[key][r.month]["qty"] += r.total_qty or 0

# #         meta_data[key] = {
# #             "item_name": r.item_name,
# #             "channel": channel,
# #         }

# #     def get_gl_monthly(account):
# #         gl_rows = frappe.db.sql("""
# #             SELECT MONTH(posting_date) AS month, SUM(debit - credit) AS amount
# #             FROM `tabGL Entry`
# #             WHERE account = %s AND posting_date BETWEEN %s AND %s
# #             GROUP BY month
# #         """, (account, start_date, end_date), as_dict=True)
# #         return {row.month: row.amount or 0 for row in gl_rows}

# #     monthly_deductions = {code: get_gl_monthly(account) for code, account in deduction_accounts.items()}

# #     total_deduct_monthly = {m: sum(monthly_deductions[code].get(m, 0) for code in deduction_accounts) for m in months}

# #     discount_rate_per_month = {}
# #     for m in months:
# #         total_qty_month = sum(sales_data[key][m]["qty"] for key in sales_data)
# #         discount_rate_per_month[m] = (total_deduct_monthly.get(m, 0) / total_qty_month) if total_qty_month else 0

# #     data = []
# #     totals_sales = defaultdict(float)
# #     totals_qty = defaultdict(float)

# #     for key in sales_data:
# #         channel, item_code = key
# #         meta = meta_data.get(key, {})
# #         row = {
# #             "item_code": item_code,
# #             "item_name": meta.get("item_name", ""),
# #             "channel": channel
# #         }
# #         total_sales_sum = 0
# #         total_qty_sum = 0

# #         for m in months:
# #             m_abbr = calendar.month_abbr[m].lower()
# #             sales = sales_data[key][m]["sales"]
# #             qty = sales_data[key][m]["qty"]
# #             rate = (sales / qty) if qty else 0

# #             totals_sales[m] += sales
# #             totals_qty[m] += qty

# #             discount_rate = discount_rate_per_month.get(m, 0)
# #             net_rate = rate - discount_rate

# #             row[f"{m_abbr}_sales"] = round(sales, 2)
# #             row[f"{m_abbr}_qty"] = round(qty, 2)
# #             row[f"{m_abbr}_rate"] = round(rate, 2)
# #             row[f"{m_abbr}_discount_rate"] = round(discount_rate, 4)
# #             row[f"{m_abbr}_net_rate"] = round(net_rate, 4)

# #             total_sales_sum += sales
# #             total_qty_sum += qty

# #         total_rate = (total_sales_sum / total_qty_sum) if total_qty_sum else 0
# #         total_discount = sum(discount_rate_per_month.get(m, 0) for m in months) / 12
# #         total_net_rate = total_rate - total_discount

# #         row["total_sales"] = round(total_sales_sum, 2)
# #         row["total_qty"] = round(total_qty_sum, 2)
# #         row["total_rate"] = round(total_rate, 2)
# #         row["total_net_rate"] = round(total_net_rate, 4)
# #         data.append(row)

# #     # Total row
# #     total_row = {
# #         "item_code": "TOTAL",
# #         "item_name": "Total of All Items",
# #         "channel": ""
# #     }
# #     total_sales_sum_all = 0
# #     total_qty_sum_all = 0
# #     for m in months:
# #         m_abbr = calendar.month_abbr[m].lower()
# #         sales = totals_sales[m]
# #         qty = totals_qty[m]
# #         rate = (sales / qty) if qty else 0
# #         discount_rate = discount_rate_per_month.get(m, 0)
# #         net_rate = rate - discount_rate

# #         total_row[f"{m_abbr}_sales"] = round(sales, 2)
# #         total_row[f"{m_abbr}_qty"] = round(qty, 2)
# #         total_row[f"{m_abbr}_rate"] = round(rate, 2)
# #         total_row[f"{m_abbr}_discount_rate"] = round(discount_rate, 4)
# #         total_row[f"{m_abbr}_net_rate"] = round(net_rate, 4)

# #         total_sales_sum_all += sales
# #         total_qty_sum_all += qty

# #     total_row["total_sales"] = round(total_sales_sum_all, 2)
# #     total_row["total_qty"] = round(total_qty_sum_all, 2)
# #     total_row["total_rate"] = round((total_sales_sum_all / total_qty_sum_all) if total_qty_sum_all else 0, 2)
# #     total_row["total_net_rate"] = round(total_row["total_rate"] - (sum(discount_rate_per_month.values()) / 12), 4)
# #     data.append(total_row)

# #     # Deduction rows
# #     def make_deduction_row(code, name, monthly_data):
# #         row = {
# #             "item_code": code,
# #             "item_name": name,
# #             "channel": ""
# #         }
# #         total_amt = 0
# #         for m in months:
# #             m_abbr = calendar.month_abbr[m].lower()
# #             amt = monthly_data.get(m, 0)
# #             row[f"{m_abbr}_sales"] = round(amt, 2)
# #             row[f"{m_abbr}_qty"] = 0
# #             row[f"{m_abbr}_rate"] = 0
# #             row[f"{m_abbr}_discount_rate"] = 0
# #             row[f"{m_abbr}_net_rate"] = 0
# #             total_amt += amt
# #         row["total_sales"] = round(total_amt, 2)
# #         row["total_qty"] = 0
# #         row["total_rate"] = 0
# #         row["total_net_rate"] = 0
# #         return row

# #     for code, monthly in monthly_deductions.items():
# #         data.append(make_deduction_row(code, code.replace("_", " ").title(), monthly))

# #     data.append(make_deduction_row("Total Deduction", "Total Deductions (All)", total_deduct_monthly))

# #     # Discount Rate summary row
# #     discount_rate_row = {
# #         "item_code": "Discount Rate",
# #         "item_name": "Discount Rate = Total Deduct / Total Qty",
# #         "channel": "",
# #     }
# #     for m in months:
# #         m_abbr = calendar.month_abbr[m].lower()
# #         val = discount_rate_per_month.get(m, 0)
# #         discount_rate_row[f"{m_abbr}_sales"] = round(val, 4)
# #         discount_rate_row[f"{m_abbr}_qty"] = 0
# #         discount_rate_row[f"{m_abbr}_rate"] = 0
# #         discount_rate_row[f"{m_abbr}_discount_rate"] = 0
# #         discount_rate_row[f"{m_abbr}_net_rate"] = 0
# #     discount_rate_row["total_sales"] = 0
# #     discount_rate_row["total_qty"] = 0
# #     discount_rate_row["total_rate"] = 0
# #     discount_rate_row["total_net_rate"] = 0
# #     data.append(discount_rate_row)

# #     return data


# # import frappe
# # from collections import defaultdict
# # import calendar

# # CHANNEL_MAPPING = {
# #     "DIRECT DISTRIBUTION DD": [
# #         "EATRIES", "LARGE GROCERY", "MINIMARKET", "SMALL GROCERY",
# #         "SUPERMARKET B", "WATER SHOP", "DIRECT DISTRIBUTION DD"
# #     ],
# #     "DISTRIBUTOR": [
# #         "DISTRIBUTOR A", "DISTRIBUTOR B", "DISTRIBUTOR C", "DISTRIBUTOR"
# #     ],
# #     "HOME DELIVERY HD": [
# #         "HOUSE", "MOSQUE", "OFFICE", "SCHOOL", "HOME DELIVERY HD"
# #     ],
# #     "HORECA HO": [
# #         "CAFÉ", "CARE", "CATERING", "COMMERCIAL", "GOVERNMENTAL",
# #         "HOTEL", "INSTITUTIONAL", "RESTAURANT", "HORECA HO","CAFE"
# #     ],
# #     "KEY ACCOUNT KA": [
# #         "E-COMMERCE", "HYPERMARKET", "SUPERMARKET-A", "SUPERMARKET-B", "KEY ACCOUNT  KA"
# #     ],
# #     "MARKETING": [
# #         "MARKETING", "DONATION", "EVENT", "SPONSORSHIP"
# #     ],
# #     "OTHER MISCELLANEOUS": [
# #         "OTHER MISCELLANEOUS","OTHER  MISCELLANEOUS"
# #     ],
# #     "WHOLESALE": [
# #         "WHOLESALE WS", "WAREHOUSE", "WHOLESALE A", "WHOLESALE-B", "WHOLESALE-C"
# #     ]
# # }

# # def get_channel(customer_group):
# #     if not customer_group:
# #         return ""
# #     customer_group_upper = customer_group.strip().upper()
# #     for channel, groups in CHANNEL_MAPPING.items():
# #         if customer_group_upper in (g.upper() for g in groups):
# #             return channel
# #     return ""

# # def execute(filters=None):
# #     filters = filters or {}
# #     year = filters.get("year")
# #     if not year:
# #         frappe.throw("Please select a year")

# #     columns = get_columns(year)
# #     data = get_data(year)
# #     return columns, data

# # def get_columns(year):
# #     months = [calendar.month_abbr[m] for m in range(1, 13)]
# #     columns = [
# #         {"label": "Customer", "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 200},
# #         {"label": "Channel", "fieldname": "channel", "fieldtype": "Data", "width": 150},
# #         {"label": "Customer Group", "fieldname": "customer_group", "fieldtype": "Link", "options": "Customer Group", "width": 180},
# #         {"label": "Item Code", "fieldname": "item_code", "fieldtype": "Data", "width": 140},
# #         {"label": "Item Name", "fieldname": "item_name", "fieldtype": "Data", "width": 250},
# #     ]
# #     for m in months:
# #         col_prefix = m.lower()
# #         columns.append({"label": f"{m} Sales", "fieldname": f"{col_prefix}_sales", "fieldtype": "Currency", "width": 100})
# #         columns.append({"label": f"{m} Qty", "fieldname": f"{col_prefix}_qty", "fieldtype": "Float", "width": 80})
# #         columns.append({"label": f"{m} Rate", "fieldname": f"{col_prefix}_rate", "fieldtype": "Currency", "width": 80})
# #         columns.append({"label": f"{m} Discount Rate", "fieldname": f"{col_prefix}_discount_rate", "fieldtype": "Float", "width": 110})
# #         columns.append({"label": f"{m} Net Rate", "fieldname": f"{col_prefix}_net_rate", "fieldtype": "Float", "width": 110})
# #     columns += [
# #         {"label": "Total Sales", "fieldname": "total_sales", "fieldtype": "Currency", "width": 110},
# #         {"label": "Total Qty", "fieldname": "total_qty", "fieldtype": "Float", "width": 90},
# #         {"label": "Total Rate", "fieldname": "total_rate", "fieldtype": "Currency", "width": 90},
# #         {"label": "Total Net Rate", "fieldname": "total_net_rate", "fieldtype": "Currency", "width": 110},
# #     ]
# #     return columns

# # def get_data(year):
# #     start_date = f"{year}-01-01"
# #     end_date = f"{year}-12-31"

# #     item_codes = (
# #         '6287016760027', '6287016760041', '6287016760034',
# #         '6287016760058', '6287016760119', '6287016760157', '6287016760164'
# #     )

# #     deduction_accounts = {
# #         "Rebate": "41010105 - Sales Rebate/Trade Discount -حسم المبيعات /الخصم التجاري - ABNA",
# #         "Registerion": "516101 - Registerion Fees -رسوم التسجيل - ABNA",
# #         "Listing": "516102 - Listing Fees -رسوم أدخال اصناف - ABNA",
# #         "Flyer": "516107 - Flyer Fees -رسوم فلاير - ABNA",
# #         "Discount": "41010103 - Discount Allowance -الخصم المسموح به - ABNA"
# #     }

# #     months = range(1, 13)
# #     sales_data = defaultdict(lambda: defaultdict(lambda: {"sales": 0, "qty": 0}))
# #     meta_data = {}

# #     sales_results = frappe.db.sql("""
# #         SELECT
# #             sii.item_code,
# #             sii.item_name,
# #             si.customer,
# #             si.customer_group,
# #             MONTH(si.posting_date) AS month,
# #             SUM(sii.qty) AS total_qty,
# #             SUM(sii.base_net_amount) AS total_sales
# #         FROM `tabSales Invoice` si
# #         JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
# #         WHERE
# #             si.docstatus = 1
# #             AND si.posting_date BETWEEN %s AND %s
# #             AND sii.item_code IN %s
# #         GROUP BY sii.item_code, si.customer, month
# #     """, (start_date, end_date, item_codes), as_dict=True)

# #     for r in sales_results:
# #         key = (r.item_code, r.customer)
# #         sales_data[key][r.month]["sales"] += r.total_sales or 0
# #         sales_data[key][r.month]["qty"] += r.total_qty or 0

# #         mapped_channel = get_channel(r.customer_group)

# #         meta_data[key] = {
# #             "item_name": r.item_name,
# #             "customer": r.customer,
# #             "customer_group": r.customer_group,
# #             "channel": mapped_channel
# #         }

# #     def get_gl_monthly(account):
# #         gl_rows = frappe.db.sql("""
# #             SELECT MONTH(posting_date) AS month, SUM(debit - credit) AS amount
# #             FROM `tabGL Entry`
# #             WHERE account = %s AND posting_date BETWEEN %s AND %s
# #             GROUP BY month
# #         """, (account, start_date, end_date), as_dict=True)
# #         return {row.month: row.amount or 0 for row in gl_rows}

# #     monthly_deductions = {code: get_gl_monthly(account) for code, account in deduction_accounts.items()}

# #     total_deduct_monthly = {m: sum(monthly_deductions[code].get(m, 0) for code in deduction_accounts) for m in months}

# #     discount_rate_per_month = {}
# #     for m in months:
# #         total_qty_month = sum(sales_data[key][m]["qty"] for key in sales_data)
# #         discount_rate_per_month[m] = (total_deduct_monthly.get(m, 0) / total_qty_month) if total_qty_month else 0

# #     data = []
# #     totals_sales = defaultdict(float)
# #     totals_qty = defaultdict(float)

# #     for key in sales_data:
# #         item_code, customer = key
# #         meta = meta_data.get(key, {})
# #         row = {
# #             "item_code": item_code,
# #             "item_name": meta.get("item_name", ""),
# #             "customer": meta.get("customer", ""),
# #             "customer_group": meta.get("customer_group", ""),
# #             "channel": meta.get("channel", "")
# #         }
# #         total_sales_sum = 0
# #         total_qty_sum = 0

# #         for m in months:
# #             m_abbr = calendar.month_abbr[m].lower()
# #             sales = sales_data[key][m]["sales"]
# #             qty = sales_data[key][m]["qty"]
# #             rate = (sales / qty) if qty else 0

# #             totals_sales[m] += sales
# #             totals_qty[m] += qty

# #             discount_rate = discount_rate_per_month.get(m, 0)
# #             net_rate = rate - discount_rate

# #             row[f"{m_abbr}_sales"] = round(sales, 2)
# #             row[f"{m_abbr}_qty"] = round(qty, 2)
# #             row[f"{m_abbr}_rate"] = round(rate, 2)
# #             row[f"{m_abbr}_discount_rate"] = round(discount_rate, 4)
# #             row[f"{m_abbr}_net_rate"] = round(net_rate, 4)

# #             total_sales_sum += sales
# #             total_qty_sum += qty

# #         total_rate = (total_sales_sum / total_qty_sum) if total_qty_sum else 0
# #         total_discount = sum(discount_rate_per_month.get(m, 0) for m in months) / 12
# #         total_net_rate = total_rate - total_discount

# #         row["total_sales"] = round(total_sales_sum, 2)
# #         row["total_qty"] = round(total_qty_sum, 2)
# #         row["total_rate"] = round(total_rate, 2)
# #         row["total_net_rate"] = round(total_net_rate, 4)
# #         data.append(row)

# #     # Total row
# #     total_row = {
# #         "item_code": "TOTAL",
# #         "item_name": "Total of All Items",
# #         "customer": "",
# #         "customer_group": "",
# #         "channel": ""
# #     }
# #     total_sales_sum_all = 0
# #     total_qty_sum_all = 0
# #     for m in months:
# #         m_abbr = calendar.month_abbr[m].lower()
# #         sales = totals_sales[m]
# #         qty = totals_qty[m]
# #         rate = (sales / qty) if qty else 0
# #         discount_rate = discount_rate_per_month.get(m, 0)
# #         net_rate = rate - discount_rate

# #         total_row[f"{m_abbr}_sales"] = round(sales, 2)
# #         total_row[f"{m_abbr}_qty"] = round(qty, 2)
# #         total_row[f"{m_abbr}_rate"] = round(rate, 2)
# #         total_row[f"{m_abbr}_discount_rate"] = round(discount_rate, 4)
# #         total_row[f"{m_abbr}_net_rate"] = round(net_rate, 4)

# #         total_sales_sum_all += sales
# #         total_qty_sum_all += qty

# #     total_row["total_sales"] = round(total_sales_sum_all, 2)
# #     total_row["total_qty"] = round(total_qty_sum_all, 2)
# #     total_row["total_rate"] = round((total_sales_sum_all / total_qty_sum_all) if total_qty_sum_all else 0, 2)
# #     total_row["total_net_rate"] = round(total_row["total_rate"] - (sum(discount_rate_per_month.values())/12), 4)
# #     data.append(total_row)

# #     # Deduction rows
# #     def make_deduction_row(code, name, monthly_data):
# #         row = {
# #             "item_code": code,
# #             "item_name": name,
# #             "customer": "",
# #             "customer_group": "",
# #             "channel": ""
# #         }
# #         total_amt = 0
# #         for m in months:
# #             m_abbr = calendar.month_abbr[m].lower()
# #             amt = monthly_data.get(m, 0)
# #             row[f"{m_abbr}_sales"] = round(amt, 2)
# #             row[f"{m_abbr}_qty"] = 0
# #             row[f"{m_abbr}_rate"] = 0
# #             row[f"{m_abbr}_discount_rate"] = 0
# #             row[f"{m_abbr}_net_rate"] = 0
# #             total_amt += amt
# #         row["total_sales"] = round(total_amt, 2)
# #         row["total_qty"] = 0
# #         row["total_rate"] = 0
# #         row["total_net_rate"] = 0
# #         return row

# #     for code, monthly in monthly_deductions.items():
# #         data.append(make_deduction_row(code, code.replace("_", " ").title(), monthly))

# #     data.append(make_deduction_row("Total Deduction", "Total Deductions (All)", total_deduct_monthly))

# #     # Discount Rate summary row
# #     discount_rate_row = {
# #         "item_code": "Discount Rate",
# #         "item_name": "Discount Rate = Total Deduct / Total Qty",
# #         "customer": "",
# #         "customer_group": "",
# #         "channel": "",
# #     }
# #     for m in months:
# #         m_abbr = calendar.month_abbr[m].lower()
# #         val = discount_rate_per_month.get(m, 0)
# #         discount_rate_row[f"{m_abbr}_sales"] = round(val, 4)
# #         discount_rate_row[f"{m_abbr}_qty"] = 0
# #         discount_rate_row[f"{m_abbr}_rate"] = 0
# #         discount_rate_row[f"{m_abbr}_discount_rate"] = 0
# #         discount_rate_row[f"{m_abbr}_net_rate"] = 0
# #     discount_rate_row["total_sales"] = 0
# #     discount_rate_row["total_qty"] = 0
# #     discount_rate_row["total_rate"] = 0
# #     discount_rate_row["total_net_rate"] = 0
# #     data.append(discount_rate_row)

# #     return data


# # import frappe
# # from collections import defaultdict
# # import calendar

# # CHANNEL_MAPPING = {
# #     "DIRECT DISTRIBUTION DD": [
# #         "EATRIES", "LARGE GROCERY", "MINIMARKET", "SMALL GROCERY",
# #         "SUPERMARKET B", "WATER SHOP", "DIRECT DISTRIBUTION DD"
# #     ],
# #     "DISTRIBUTOR": [
# #         "DISTRIBUTOR A", "DISTRIBUTOR B", "DISTRIBUTOR C", "DISTRIBUTOR"
# #     ],
# #     "HOME DELIVERY HD": [
# #         "HOUSE", "MOSQUE", "OFFICE", "SCHOOL", "HOME DELIVERY HD"
# #     ],
# #     "HORECA HO": [
# #         "CAFÉ", "CARE", "CATERING", "COMMERCIAL", "GOVERNMENTAL",
# #         "HOTEL", "INSTITUTIONAL", "RESTAURANT", "HORECA HO","CAFE"
# #     ],
# #     "KEY ACCOUNT KA": [
# #         "E-COMMERCE", "HYPERMARKET", "SUPERMARKET-A", "SUPERMARKET-B", "KEY ACCOUNT  KA"
# #     ],
# #     "MARKETING": [
# #         "MARKETING", "DONATION", "EVENT", "SPONSORSHIP"
# #     ],
# #     "OTHER MISCELLANEOUS": [
# #         "OTHER MISCELLANEOUS","OTHER  MISCELLANEOUS"
# #     ],
# #     "WHOLESALE": [
# #         "WHOLESALE WS", "WAREHOUSE", "WHOLESALE A", "WHOLESALE-B", "WHOLESALE-C"
# #     ]
# # }

# # def get_channel(customer_group):
# #     if not customer_group:
# #         return ""
# #     customer_group_upper = customer_group.strip().upper()
# #     for channel, groups in CHANNEL_MAPPING.items():
# #         if customer_group_upper in (g.upper() for g in groups):
# #             return channel
# #     return ""

# # def execute(filters=None):
# #     filters = filters or {}
# #     year = filters.get("year")
# #     if not year:
# #         frappe.throw("Please select a year")

# #     columns = get_columns(year)
# #     data = get_data(year)
# #     return columns, data

# # def get_columns(year):
# #     months = [calendar.month_abbr[m] for m in range(1, 13)]
# #     columns = [
# #         {"label": "Customer", "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 200},
# #         {"label": "Channel", "fieldname": "channel", "fieldtype": "Data", "width": 150},
# #         {"label": "Customer Group", "fieldname": "customer_group", "fieldtype": "Link", "options": "Customer Group", "width": 180},
# #         {"label": "Item Code", "fieldname": "item_code", "fieldtype": "Data", "width": 140},
# #         {"label": "Item Name", "fieldname": "item_name", "fieldtype": "Data", "width": 250},
# #     ]
# #     for m in months:
# #         col_prefix = m.lower()
# #         columns.append({"label": f"{m} Sales", "fieldname": f"{col_prefix}_sales", "fieldtype": "Currency", "width": 100})
# #         columns.append({"label": f"{m} Qty", "fieldname": f"{col_prefix}_qty", "fieldtype": "Float", "width": 80})
# #         columns.append({"label": f"{m} Rate", "fieldname": f"{col_prefix}_rate", "fieldtype": "Currency", "width": 80})
# #         columns.append({"label": f"{m} Discount Rate", "fieldname": f"{col_prefix}_discount_rate", "fieldtype": "Float", "width": 110})
# #         columns.append({"label": f"{m} Net Rate", "fieldname": f"{col_prefix}_net_rate", "fieldtype": "Float", "width": 110})
# #     columns += [
# #         {"label": "Total Sales", "fieldname": "total_sales", "fieldtype": "Currency", "width": 110},
# #         {"label": "Total Qty", "fieldname": "total_qty", "fieldtype": "Float", "width": 90},
# #         {"label": "Total Rate", "fieldname": "total_rate", "fieldtype": "Currency", "width": 90},
# #         {"label": "Total Net Rate", "fieldname": "total_net_rate", "fieldtype": "Currency", "width": 110},
# #     ]
# #     return columns

# # def get_monthly_rebate_by_customer(start_date, end_date):
# #     results = frappe.db.sql("""
# #         SELECT
# #             party AS customer,
# #             MONTH(posting_date) AS month,
# #             SUM(rebate_received_amount) AS rebate_amount
# #         FROM `tabRebate`
# #         WHERE
# #             docstatus = 1
# #             AND party_type = 'Customer'
# #             AND posting_date BETWEEN %s AND %s
# #         GROUP BY party, MONTH(posting_date)
# #     """, (start_date, end_date), as_dict=True)

# #     rebate_data = defaultdict(lambda: defaultdict(float))
# #     for row in results:
# #         rebate_data[row.customer][row.month] += row.rebate_amount or 0

# #     return rebate_data

# # def get_customer_groups(customers):
# #     if not customers:
# #         return {}
# #     customer_groups = frappe.db.sql("""
# #         SELECT name, customer_group FROM `tabCustomer`
# #         WHERE name IN %s
# #     """, (tuple(customers),), as_dict=True)
# #     return {c.name: c.customer_group for c in customer_groups}

# # def get_data(year):
# #     start_date = f"{year}-01-01"
# #     end_date = f"{year}-12-31"

# #     item_codes = (
# #         '6287016760027', '6287016760041', '6287016760034',
# #         '6287016760058', '6287016760119', '6287016760157', '6287016760164'
# #     )

# #     deduction_accounts = {
# #         "Rebate": "41010105 - Sales Rebate/Trade Discount -حسم المبيعات /الخصم التجاري - ABNA",
# #         "Registerion": "516101 - Registerion Fees -رسوم التسجيل - ABNA",
# #         "Listing": "516102 - Listing Fees -رسوم أدخال اصناف - ABNA",
# #         "Flyer": "516107 - Flyer Fees -رسوم فلاير - ABNA",
# #         "Discount": "41010103 - Discount Allowance -الخصم المسموح به - ABNA"
# #     }

# #     months = range(1, 13)
# #     sales_data = defaultdict(lambda: defaultdict(lambda: {"sales": 0, "qty": 0}))
# #     meta_data = {}

# #     sales_results = frappe.db.sql("""
# #         SELECT
# #             sii.item_code,
# #             sii.item_name,
# #             si.customer,
# #             si.customer_group,
# #             MONTH(si.posting_date) AS month,
# #             SUM(sii.qty) AS total_qty,
# #             SUM(sii.base_net_amount) AS total_sales
# #         FROM `tabSales Invoice` si
# #         JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
# #         WHERE
# #             si.docstatus = 1
# #             AND si.posting_date BETWEEN %s AND %s
# #             AND sii.item_code IN %s
# #         GROUP BY sii.item_code, si.customer, month
# #     """, (start_date, end_date, item_codes), as_dict=True)

# #     for r in sales_results:
# #         key = (r.item_code, r.customer)
# #         sales_data[key][r.month]["sales"] += r.total_sales or 0
# #         sales_data[key][r.month]["qty"] += r.total_qty or 0

# #         mapped_channel = get_channel(r.customer_group)

# #         meta_data[key] = {
# #             "item_name": r.item_name,
# #             "customer": r.customer,
# #             "customer_group": r.customer_group,
# #             "channel": mapped_channel
# #         }

# #     def get_gl_monthly(account):
# #         gl_rows = frappe.db.sql("""
# #             SELECT MONTH(posting_date) AS month, SUM(debit - credit) AS amount
# #             FROM `tabGL Entry`
# #             WHERE account = %s AND posting_date BETWEEN %s AND %s
# #             GROUP BY month
# #         """, (account, start_date, end_date), as_dict=True)
# #         return {row.month: row.amount or 0 for row in gl_rows}

# #     monthly_deductions = {code: get_gl_monthly(account) for code, account in deduction_accounts.items()}

# #     total_deduct_monthly = {m: sum(monthly_deductions[code].get(m, 0) for code in deduction_accounts) for m in months}

# #     discount_rate_per_month = {}
# #     for m in months:
# #         total_qty_month = sum(sales_data[key][m]["qty"] for key in sales_data)
# #         discount_rate_per_month[m] = (total_deduct_monthly.get(m, 0) / total_qty_month) if total_qty_month else 0

# #     data = []
# #     totals_sales = defaultdict(float)
# #     totals_qty = defaultdict(float)

# #     # Fetch rebate data from Rebate doctype
# #     rebate_by_customer = get_monthly_rebate_by_customer(start_date, end_date)
# #     rebate_customers = list(rebate_by_customer.keys())
# #     rebate_customer_groups = get_customer_groups(rebate_customers)

# #     for key in sales_data:
# #         item_code, customer = key
# #         meta = meta_data.get(key, {})
# #         row = {
# #             "item_code": item_code,
# #             "item_name": meta.get("item_name", ""),
# #             "customer": meta.get("customer", ""),
# #             "customer_group": meta.get("customer_group", ""),
# #             "channel": meta.get("channel", "")
# #         }
# #         total_sales_sum = 0
# #         total_qty_sum = 0

# #         for m in months:
# #             m_abbr = calendar.month_abbr[m].lower()
# #             sales = sales_data[key][m]["sales"]
# #             qty = sales_data[key][m]["qty"]
# #             rate = (sales / qty) if qty else 0

# #             totals_sales[m] += sales
# #             totals_qty[m] += qty

# #             discount_rate = discount_rate_per_month.get(m, 0)
# #             net_rate = rate - discount_rate

# #             row[f"{m_abbr}_sales"] = round(sales, 2)
# #             row[f"{m_abbr}_qty"] = round(qty, 2)
# #             row[f"{m_abbr}_rate"] = round(rate, 2)
# #             row[f"{m_abbr}_discount_rate"] = round(discount_rate, 4)
# #             row[f"{m_abbr}_net_rate"] = round(net_rate, 4)

# #             total_sales_sum += sales
# #             total_qty_sum += qty

# #         total_rate = (total_sales_sum / total_qty_sum) if total_qty_sum else 0
# #         total_discount = sum(discount_rate_per_month.get(m, 0) for m in months) / 12
# #         total_net_rate = total_rate - total_discount

# #         row["total_sales"] = round(total_sales_sum, 2)
# #         row["total_qty"] = round(total_qty_sum, 2)
# #         row["total_rate"] = round(total_rate, 2)
# #         row["total_net_rate"] = round(total_net_rate, 4)
# #         data.append(row)

# #     # Total row
# #     total_row = {
# #         "item_code": "TOTAL",
# #         "item_name": "Total of All Items",
# #         "customer": "",
# #         "customer_group": "",
# #         "channel": ""
# #     }
# #     total_sales_sum_all = 0
# #     total_qty_sum_all = 0
# #     for m in months:
# #         m_abbr = calendar.month_abbr[m].lower()
# #         sales = totals_sales[m]
# #         qty = totals_qty[m]
# #         rate = (sales / qty) if qty else 0
# #         discount_rate = discount_rate_per_month.get(m, 0)
# #         net_rate = rate - discount_rate

# #         total_row[f"{m_abbr}_sales"] = round(sales, 2)
# #         total_row[f"{m_abbr}_qty"] = round(qty, 2)
# #         total_row[f"{m_abbr}_rate"] = round(rate, 2)
# #         total_row[f"{m_abbr}_discount_rate"] = round(discount_rate, 4)
# #         total_row[f"{m_abbr}_net_rate"] = round(net_rate, 4)

# #         total_sales_sum_all += sales
# #         total_qty_sum_all += qty

# #     total_row["total_sales"] = round(total_sales_sum_all, 2)
# #     total_row["total_qty"] = round(total_qty_sum_all, 2)
# #     total_row["total_rate"] = round((total_sales_sum_all / total_qty_sum_all) if total_qty_sum_all else 0, 2)
# #     total_row["total_net_rate"] = round(total_row["total_rate"] - (sum(discount_rate_per_month.values())/12), 4)
# #     data.append(total_row)

# #     # Deduction rows
# #     def make_deduction_row(code, name, monthly_data):
# #         row = {
# #             "item_code": code,
# #             "item_name": name,
# #             "customer": "",
# #             "customer_group": "",
# #             "channel": ""
# #         }
# #         total_amt = 0
# #         for m in months:
# #             m_abbr = calendar.month_abbr[m].lower()
# #             amt = monthly_data.get(m, 0)
# #             row[f"{m_abbr}_sales"] = round(amt, 2)
# #             row[f"{m_abbr}_qty"] = 0
# #             row[f"{m_abbr}_rate"] = 0
# #             row[f"{m_abbr}_discount_rate"] = 0
# #             row[f"{m_abbr}_net_rate"] = 0
# #             total_amt += amt
# #         row["total_sales"] = round(total_amt, 2)
# #         row["total_qty"] = 0
# #         row["total_rate"] = 0
# #         row["total_net_rate"] = 0
# #         return row

# #     for code, monthly in monthly_deductions.items():
# #         data.append(make_deduction_row(code, code.replace("_", " ").title(), monthly))

# #     data.append(make_deduction_row("Total Deduction", "Total Deductions (All)", total_deduct_monthly))

# #     # Discount Rate summary row
# #     discount_rate_row = {
# #         "item_code": "Discount Rate",
# #         "item_name": "Discount Rate = Total Deduct / Total Qty",
# #         "customer": "",
# #         "customer_group": "",
# #         "channel": "",
# #     }
# #     for m in months:
# #         m_abbr = calendar.month_abbr[m].lower()
# #         val = discount_rate_per_month.get(m, 0)
# #         discount_rate_row[f"{m_abbr}_sales"] = round(val, 4)
# #         discount_rate_row[f"{m_abbr}_qty"] = 0
# #         discount_rate_row[f"{m_abbr}_rate"] = 0
# #         discount_rate_row[f"{m_abbr}_discount_rate"] = 0
# #         discount_rate_row[f"{m_abbr}_net_rate"] = 0
# #     discount_rate_row["total_sales"] = 0
# #     discount_rate_row["total_qty"] = 0
# #     discount_rate_row["total_rate"] = 0
# #     discount_rate_row["total_net_rate"] = 0
# #     data.append(discount_rate_row)

# #     # --- Add rebate amount breakdown rows per customer with customer group and channel ---
# #     for customer, monthly_rebates in rebate_by_customer.items():
# #         customer_group = rebate_customer_groups.get(customer, "")
# #         channel = get_channel(customer_group)
# #         row = {
# #             "item_code": "REBATE",
# #             "item_name": "Rebate Breakdown",
# #             "customer": customer,
# #             "customer_group": customer_group,
# #             "channel": channel,
# #         }
# #         total_rebate = 0
# #         for m in months:
# #             m_abbr = calendar.month_abbr[m].lower()
# #             rebate = monthly_rebates.get(m, 0)
# #             row[f"{m_abbr}_sales"] = round(rebate, 2)
# #             row[f"{m_abbr}_qty"] = 0
# #             row[f"{m_abbr}_rate"] = 0
# #             row[f"{m_abbr}_discount_rate"] = 0
# #             row[f"{m_abbr}_net_rate"] = 0
# #             total_rebate += rebate

# #         row["total_sales"] = round(total_rebate, 2)
# #         row["total_qty"] = 0
# #         row["total_rate"] = 0
# #         row["total_net_rate"] = 0
# #         data.append(row)

# #     return data


# # import frappe
# # from collections import defaultdict
# # import calendar

# # CHANNEL_MAPPING = {
# #     "DIRECT DISTRIBUTION DD": [
# #         "EATRIES", "LARGE GROCERY", "MINIMARKET", "SMALL GROCERY",
# #         "SUPERMARKET B", "WATER SHOP", "DIRECT DISTRIBUTION DD"
# #     ],
# #     "DISTRIBUTOR": [
# #         "DISTRIBUTOR A", "DISTRIBUTOR B", "DISTRIBUTOR C", "DISTRIBUTOR"
# #     ],
# #     "HOME DELIVERY HD": [
# #         "HOUSE", "MOSQUE", "OFFICE", "SCHOOL", "HOME DELIVERY HD"
# #     ],
# #     "HORECA HO": [
# #         "CAFÉ", "CARE", "CATERING", "COMMERCIAL", "GOVERNMENTAL",
# #         "HOTEL", "INSTITUTIONAL", "RESTAURANT", "HORECA HO", "CAFE"
# #     ],
# #     "KEY ACCOUNT KA": [
# #         "E-COMMERCE", "HYPERMARKET", "SUPERMARKET-A", "SUPERMARKET-B", "KEY ACCOUNT  KA"
# #     ],
# #     "MARKETING": [
# #         "MARKETING", "DONATION", "EVENT", "SPONSORSHIP"
# #     ],
# #     "OTHER MISCELLANEOUS": [
# #         "OTHER MISCELLANEOUS", "OTHER  MISCELLANEOUS"
# #     ],
# #     "WHOLESALE": [
# #         "WHOLESALE WS", "WAREHOUSE", "WHOLESALE A", "WHOLESALE-B", "WHOLESALE-C"
# #     ]
# # }

# # def get_channel(customer_group):
# #     if not customer_group:
# #         return ""
# #     customer_group_upper = customer_group.strip().upper()
# #     for channel, groups in CHANNEL_MAPPING.items():
# #         if customer_group_upper in (g.upper() for g in groups):
# #             return channel
# #     return ""

# # def execute(filters=None):
# #     filters = filters or {}
# #     year = filters.get("year")
# #     if not year:
# #         frappe.throw("Please select a year")

# #     columns = get_columns(year)
# #     data = get_data(year)
# #     return columns, data

# # def get_columns(year):
# #     months = [calendar.month_abbr[m] for m in range(1, 13)]
# #     columns = [
# #         {"label": "Customer", "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 200},
# #         {"label": "Channel", "fieldname": "channel", "fieldtype": "Data", "width": 150},
# #         {"label": "Customer Group", "fieldname": "customer_group", "fieldtype": "Link", "options": "Customer Group", "width": 180},
# #         {"label": "Item Code", "fieldname": "item_code", "fieldtype": "Data", "width": 140},
# #         {"label": "Item Name", "fieldname": "item_name", "fieldtype": "Data", "width": 250},
# #     ]
# #     for m in months:
# #         col_prefix = m.lower()
# #         columns.append({"label": f"{m} Sales", "fieldname": f"{col_prefix}_sales", "fieldtype": "Currency", "width": 100})
# #         columns.append({"label": f"{m} Qty", "fieldname": f"{col_prefix}_qty", "fieldtype": "Float", "width": 80})
# #         columns.append({"label": f"{m} Rate", "fieldname": f"{col_prefix}_rate", "fieldtype": "Currency", "width": 80})
# #         columns.append({"label": f"{m} Discount Rate", "fieldname": f"{col_prefix}_discount_rate", "fieldtype": "Float", "width": 110})
# #         columns.append({"label": f"{m} Net Rate", "fieldname": f"{col_prefix}_net_rate", "fieldtype": "Float", "width": 110})
# #     columns += [
# #         {"label": "Total Sales", "fieldname": "total_sales", "fieldtype": "Currency", "width": 110},
# #         {"label": "Total Qty", "fieldname": "total_qty", "fieldtype": "Float", "width": 90},
# #         {"label": "Total Rate", "fieldname": "total_rate", "fieldtype": "Currency", "width": 90},
# #         {"label": "Total Net Rate", "fieldname": "total_net_rate", "fieldtype": "Currency", "width": 110},
# #     ]
# #     return columns

# # def get_monthly_rebate_by_customer(start_date, end_date):
# #     results = frappe.db.sql("""
# #         SELECT
# #             party AS customer,
# #             MONTH(posting_date) AS month,
# #             SUM(rebate_received_amount) AS rebate_amount
# #         FROM `tabRebate`
# #         WHERE
# #             docstatus = 1
# #             AND party_type = 'Customer'
# #             AND posting_date BETWEEN %s AND %s
# #         GROUP BY party, MONTH(posting_date)
# #     """, (start_date, end_date), as_dict=True)

# #     rebate_data = defaultdict(lambda: defaultdict(float))
# #     for row in results:
# #         rebate_data[row.customer][row.month] += row.rebate_amount or 0

# #     return rebate_data

# # def get_monthly_discount_by_customer(start_date, end_date):
# #     results = frappe.db.sql("""
# #         SELECT
# #             customer,
# #             MONTH(posting_date) AS month,
# #             SUM(promtion_amount) AS discount_amount
# #         FROM `tabCustomer Promotion`
# #         WHERE
# #             docstatus = 1
# #             AND posting_date BETWEEN %s AND %s
# #         GROUP BY customer, MONTH(posting_date)
# #     """, (start_date, end_date), as_dict=True)

# #     discount_data = defaultdict(lambda: defaultdict(float))
# #     for row in results:
# #         discount_data[row.customer][row.month] += row.discount_amount or 0

# #     return discount_data

# # def get_credit_note_deductions_by_customer(start_date, end_date):
# #     deduction_accounts = {
# #         "Flyer": "516107 - Flyer Fees -رسوم فلاير - ABNA",
# #         "Listing": "516102 - Listing Fees -رسوم أدخال اصناف - ABNA",
# #         "Registerion": "516101 - Registerion Fees -رسوم التسجيل - ABNA"
# #     }

# #     accounts_list = list(deduction_accounts.values())
# #     placeholders = ', '.join(['%s'] * len(accounts_list))

# #     query = f"""
# #         SELECT
# #             cn.customer,
# #             MONTH(cn.posting_date) AS month,
# #             cni.account,
# #             SUM(cni.debit - cni.credit) AS amount
# #         FROM `tabCredit Note` cn
# #         JOIN `tabJournal Entry Account` cni ON cni.parent = cn.name
# #         WHERE
# #             cn.docstatus = 1
# #             AND cn.posting_date BETWEEN %s AND %s
# #             AND cni.account IN ({placeholders})
# #         GROUP BY cn.customer, cni.account, MONTH(cn.posting_date)
# #     """

# #     params = [start_date, end_date] + accounts_list

# #     results = frappe.db.sql(query, params, as_dict=True)

# #     data = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))
# #     account_to_type = {v: k for k, v in deduction_accounts.items()}

# #     for row in results:
# #         deduction_type = account_to_type.get(row.account, "Unknown")
# #         data[row.customer][deduction_type][row.month] += row.amount or 0

# #     return data

# # def get_customer_groups(customers):
# #     if not customers:
# #         return {}
# #     customer_groups = frappe.db.sql("""
# #         SELECT name, customer_group FROM `tabCustomer`
# #         WHERE name IN %s
# #     """, (tuple(customers),), as_dict=True)
# #     return {c.name: c.customer_group for c in customer_groups}

# # def get_data(year):
# #     start_date = f"{year}-01-01"
# #     end_date = f"{year}-12-31"

# #     item_codes = (
# #         '6287016760027', '6287016760041', '6287016760034',
# #         '6287016760058', '6287016760119', '6287016760157', '6287016760164'
# #     )

# #     deduction_accounts = {
# #         "Rebate": "41010105 - Sales Rebate/Trade Discount -حسم المبيعات /الخصم التجاري - ABNA",
# #         "Registerion": "516101 - Registerion Fees -رسوم التسجيل - ABNA",
# #         "Listing": "516102 - Listing Fees -رسوم أدخال اصناف - ABNA",
# #         "Flyer": "516107 - Flyer Fees -رسوم فلاير - ABNA",
# #         "Discount": "41010103 - Discount Allowance -الخصم المسموح به - ABNA"
# #     }

# #     months = range(1, 13)
# #     sales_data = defaultdict(lambda: defaultdict(lambda: {"sales": 0, "qty": 0}))
# #     meta_data = {}

# #     sales_results = frappe.db.sql("""
# #         SELECT
# #             sii.item_code,
# #             sii.item_name,
# #             si.customer,
# #             si.customer_group,
# #             MONTH(si.posting_date) AS month,
# #             SUM(sii.qty) AS total_qty,
# #             SUM(sii.base_net_amount) AS total_sales
# #         FROM `tabSales Invoice` si
# #         JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
# #         WHERE
# #             si.docstatus = 1
# #             AND si.posting_date BETWEEN %s AND %s
# #             AND sii.item_code IN %s
# #         GROUP BY sii.item_code, si.customer, month
# #     """, (start_date, end_date, item_codes), as_dict=True)

# #     for r in sales_results:
# #         key = (r.item_code, r.customer)
# #         sales_data[key][r.month]["sales"] += r.total_sales or 0
# #         sales_data[key][r.month]["qty"] += r.total_qty or 0

# #         mapped_channel = get_channel(r.customer_group)

# #         meta_data[key] = {
# #             "item_name": r.item_name,
# #             "customer": r.customer,
# #             "customer_group": r.customer_group,
# #             "channel": mapped_channel
# #         }

# #     def get_gl_monthly(account):
# #         gl_rows = frappe.db.sql("""
# #             SELECT MONTH(posting_date) AS month, SUM(debit - credit) AS amount
# #             FROM `tabGL Entry`
# #             WHERE account = %s AND posting_date BETWEEN %s AND %s
# #             GROUP BY month
# #         """, (account, start_date, end_date), as_dict=True)
# #         return {row.month: row.amount or 0 for row in gl_rows}

# #     monthly_deductions = {code: get_gl_monthly(account) for code, account in deduction_accounts.items()}

# #     total_deduct_monthly = {m: sum(monthly_deductions[code].get(m, 0) for code in deduction_accounts) for m in months}

# #     discount_rate_per_month = {}
# #     for m in months:
# #         total_qty_month = sum(sales_data[key][m]["qty"] for key in sales_data)
# #         discount_rate_per_month[m] = (total_deduct_monthly.get(m, 0) / total_qty_month) if total_qty_month else 0

# #     data = []
# #     totals_sales = defaultdict(float)
# #     totals_qty = defaultdict(float)

# #     # Fetch rebate data from Rebate doctype
# #     rebate_by_customer = get_monthly_rebate_by_customer(start_date, end_date)
# #     rebate_customers = list(rebate_by_customer.keys())
# #     rebate_customer_groups = get_customer_groups(rebate_customers)

# #     for key in sales_data:
# #         item_code, customer = key
# #         meta = meta_data.get(key, {})
# #         row = {
# #             "item_code": item_code,
# #             "item_name": meta.get("item_name", ""),
# #             "customer": meta.get("customer", ""),
# #             "customer_group": meta.get("customer_group", ""),
# #             "channel": meta.get("channel", "")
# #         }
# #         total_sales_sum = 0
# #         total_qty_sum = 0

# #         for m in months:
# #             m_abbr = calendar.month_abbr[m].lower()
# #             sales = sales_data[key][m]["sales"]
# #             qty = sales_data[key][m]["qty"]
# #             rate = (sales / qty) if qty else 0

# #             totals_sales[m] += sales
# #             totals_qty[m] += qty

# #             discount_rate = discount_rate_per_month.get(m, 0)
# #             net_rate = rate - discount_rate

# #             row[f"{m_abbr}_sales"] = round(sales, 2)
# #             row[f"{m_abbr}_qty"] = round(qty, 2)
# #             row[f"{m_abbr}_rate"] = round(rate, 2)
# #             row[f"{m_abbr}_discount_rate"] = round(discount_rate, 4)
# #             row[f"{m_abbr}_net_rate"] = round(net_rate, 4)

# #             total_sales_sum += sales
# #             total_qty_sum += qty

# #         total_rate = (total_sales_sum / total_qty_sum) if total_qty_sum else 0
# #         total_discount = sum(discount_rate_per_month.get(m, 0) for m in months) / 12
# #         total_net_rate = total_rate - total_discount

# #         row["total_sales"] = round(total_sales_sum, 2)
# #         row["total_qty"] = round(total_qty_sum, 2)
# #         row["total_rate"] = round(total_rate, 2)
# #         row["total_net_rate"] = round(total_net_rate, 4)
# #         data.append(row)

# #     # Total row
# #     total_row = {
# #         "item_code": "TOTAL",
# #         "item_name": "Total of All Items",
# #         "customer": "",
# #         "customer_group": "",
# #         "channel": ""
# #     }
# #     total_sales_sum_all = 0
# #     total_qty_sum_all = 0
# #     for m in months:
# #         m_abbr = calendar.month_abbr[m].lower()
# #         sales = totals_sales[m]
# #         qty = totals_qty[m]
# #         rate = (sales / qty) if qty else 0
# #         discount_rate = discount_rate_per_month.get(m, 0)
# #         net_rate = rate - discount_rate

# #         total_row[f"{m_abbr}_sales"] = round(sales, 2)
# #         total_row[f"{m_abbr}_qty"] = round(qty, 2)
# #         total_row[f"{m_abbr}_rate"] = round(rate, 2)
# #         total_row[f"{m_abbr}_discount_rate"] = round(discount_rate, 4)
# #         total_row[f"{m_abbr}_net_rate"] = round(net_rate, 4)

# #         total_sales_sum_all += sales
# #         total_qty_sum_all += qty

# #     total_row["total_sales"] = round(total_sales_sum_all, 2)
# #     total_row["total_qty"] = round(total_qty_sum_all, 2)
# #     total_row["total_rate"] = round((total_sales_sum_all / total_qty_sum_all) if total_qty_sum_all else 0, 2)
# #     total_row["total_net_rate"] = round(total_row["total_rate"] - (sum(discount_rate_per_month.values()) / 12), 4)
# #     data.append(total_row)

# #     # Deduction rows
# #     def make_deduction_row(code, name, monthly_data):
# #         row = {
# #             "item_code": code,
# #             "item_name": name,
# #             "customer": "",
# #             "customer_group": "",
# #             "channel": ""
# #         }
# #         total_amt = 0
# #         for m in months:
# #             m_abbr = calendar.month_abbr[m].lower()
# #             amt = monthly_data.get(m, 0)
# #             row[f"{m_abbr}_sales"] = round(amt, 2)
# #             row[f"{m_abbr}_qty"] = 0
# #             row[f"{m_abbr}_rate"] = 0
# #             row[f"{m_abbr}_discount_rate"] = 0
# #             row[f"{m_abbr}_net_rate"] = 0
# #             total_amt += amt
# #         row["total_sales"] = round(total_amt, 2)
# #         row["total_qty"] = 0
# #         row["total_rate"] = 0
# #         row["total_net_rate"] = 0
# #         return row

# #     for code, monthly in monthly_deductions.items():
# #         data.append(make_deduction_row(code, code.replace("_", " ").title(), monthly))

# #     data.append(make_deduction_row("Total Deduction", "Total Deductions (All)", total_deduct_monthly))

# #     # Discount Rate summary row
# #     discount_rate_row = {
# #         "item_code": "Discount Rate",
# #         "item_name": "Discount Rate = Total Deduct / Total Qty",
# #         "customer": "",
# #         "customer_group": "",
# #         "channel": "",
# #     }
# #     for m in months:
# #         m_abbr = calendar.month_abbr[m].lower()
# #         val = discount_rate_per_month.get(m, 0)
# #         discount_rate_row[f"{m_abbr}_sales"] = round(val, 4)
# #         discount_rate_row[f"{m_abbr}_qty"] = 0
# #         discount_rate_row[f"{m_abbr}_rate"] = 0
# #         discount_rate_row[f"{m_abbr}_discount_rate"] = 0
# #         discount_rate_row[f"{m_abbr}_net_rate"] = 0
# #     discount_rate_row["total_sales"] = 0
# #     discount_rate_row["total_qty"] = 0
# #     discount_rate_row["total_rate"] = 0
# #     discount_rate_row["total_net_rate"] = 0
# #     data.append(discount_rate_row)

# #     # --- Add rebate amount breakdown rows per customer with customer group and channel ---
# #     for customer, monthly_rebates in rebate_by_customer.items():
# #         customer_group = rebate_customer_groups.get(customer, "")
# #         channel = get_channel(customer_group)
# #         row = {
# #             "item_code": "REBATE",
# #             "item_name": "Rebate Breakdown",
# #             "customer": customer,
# #             "customer_group": customer_group,
# #             "channel": channel,
# #         }
# #         total_rebate = 0
# #         for m in months:
# #             m_abbr = calendar.month_abbr[m].lower()
# #             rebate = monthly_rebates.get(m, 0)
# #             row[f"{m_abbr}_sales"] = round(-rebate, 2)
# #             row[f"{m_abbr}_qty"] = 0
# #             row[f"{m_abbr}_rate"] = 0
# #             row[f"{m_abbr}_discount_rate"] = 0
# #             row[f"{m_abbr}_net_rate"] = 0
# #             total_rebate += rebate

# #         row["total_sales"] = round(-total_rebate, 2)
# #         row["total_qty"] = 0
# #         row["total_rate"] = 0
# #         row["total_net_rate"] = 0
# #         data.append(row)

# #     # --- Add discount amount breakdown rows per customer with customer group and channel ---
# #     discount_by_customer = get_monthly_discount_by_customer(start_date, end_date)
# #     discount_customers = list(discount_by_customer.keys())
# #     discount_customer_groups = get_customer_groups(discount_customers)

# #     for customer, monthly_discounts in discount_by_customer.items():
# #         customer_group = discount_customer_groups.get(customer, "")
# #         channel = get_channel(customer_group)
# #         row = {
# #             "item_code": "DISCOUNT",
# #             "item_name": "Discount Breakdown",
# #             "customer": customer,
# #             "customer_group": customer_group,
# #             "channel": channel,
# #         }
# #         total_discount = 0
# #         for m in months:
# #             m_abbr = calendar.month_abbr[m].lower()
# #             discount = monthly_discounts.get(m, 0)
# #             row[f"{m_abbr}_sales"] = round(-discount, 2)
# #             row[f"{m_abbr}_qty"] = 0
# #             row[f"{m_abbr}_rate"] = 0
# #             row[f"{m_abbr}_discount_rate"] = 0
# #             row[f"{m_abbr}_net_rate"] = 0
# #             total_discount += discount

# #         row["total_sales"] = round(-total_discount, 2)
# #         row["total_qty"] = 0
# #         row["total_rate"] = 0
# #         row["total_net_rate"] = 0
# #         data.append(row)

# #     # --- Add Flyer, Listing, Registerion breakdown rows per customer from Credit Note ---
# #     credit_note_deductions = get_credit_note_deductions_by_customer(start_date, end_date)
# #     credit_note_customers = list(credit_note_deductions.keys())
# #     credit_note_customer_groups = get_customer_groups(credit_note_customers)

# #     for customer, deductions in credit_note_deductions.items():
# #         customer_group = credit_note_customer_groups.get(customer, "")
# #         channel = get_channel(customer_group)

# #         for deduction_type, monthly_values in deductions.items():
# #             row = {
# #                 "item_code": "CREDIT NOTE - " + deduction_type.upper(),
# #                 "item_name": f"{deduction_type} Deduction Breakdown",
# #                 "customer": customer,
# #                 "customer_group": customer_group,
# #                 "channel": channel,
# #             }
# #             total_amount = 0
# #             for m in months:
# #                 m_abbr = calendar.month_abbr[m].lower()
# #                 amount = monthly_values.get(m, 0)
# #                 row[f"{m_abbr}_sales"] = round(-amount, 2)
# #                 row[f"{m_abbr}_qty"] = 0
# #                 row[f"{m_abbr}_rate"] = 0
# #                 row[f"{m_abbr}_discount_rate"] = 0
# #                 row[f"{m_abbr}_net_rate"] = 0
# #                 total_amount += amount

# #             row["total_sales"] = round(-total_amount, 2)
# #             row["total_qty"] = 0
# #             row["total_rate"] = 0
# #             row["total_net_rate"] = 0
# #             data.append(row)

    

# #     return data


# # import frappe
# # from collections import defaultdict
# # import calendar

# # CHANNEL_MAPPING = {
# #     "DIRECT DISTRIBUTION DD": [
# #         "EATRIES", "LARGE GROCERY", "MINIMARKET", "SMALL GROCERY",
# #         "SUPERMARKET B", "WATER SHOP", "DIRECT DISTRIBUTION DD"
# #     ],
# #     "DISTRIBUTOR": [
# #         "DISTRIBUTOR A", "DISTRIBUTOR B", "DISTRIBUTOR C", "DISTRIBUTOR"
# #     ],
# #     "HOME DELIVERY HD": [
# #         "HOUSE", "MOSQUE", "OFFICE", "SCHOOL", "HOME DELIVERY HD"
# #     ],
# #     "HORECA HO": [
# #         "CAFÉ", "CARE", "CATERING", "COMMERCIAL", "GOVERNMENTAL",
# #         "HOTEL", "INSTITUTIONAL", "RESTAURANT", "HORECA HO", "CAFE"
# #     ],
# #     "KEY ACCOUNT KA": [
# #         "E-COMMERCE", "HYPERMARKET", "SUPERMARKET-A", "SUPERMARKET-B", "KEY ACCOUNT  KA"
# #     ],
# #     "MARKETING": [
# #         "MARKETING", "DONATION", "EVENT", "SPONSORSHIP"
# #     ],
# #     "OTHER MISCELLANEOUS": [
# #         "OTHER MISCELLANEOUS", "OTHER  MISCELLANEOUS"
# #     ],
# #     "WHOLESALE": [
# #         "WHOLESALE WS", "WAREHOUSE", "WHOLESALE A", "WHOLESALE-B", "WHOLESALE-C"
# #     ]
# # }

# # def get_channel(customer_group):
# #     if not customer_group:
# #         return ""
# #     customer_group_upper = customer_group.strip().upper()
# #     for channel, groups in CHANNEL_MAPPING.items():
# #         if customer_group_upper in (g.upper() for g in groups):
# #             return channel
# #     return ""

# # def execute(filters=None):
# #     filters = filters or {}
# #     year = filters.get("year")
# #     if not year:
# #         frappe.throw("Please select a year")

# #     columns = get_columns(year)
# #     data = get_data(year)
# #     return columns, data

# # def get_columns(year):
# #     months = [calendar.month_abbr[m] for m in range(1, 13)]
# #     columns = [
# #         {"label": "Channel", "fieldname": "channel", "fieldtype": "Data", "width": 150},
# #         {"label": "Item Code", "fieldname": "item_code", "fieldtype": "Data", "width": 140},
# #         {"label": "Item Name", "fieldname": "item_name", "fieldtype": "Data", "width": 250},
# #     ]
# #     for m in months:
# #         col_prefix = m.lower()
# #         columns.append({"label": f"{m} Sales", "fieldname": f"{col_prefix}_sales", "fieldtype": "Currency", "width": 100})
# #         columns.append({"label": f"{m} Qty", "fieldname": f"{col_prefix}_qty", "fieldtype": "Float", "width": 80})
# #         columns.append({"label": f"{m} Rate", "fieldname": f"{col_prefix}_rate", "fieldtype": "Currency", "width": 80})
# #         columns.append({"label": f"{m} Discount Rate", "fieldname": f"{col_prefix}_discount_rate", "fieldtype": "Float", "width": 110})
# #         columns.append({"label": f"{m} Net Rate", "fieldname": f"{col_prefix}_net_rate", "fieldtype": "Float", "width": 110})
# #     columns += [
# #         {"label": "Total Sales", "fieldname": "total_sales", "fieldtype": "Currency", "width": 110},
# #         {"label": "Total Qty", "fieldname": "total_qty", "fieldtype": "Float", "width": 90},
# #         {"label": "Total Rate", "fieldname": "total_rate", "fieldtype": "Currency", "width": 90},
# #         {"label": "Total Net Rate", "fieldname": "total_net_rate", "fieldtype": "Currency", "width": 110},
# #     ]
# #     return columns

# # def get_monthly_rebate_by_channel(start_date, end_date):
# #     results = frappe.db.sql("""
# #         SELECT
# #             cu.customer_group,
# #             MONTH(r.posting_date) AS month,
# #             SUM(r.rebate_received_amount) AS rebate_amount
# #         FROM `tabRebate` r
# #         JOIN `tabCustomer` cu ON cu.name = r.party
# #         WHERE
# #             r.docstatus = 1
# #             AND r.party_type = 'Customer'
# #             AND r.posting_date BETWEEN %s AND %s
# #         GROUP BY cu.customer_group, MONTH(r.posting_date)
# #     """, (start_date, end_date), as_dict=True)

# #     rebate_data = defaultdict(lambda: defaultdict(float))
# #     for row in results:
# #         channel = get_channel(row.customer_group)
# #         rebate_data[channel][row.month] += row.rebate_amount or 0

# #     return rebate_data

# # def get_monthly_discount_by_channel(start_date, end_date):
# #     results = frappe.db.sql("""
# #         SELECT
# #             cu.customer_group,
# #             MONTH(cp.posting_date) AS month,
# #             SUM(cp.promtion_amount) AS discount_amount
# #         FROM `tabCustomer Promotion` cp
# #         JOIN `tabCustomer` cu ON cu.name = cp.customer
# #         WHERE
# #             cp.docstatus = 1
# #             AND cp.posting_date BETWEEN %s AND %s
# #         GROUP BY cu.customer_group, MONTH(cp.posting_date)
# #     """, (start_date, end_date), as_dict=True)

# #     discount_data = defaultdict(lambda: defaultdict(float))
# #     for row in results:
# #         channel = get_channel(row.customer_group)
# #         discount_data[channel][row.month] += row.discount_amount or 0

# #     return discount_data

# # def get_credit_note_deductions_by_channel(start_date, end_date):
# #     deduction_accounts = {
# #         "Flyer": "516107 - Flyer Fees -رسوم فلاير - ABNA",
# #         "Listing": "516102 - Listing Fees -رسوم أدخال اصناف - ABNA",
# #         "Registerion": "516101 - Registerion Fees -رسوم التسجيل - ABNA"
# #     }

# #     accounts_list = list(deduction_accounts.values())
# #     placeholders = ', '.join(['%s'] * len(accounts_list))

# #     query = f"""
# #         SELECT
# #             cu.customer_group,
# #             MONTH(cn.posting_date) AS month,
# #             cni.account,
# #             SUM(cni.debit - cni.credit) AS amount
# #         FROM `tabCredit Note` cn
# #         JOIN `tabJournal Entry Account` cni ON cni.parent = cn.name
# #         JOIN `tabCustomer` cu ON cu.name = cn.customer
# #         WHERE
# #             cn.docstatus = 1
# #             AND cn.posting_date BETWEEN %s AND %s
# #             AND cni.account IN ({placeholders})
# #         GROUP BY cu.customer_group, cni.account, MONTH(cn.posting_date)
# #     """

# #     params = [start_date, end_date] + accounts_list

# #     results = frappe.db.sql(query, params, as_dict=True)

# #     data = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))
# #     account_to_type = {v: k for k, v in deduction_accounts.items()}

# #     for row in results:
# #         channel = get_channel(row.customer_group)
# #         deduction_type = account_to_type.get(row.account, "Unknown")
# #         data[channel][deduction_type][row.month] += row.amount or 0

# #     return data

# # def get_data(year):
# #     start_date = f"{year}-01-01"
# #     end_date = f"{year}-12-31"

# #     # All relevant item codes
# #     item_codes = (
# #         '6287016760027', '6287016760041', '6287016760034',
# #         '6287016760058', '6287016760119', '6287016760157', '6287016760164'
# #     )

# #     # Define item grouping mapping (child item_code -> parent item_code)
# #     item_group_map = {
# #         '6287016760119': '6287016760027',
# #         '6287016760157': '6287016760027',
# #         '6287016760058': '6287016760041',
# #         '6287016760164': '6287016760041',
# #     }

# #     deduction_accounts = {
# #         "Rebate": "41010105 - Sales Rebate/Trade Discount -حسم المبيعات /الخصم التجاري - ABNA",
# #         "Registerion": "516101 - Registerion Fees -رسوم التسجيل - ABNA",
# #         "Listing": "516102 - Listing Fees -رسوم أدخال اصناف - ABNA",
# #         "Flyer": "516107 - Flyer Fees -رسوم فلاير - ABNA",
# #         "Discount": "41010103 - Discount Allowance -الخصم المسموح به - ABNA"
# #     }

# #     months = range(1, 13)

# #     sales_results = frappe.db.sql("""
# #         SELECT
# #             sii.item_code,
# #             sii.item_name,
# #             si.customer_group,
# #             MONTH(si.posting_date) AS month,
# #             SUM(sii.qty) AS total_qty,
# #             SUM(sii.base_net_amount) AS total_sales
# #         FROM `tabSales Invoice` si
# #         JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
# #         WHERE
# #             si.docstatus = 1
# #             AND si.posting_date BETWEEN %s AND %s
# #             AND sii.item_code IN %s
# #         GROUP BY sii.item_code, si.customer_group, month
# #     """, (start_date, end_date, item_codes), as_dict=True)

# #     sales_data = defaultdict(lambda: defaultdict(lambda: {"sales": 0, "qty": 0}))
# #     meta_data = {}
# #     channel_totals = defaultdict(lambda: defaultdict(lambda: {"sales": 0, "qty": 0}))

# #     for r in sales_results:
# #         # Map child item to parent if exists
# #         parent_item_code = item_group_map.get(r.item_code, r.item_code)
# #         channel = get_channel(r.customer_group)
# #         key = (channel, parent_item_code)

# #         sales_data[key][r.month]["sales"] += r.total_sales or 0
# #         sales_data[key][r.month]["qty"] += r.total_qty or 0

# #         # Aggregate channel-wise totals
# #         channel_totals[channel][r.month]["sales"] += r.total_sales or 0
# #         channel_totals[channel][r.month]["qty"] += r.total_qty or 0

# #         if key not in meta_data:
# #             # Get parent item name from DB or fallback
# #             if parent_item_code == r.item_code:
# #                 item_name = r.item_name
# #             else:
# #                 item_name = frappe.db.get_value("Item", parent_item_code, "item_name") or r.item_name

# #             meta_data[key] = {
# #                 "item_name": item_name,
# #                 "channel": channel,
# #                 "item_code": parent_item_code
# #             }

# #     def get_gl_monthly(account):
# #         gl_rows = frappe.db.sql("""
# #             SELECT MONTH(posting_date) AS month, SUM(debit - credit) AS amount
# #             FROM `tabGL Entry`
# #             WHERE account = %s AND posting_date BETWEEN %s AND %s
# #             GROUP BY month
# #         """, (account, start_date, end_date), as_dict=True)
# #         return {row.month: row.amount or 0 for row in gl_rows}

# #     monthly_deductions = {code: get_gl_monthly(account) for code, account in deduction_accounts.items()}
# #     months_list = list(months)
# #     total_deduct_monthly = {m: sum(monthly_deductions[code].get(m, 0) for code in deduction_accounts) for m in months}

# #     # Calculate channel-wise total deductions
# #     rebate_by_channel = get_monthly_rebate_by_channel(start_date, end_date)
# #     discount_by_channel = get_monthly_discount_by_channel(start_date, end_date)
# #     credit_note_deductions = get_credit_note_deductions_by_channel(start_date, end_date)

# #     total_deductions_by_channel = defaultdict(lambda: defaultdict(float))
# #     for channel, monthly_data in rebate_by_channel.items():
# #         for m, v in monthly_data.items():
# #             total_deductions_by_channel[channel][m] += v
# #     for channel, monthly_data in discount_by_channel.items():
# #         for m, v in monthly_data.items():
# #             total_deductions_by_channel[channel][m] += v
# #     for channel, deduction_types in credit_note_deductions.items():
# #         for monthly_data in deduction_types.values():
# #             for m, v in monthly_data.items():
# #                 total_deductions_by_channel[channel][m] += v

# #     # Calculate channel-wise discount rate (Total Deductions / Sales Qty)
# #     channel_discount_rate = defaultdict(lambda: defaultdict(float))
# #     for channel in channel_totals:
# #         for m in months:
# #             total_qty = channel_totals[channel][m]["qty"]
# #             total_deductions = total_deductions_by_channel[channel][m]
# #             channel_discount_rate[channel][m] = (total_deductions / total_qty) if total_qty else 0

# #     # Overall discount rate for net rate calculations (unchanged)
# #     discount_rate_per_month = {}
# #     for m in months:
# #         total_qty_month = sum(channel_totals[channel][m]["qty"] for channel in channel_totals)
# #         discount_rate_per_month[m] = (total_deduct_monthly.get(m, 0) / total_qty_month) if total_qty_month else 0

# #     data = []
# #     totals_sales = defaultdict(float)
# #     totals_qty = defaultdict(float)

# #     # Sales Data Rows grouped by Channel and Item
# #     for key in sales_data:
# #         channel, item_code = key
# #         meta = meta_data.get(key, {})
# #         row = {
# #             "channel": channel,
# #             "item_code": item_code,
# #             "item_name": meta.get("item_name", "")
# #         }
# #         total_sales_sum = 0
# #         total_qty_sum = 0

# #         for m in months:
# #             m_abbr = calendar.month_abbr[m].lower()
# #             sales = sales_data[key][m]["sales"]
# #             qty = sales_data[key][m]["qty"]
# #             rate = (sales / qty) if qty else 0

# #             totals_sales[m] += sales
# #             totals_qty[m] += qty

# #             discount_rate = discount_rate_per_month.get(m, 0)
# #             net_rate = rate - discount_rate

# #             row[f"{m_abbr}_sales"] = round(sales, 2)
# #             row[f"{m_abbr}_qty"] = round(qty, 2)
# #             row[f"{m_abbr}_rate"] = round(rate, 2)
# #             row[f"{m_abbr}_discount_rate"] = round(discount_rate, 4)
# #             row[f"{m_abbr}_net_rate"] = round(net_rate, 4)

# #             total_sales_sum += sales
# #             total_qty_sum += qty

# #         total_rate = (total_sales_sum / total_qty_sum) if total_qty_sum else 0
# #         total_discount = sum(discount_rate_per_month.get(m, 0) for m in months) / 12
# #         total_net_rate = total_rate - total_discount

# #         row["total_sales"] = round(total_sales_sum, 2)
# #         row["total_qty"] = round(total_qty_sum, 2)
# #         row["total_rate"] = round(total_rate, 2)
# #         row["total_net_rate"] = round(total_net_rate, 4)
# #         data.append(row)

# #     # Channel-wise total rows
# #     for channel in channel_totals:
# #         row = {
# #             "channel": channel,
# #             "item_code": "",
# #             "item_name": f"Total for {channel}",
# #         }
# #         total_sales_sum = 0
# #         total_qty_sum = 0

# #         for m in months:
# #             m_abbr = calendar.month_abbr[m].lower()
# #             sales = channel_totals[channel][m]["sales"]
# #             qty = channel_totals[channel][m]["qty"]
# #             rate = (sales / qty) if qty else 0
# #             discount_rate = discount_rate_per_month.get(m, 0)
# #             net_rate = rate - discount_rate

# #             row[f"{m_abbr}_sales"] = round(sales, 2)
# #             row[f"{m_abbr}_qty"] = round(qty, 2)
# #             row[f"{m_abbr}_rate"] = round(rate, 2)
# #             row[f"{m_abbr}_discount_rate"] = round(discount_rate, 4)
# #             row[f"{m_abbr}_net_rate"] = round(net_rate, 4)

# #             total_sales_sum += sales
# #             total_qty_sum += qty

# #         total_rate = (total_sales_sum / total_qty_sum) if total_qty_sum else 0
# #         total_net_rate = total_rate - (sum(discount_rate_per_month.get(m, 0) for m in months) / 12)

# #         row["total_sales"] = round(total_sales_sum, 2)
# #         row["total_qty"] = round(total_qty_sum, 2)
# #         row["total_rate"] = round(total_rate, 2)
# #         row["total_net_rate"] = round(total_net_rate, 4)
# #         data.append(row)

# #     # Total row for all sales grouped by channel
# #     total_row = {
# #         "channel": "TOTAL",
# #         "item_code": "",
# #         "item_name": "Total of All Items",
# #     }
# #     total_sales_sum_all = 0
# #     total_qty_sum_all = 0
# #     for m in months:
# #         m_abbr = calendar.month_abbr[m].lower()
# #         sales = totals_sales[m]
# #         qty = totals_qty[m]
# #         rate = (sales / qty) if qty else 0
# #         discount_rate = discount_rate_per_month.get(m, 0)
# #         net_rate = rate - discount_rate

# #         total_row[f"{m_abbr}_sales"] = round(sales, 2)
# #         total_row[f"{m_abbr}_qty"] = round(qty, 2)
# #         total_row[f"{m_abbr}_rate"] = round(rate, 2)
# #         total_row[f"{m_abbr}_discount_rate"] = round(discount_rate, 4)
# #         total_row[f"{m_abbr}_net_rate"] = round(net_rate, 4)

# #         total_sales_sum_all += sales
# #         total_qty_sum_all += qty

# #     total_row["total_sales"] = round(total_sales_sum_all, 2)
# #     total_row["total_qty"] = round(total_qty_sum_all, 2)
# #     total_row["total_rate"] = round((total_sales_sum_all / total_qty_sum_all) if total_qty_sum_all else 0, 2)
# #     total_row["total_net_rate"] = round(total_row["total_rate"] - (sum(discount_rate_per_month.values()) / 12), 4)
# #     data.append(total_row)

# #     # Deduction rows by channel
# #     def make_deduction_row(channel, code, name, monthly_data):
# #         row = {
# #             "channel": channel,
# #             "item_code": code,
# #             "item_name": name,
# #         }
# #         total_amt = 0
# #         for m in months:
# #             m_abbr = calendar.month_abbr[m].lower()
# #             amt = monthly_data.get(m, 0)
# #             row[f"{m_abbr}_sales"] = round(-amt, 2)  # Negative as deduction
# #             row[f"{m_abbr}_qty"] = 0
# #             row[f"{m_abbr}_rate"] = 0
# #             row[f"{m_abbr}_discount_rate"] = 0
# #             row[f"{m_abbr}_net_rate"] = 0
# #             total_amt += amt
# #         row["total_sales"] = round(-total_amt, 2)
# #         row["total_qty"] = 0
# #         row["total_rate"] = 0
# #         row["total_net_rate"] = 0
# #         return row

# #     # Add rebate rows grouped by channel
# #     for channel, monthly_data in rebate_by_channel.items():
# #         data.append(make_deduction_row(channel, "REBATE", "Rebate Breakdown", monthly_data))

# #     # Add discount rows grouped by channel
# #     for channel, monthly_data in discount_by_channel.items():
# #         data.append(make_deduction_row(channel, "DISCOUNT", "Discount Breakdown", monthly_data))

# #     # Add credit note deduction rows grouped by channel and deduction type
# #     for channel, deduction_types in credit_note_deductions.items():
# #         for deduction_type, monthly_values in deduction_types.items():
# #             data.append(make_deduction_row(channel, f"CREDIT NOTE - {deduction_type.upper()}",
# #                                           f"{deduction_type} Deduction Breakdown", monthly_values))

# #     # Total deductions by channel row
# #     for channel, monthly_totals in total_deductions_by_channel.items():
# #         data.append(make_deduction_row(channel, "TOTAL DEDUCTION", "Total Deductions (All)", monthly_totals))

# #     # Channel-wise discount rate rows (Total Deductions / Sales Qty), only if non-zero
# #     for channel in channel_totals:
# #         # Check if any month has a non-zero discount rate
# #         has_non_zero_discount = any(channel_discount_rate[channel][m] != 0 for m in months)
# #         if has_non_zero_discount:
# #             row = {
# #                 "channel": channel,
# #                 "item_code": "",
# #                 "item_name": f"Discount Rate for {channel} (Total Deductions / Sales Qty)",
# #             }
# #             for m in months:
# #                 m_abbr = calendar.month_abbr[m].lower()
# #                 discount_rate = channel_discount_rate[channel][m]
# #                 row[f"{m_abbr}_sales"] = round(discount_rate, 4)
# #                 row[f"{m_abbr}_qty"] = 0
# #                 row[f"{m_abbr}_rate"] = 0
# #                 row[f"{m_abbr}_discount_rate"] = 0
# #                 row[f"{m_abbr}_net_rate"] = 0
# #             row["total_sales"] = 0
# #             row["total_qty"] = 0
# #             row["total_rate"] = 0
# #             row["total_net_rate"] = 0
# #             data.append(row)

# #     return data


# import frappe
# from collections import defaultdict
# import calendar

# CHANNEL_MAPPING = {
#     "DIRECT DISTRIBUTION DD": [
#         "EATRIES", "LARGE GROCERY", "MINIMARKET", "SMALL GROCERY",
#         "SUPERMARKET B", "WATER SHOP", "DIRECT DISTRIBUTION DD"
#     ],
#     "DISTRIBUTOR": [
#         "DISTRIBUTOR A", "DISTRIBUTOR B", "DISTRIBUTOR C", "DISTRIBUTOR"
#     ],
#     "HOME DELIVERY HD": [
#         "HOUSE", "MOSQUE", "OFFICE", "SCHOOL", "HOME DELIVERY HD"
#     ],
#     "HORECA HO": [
#         "CAFÉ", "CARE", "CATERING", "COMMERCIAL", "GOVERNMENTAL",
#         "HOTEL", "INSTITUTIONAL", "RESTAURANT", "HORECA HO", "CAFE"
#     ],
#     "KEY ACCOUNT KA": [
#         "E-COMMERCE", "HYPERMARKET", "SUPERMARKET-A", "SUPERMARKET-B", "KEY ACCOUNT  KA"
#     ],
#     "MARKETING": [
#         "MARKETING", "DONATION", "EVENT", "SPONSORSHIP"
#     ],
#     "OTHER MISCELLANEOUS": [
#         "OTHER MISCELLANEOUS", "OTHER  MISCELLANEOUS"
#     ],
#     "WHOLESALE": [
#         "WHOLESALE WS", "WAREHOUSE", "WHOLESALE A", "WHOLESALE-B", "WHOLESALE-C"
#     ]
# }

# def get_channel(customer_group):
#     if not customer_group:
#         return ""
#     customer_group_upper = customer_group.strip().upper()
#     for channel, groups in CHANNEL_MAPPING.items():
#         if customer_group_upper in (g.upper() for g in groups):
#             return channel
#     return ""

# def execute(filters=None):
#     filters = filters or {}
#     year = filters.get("year")
#     if not year:
#         frappe.throw("Please select a year")

#     columns = get_columns(year)
#     data = get_data(year)
#     return columns, data

# def get_columns(year):
#     months = [calendar.month_abbr[m] for m in range(1, 13)]
#     columns = [
#         {"label": "Channel", "fieldname": "channel", "fieldtype": "Data", "width": 150},
#         {"label": "Item Code", "fieldname": "item_code", "fieldtype": "Data", "width": 140},
#         {"label": "Item Name", "fieldname": "item_name", "fieldtype": "Data", "width": 250},
#     ]

#     for m in months:
#         m_lower = m.lower()
#         columns.append({"label": f"{m} Sales", "fieldname": f"{m_lower}_sales", "fieldtype": "Currency", "width": 100})
#         columns.append({"label": f"{m} Qty", "fieldname": f"{m_lower}_qty", "fieldtype": "Float", "width": 80})
#         columns.append({"label": f"{m} Rate", "fieldname": f"{m_lower}_rate", "fieldtype": "Currency", "width": 80})
#         # columns.append({"label": f"{m} Discount Rate", "fieldname": f"{m_lower}_discount_rate", "fieldtype": "Float", "width": 110})
#         columns.append({"label": f"{m} Net Rate", "fieldname": f"{m_lower}_net_rate", "fieldtype": "Float", "width": 110})
#         columns.append({"label": f"{m} Channel Discount", "fieldname": f"{m_lower}_channel_discount", "fieldtype": "Currency", "width": 120})
#         columns.append({"label": f"{m} Channel Discount Rate", "fieldname": f"{m_lower}_channel_discount_rate", "fieldtype": "Float", "width": 130})

#     columns += [
#         {"label": "Total Sales", "fieldname": "total_sales", "fieldtype": "Currency", "width": 110},
#         {"label": "Total Qty", "fieldname": "total_qty", "fieldtype": "Float", "width": 90},
#         {"label": "Total Rate", "fieldname": "total_rate", "fieldtype": "Currency", "width": 90},
#         {"label": "Total Net Rate", "fieldname": "total_net_rate", "fieldtype": "Currency", "width": 110},
#     ]
#     return columns

# def get_monthly_rebate_by_channel(start_date, end_date):
#     results = frappe.db.sql("""
#         SELECT
#             cu.customer_group,
#             MONTH(r.posting_date) AS month,
#             SUM(r.rebate_received_amount) AS rebate_amount
#         FROM `tabRebate` r
#         JOIN `tabCustomer` cu ON cu.name = r.party
#         WHERE
#             r.docstatus = 1
#             AND r.party_type = 'Customer'
#             AND r.posting_date BETWEEN %s AND %s
#         GROUP BY cu.customer_group, MONTH(r.posting_date)
#     """, (start_date, end_date), as_dict=True)

#     rebate_data = defaultdict(lambda: defaultdict(float))
#     for row in results:
#         channel = get_channel(row.customer_group)
#         rebate_data[channel][row.month] += row.rebate_amount or 0

#     return rebate_data

# def get_monthly_discount_by_channel(start_date, end_date):
#     results = frappe.db.sql("""
#         SELECT
#             cu.customer_group,
#             MONTH(cp.posting_date) AS month,
#             SUM(cp.promtion_amount) AS discount_amount
#         FROM `tabCustomer Promotion` cp
#         JOIN `tabCustomer` cu ON cu.name = cp.customer
#         WHERE
#             cp.docstatus = 1
#             AND cp.posting_date BETWEEN %s AND %s
#         GROUP BY cu.customer_group, MONTH(cp.posting_date)
#     """, (start_date, end_date), as_dict=True)

#     discount_data = defaultdict(lambda: defaultdict(float))
#     for row in results:
#         channel = get_channel(row.customer_group)
#         discount_data[channel][row.month] += row.discount_amount or 0

#     return discount_data

# def get_credit_note_deductions_by_channel(start_date, end_date):
#     deduction_accounts = {
#         "Flyer": "516107 - Flyer Fees -رسوم فلاير - ABNA",
#         "Listing": "516102 - Listing Fees -رسوم أدخال اصناف - ABNA",
#         "Registerion": "516101 - Registerion Fees -رسوم التسجيل - ABNA"
#     }

#     accounts_list = list(deduction_accounts.values())
#     placeholders = ', '.join(['%s'] * len(accounts_list))

#     query = f"""
#         SELECT
#             cu.customer_group,
#             MONTH(cn.posting_date) AS month,
#             cni.account,
#             SUM(cni.debit - cni.credit) AS amount
#         FROM `tabCredit Note` cn
#         JOIN `tabJournal Entry Account` cni ON cni.parent = cn.name
#         JOIN `tabCustomer` cu ON cu.name = cn.customer
#         WHERE
#             cn.docstatus = 1
#             AND cn.posting_date BETWEEN %s AND %s
#             AND cni.account IN ({placeholders})
#         GROUP BY cu.customer_group, cni.account, MONTH(cn.posting_date)
#     """

#     params = [start_date, end_date] + accounts_list

#     results = frappe.db.sql(query, params, as_dict=True)

#     data = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))
#     account_to_type = {v: k for k, v in deduction_accounts.items()}

#     for row in results:
#         channel = get_channel(row.customer_group)
#         deduction_type = account_to_type.get(row.account, "Unknown")
#         data[channel][deduction_type][row.month] += row.amount or 0

#     return data

# # def get_data(year):
# #     start_date = f"{year}-01-01"
# #     end_date = f"{year}-12-31"

# #     # All relevant item codes
# #     item_codes = (
# #         '6287016760027', '6287016760041', '6287016760034',
# #         '6287016760058', '6287016760119', '6287016760157', '6287016760164'
# #     )

# #     # Define item grouping mapping (child item_code -> parent item_code)
# #     item_group_map = {
# #         '6287016760119': '6287016760027',
# #         '6287016760157': '6287016760027',
# #         '6287016760058': '6287016760041',
# #         '6287016760164': '6287016760041',
# #     }

# #     deduction_accounts = {
# #         "Rebate": "41010105 - Sales Rebate/Trade Discount -حسم المبيعات /الخصم التجاري - ABNA",
# #         "Registerion": "516101 - Registerion Fees -رسوم التسجيل - ABNA",
# #         "Listing": "516102 - Listing Fees -رسوم أدخال اصناف - ABNA",
# #         "Flyer": "516107 - Flyer Fees -رسوم فلاير - ABNA",
# #         "Discount": "41010103 - Discount Allowance -الخصم المسموح به - ABNA"
# #     }

# #     months = range(1, 13)

# #     sales_results = frappe.db.sql("""
# #         SELECT
# #             sii.item_code,
# #             sii.item_name,
# #             si.customer_group,
# #             MONTH(si.posting_date) AS month,
# #             SUM(sii.qty) AS total_qty,
# #             SUM(sii.base_net_amount) AS total_sales
# #         FROM `tabSales Invoice` si
# #         JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
# #         WHERE
# #             si.docstatus = 1
# #             AND si.posting_date BETWEEN %s AND %s
# #             AND sii.item_code IN %s
# #         GROUP BY sii.item_code, si.customer_group, month
# #     """, (start_date, end_date, item_codes), as_dict=True)

# #     sales_data = defaultdict(lambda: defaultdict(lambda: {"sales": 0, "qty": 0}))
# #     meta_data = {}
# #     channel_totals = defaultdict(lambda: defaultdict(lambda: {"sales": 0, "qty": 0}))

# #     for r in sales_results:
# #         # Map child item to parent if exists
# #         parent_item_code = item_group_map.get(r.item_code, r.item_code)
# #         channel = get_channel(r.customer_group)
# #         key = (channel, parent_item_code)

# #         sales_data[key][r.month]["sales"] += r.total_sales or 0
# #         sales_data[key][r.month]["qty"] += r.total_qty or 0

# #         # Aggregate channel-wise totals
# #         channel_totals[channel][r.month]["sales"] += r.total_sales or 0
# #         channel_totals[channel][r.month]["qty"] += r.total_qty or 0

# #         if key not in meta_data:
# #             # Get parent item name from DB or fallback
# #             if parent_item_code == r.item_code:
# #                 item_name = r.item_name
# #             else:
# #                 item_name = frappe.db.get_value("Item", parent_item_code, "item_name") or r.item_name

# #             meta_data[key] = {
# #                 "item_name": item_name,
# #                 "channel": channel,
# #                 "item_code": parent_item_code
# #             }

# #     def get_gl_monthly(account):
# #         gl_rows = frappe.db.sql("""
# #             SELECT MONTH(posting_date) AS month, SUM(debit - credit) AS amount
# #             FROM `tabGL Entry`
# #             WHERE account = %s AND posting_date BETWEEN %s AND %s
# #             GROUP BY month
# #         """, (account, start_date, end_date), as_dict=True)
# #         return {row.month: row.amount or 0 for row in gl_rows}

# #     monthly_deductions = {code: get_gl_monthly(account) for code, account in deduction_accounts.items()}
# #     months_list = list(months)
# #     total_deduct_monthly = {m: sum(monthly_deductions[code].get(m, 0) for code in deduction_accounts) for m in months}

# #     # Calculate channel-wise total deductions
# #     rebate_by_channel = get_monthly_rebate_by_channel(start_date, end_date)
# #     discount_by_channel = get_monthly_discount_by_channel(start_date, end_date)
# #     credit_note_deductions = get_credit_note_deductions_by_channel(start_date, end_date)

# #     total_deductions_by_channel = defaultdict(lambda: defaultdict(float))
# #     for channel, monthly_data in rebate_by_channel.items():
# #         for m, v in monthly_data.items():
# #             total_deductions_by_channel[channel][m] += v
# #     for channel, monthly_data in discount_by_channel.items():
# #         for m, v in monthly_data.items():
# #             total_deductions_by_channel[channel][m] += v
# #     for channel, deduction_types in credit_note_deductions.items():
# #         for monthly_data in deduction_types.values():
# #             for m, v in monthly_data.items():
# #                 total_deductions_by_channel[channel][m] += v

# #     # Calculate channel-wise discount rate (Total Deductions / Sales Qty)
# #     channel_discount_rate = defaultdict(lambda: defaultdict(float))
# #     for channel in channel_totals:
# #         for m in months:
# #             total_qty = channel_totals[channel][m]["qty"]
# #             total_deductions = total_deductions_by_channel[channel][m]
# #             channel_discount_rate[channel][m] = (total_deductions / total_qty) if total_qty else 0

# #     # Overall discount rate for net rate calculations (unchanged)
# #     discount_rate_per_month = {}
# #     for m in months:
# #         total_qty_month = sum(channel_totals[channel][m]["qty"] for channel in channel_totals)
# #         discount_rate_per_month[m] = (total_deduct_monthly.get(m, 0) / total_qty_month) if total_qty_month else 0

# #     data = []
# #     totals_sales = defaultdict(float)
# #     totals_qty = defaultdict(float)

# #     # Sales Data Rows grouped by Channel and Item
# #     for key in sales_data:
# #         channel, item_code = key
# #         meta = meta_data.get(key, {})
# #         row = {
# #             "channel": channel,
# #             "item_code": item_code,
# #             "item_name": meta.get("item_name", "")
# #         }
# #         total_sales_sum = 0
# #         total_qty_sum = 0

# #         for m in months:
# #             m_abbr = calendar.month_abbr[m].lower()
# #             sales = sales_data[key][m]["sales"]
# #             qty = sales_data[key][m]["qty"]
# #             rate = (sales / qty) if qty else 0

# #             totals_sales[m] += sales
# #             totals_qty[m] += qty

# #             discount_rate = discount_rate_per_month.get(m, 0)
# #             net_rate = rate - discount_rate
# #             channel_disc = total_deductions_by_channel[channel].get(m, 0)
# #             channel_disc_rate = channel_discount_rate[channel].get(m, 0)

# #             row[f"{m_abbr}_sales"] = round(sales, 2)
# #             row[f"{m_abbr}_qty"] = round(qty, 2)
# #             row[f"{m_abbr}_rate"] = round(rate, 2)
# #             row[f"{m_abbr}_discount_rate"] = round(discount_rate, 4)
# #             row[f"{m_abbr}_net_rate"] = round(net_rate, 4)
# #             row[f"{m_abbr}_channel_discount"] = round(channel_disc, 2)
# #             row[f"{m_abbr}_channel_discount_rate"] = round(channel_disc_rate, 4)

# #             total_sales_sum += sales
# #             total_qty_sum += qty

# #         total_rate = (total_sales_sum / total_qty_sum) if total_qty_sum else 0
# #         total_discount = sum(discount_rate_per_month.get(m, 0) for m in months) / 12
# #         total_net_rate = total_rate - total_discount

# #         row["total_sales"] = round(total_sales_sum, 2)
# #         row["total_qty"] = round(total_qty_sum, 2)
# #         row["total_rate"] = round(total_rate, 2)
# #         row["total_net_rate"] = round(total_net_rate, 4)
# #         data.append(row)

# #     # Channel-wise total rows
# #     for channel in channel_totals:
# #         row = {
# #             "channel": channel,
# #             "item_code": "",
# #             "item_name": f"Total for {channel}",
# #         }
# #         total_sales_sum = 0
# #         total_qty_sum = 0

# #         for m in months:
# #             m_abbr = calendar.month_abbr[m].lower()
# #             sales = channel_totals[channel][m]["sales"]
# #             qty = channel_totals[channel][m]["qty"]
# #             rate = (sales / qty) if qty else 0
# #             discount_rate = discount_rate_per_month.get(m, 0)
# #             net_rate = rate - discount_rate
# #             channel_disc = total_deductions_by_channel[channel].get(m, 0)
# #             channel_disc_rate = channel_discount_rate[channel].get(m, 0)

# #             row[f"{m_abbr}_sales"] = round(sales, 2)
# #             row[f"{m_abbr}_qty"] = round(qty, 2)
# #             row[f"{m_abbr}_rate"] = round(rate, 2)
# #             row[f"{m_abbr}_discount_rate"] = round(discount_rate, 4)
# #             row[f"{m_abbr}_net_rate"] = round(net_rate, 4)
# #             row[f"{m_abbr}_channel_discount"] = round(channel_disc, 2)
# #             row[f"{m_abbr}_channel_discount_rate"] = round(channel_disc_rate, 4)

# #             total_sales_sum += sales
# #             total_qty_sum += qty

# #         total_rate = (total_sales_sum / total_qty_sum) if total_qty_sum else 0
# #         total_net_rate = total_rate - (sum(discount_rate_per_month.get(m, 0) for m in months) / 12)

# #         row["total_sales"] = round(total_sales_sum, 2)
# #         row["total_qty"] = round(total_qty_sum, 2)
# #         row["total_rate"] = round(total_rate, 2)
# #         row["total_net_rate"] = round(total_net_rate, 4)
# #         data.append(row)

# #     # Total row for all sales grouped by channel
# #     total_row = {
# #         "channel": "TOTAL",
# #         "item_code": "",
# #         "item_name": "Total of All Items",
# #     }
# #     total_sales_sum_all = 0
# #     total_qty_sum_all = 0
# #     for m in months:
# #         m_abbr = calendar.month_abbr[m].lower()
# #         sales = totals_sales[m]
# #         qty = totals_qty[m]
# #         rate = (sales / qty) if qty else 0
# #         discount_rate = discount_rate_per_month.get(m, 0)
# #         net_rate = rate - discount_rate
# #         channel_disc = sum(total_deductions_by_channel[ch].get(m, 0) for ch in channel_totals)
# #         channel_disc_rate = sum(channel_discount_rate[ch].get(m, 0) for ch in channel_totals) / len(channel_totals) if channel_totals else 0

# #         total_row[f"{m_abbr}_sales"] = round(sales, 2)
# #         total_row[f"{m_abbr}_qty"] = round(qty, 2)
# #         total_row[f"{m_abbr}_rate"] = round(rate, 2)
# #         total_row[f"{m_abbr}_discount_rate"] = round(discount_rate, 4)
# #         total_row[f"{m_abbr}_net_rate"] = round(net_rate, 4)
# #         total_row[f"{m_abbr}_channel_discount"] = round(channel_disc, 2)
# #         total_row[f"{m_abbr}_channel_discount_rate"] = round(channel_disc_rate, 4)

# #         total_sales_sum_all += sales
# #         total_qty_sum_all += qty

# #     total_rate_all = (total_sales_sum_all / total_qty_sum_all) if total_qty_sum_all else 0
# #     total_net_rate_all = total_rate_all - (sum(discount_rate_per_month.get(m, 0) for m in months) / 12)
# #     total_row["total_sales"] = round(total_sales_sum_all, 2)
# #     total_row["total_qty"] = round(total_qty_sum_all, 2)
# #     total_row["total_rate"] = round(total_rate_all, 2)
# #     total_row["total_net_rate"] = round(total_net_rate_all, 4)

# #     data.append(total_row)

# #     return data

# def get_data(year):
#     start_date = f"{year}-01-01"
#     end_date = f"{year}-12-31"

#     # All relevant item codes
#     item_codes = (
#         '6287016760027', '6287016760041', '6287016760034',
#         '6287016760058', '6287016760119', '6287016760157', '6287016760164'
#     )

#     # Define item grouping mapping (child item_code -> parent item_code)
#     item_group_map = {
#         '6287016760119': '6287016760027',
#         '6287016760157': '6287016760027',
#         '6287016760058': '6287016760041',
#         '6287016760164': '6287016760041',
#     }

#     deduction_accounts = {
#         "Rebate": "41010105 - Sales Rebate/Trade Discount -حسم المبيعات /الخصم التجاري - ABNA",
#         "Registerion": "516101 - Registerion Fees -رسوم التسجيل - ABNA",
#         "Listing": "516102 - Listing Fees -رسوم أدخال اصناف - ABNA",
#         "Flyer": "516107 - Flyer Fees -رسوم فلاير - ABNA",
#         "Discount": "41010103 - Discount Allowance -الخصم المسموح به - ABNA"
#     }

#     months = range(1, 13)

#     sales_results = frappe.db.sql("""
#         SELECT
#             sii.item_code,
#             sii.item_name,
#             si.customer_group,
#             MONTH(si.posting_date) AS month,
#             SUM(sii.qty) AS total_qty,
#             SUM(sii.base_net_amount) AS total_sales
#         FROM `tabSales Invoice` si
#         JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
#         WHERE
#             si.docstatus = 1
#             AND si.posting_date BETWEEN %s AND %s
#             AND sii.item_code IN %s
#         GROUP BY sii.item_code, si.customer_group, month
#     """, (start_date, end_date, item_codes), as_dict=True)

#     sales_data = defaultdict(lambda: defaultdict(lambda: {"sales": 0, "qty": 0}))
#     meta_data = {}
#     channel_totals = defaultdict(lambda: defaultdict(lambda: {"sales": 0, "qty": 0}))

#     for r in sales_results:
#         parent_item_code = item_group_map.get(r.item_code, r.item_code)
#         channel = get_channel(r.customer_group)
#         key = (channel, parent_item_code)

#         sales_data[key][r.month]["sales"] += r.total_sales or 0
#         sales_data[key][r.month]["qty"] += r.total_qty or 0

#         channel_totals[channel][r.month]["sales"] += r.total_sales or 0
#         channel_totals[channel][r.month]["qty"] += r.total_qty or 0

#         if key not in meta_data:
#             if parent_item_code == r.item_code:
#                 item_name = r.item_name
#             else:
#                 item_name = frappe.db.get_value("Item", parent_item_code, "item_name") or r.item_name

#             meta_data[key] = {
#                 "item_name": item_name,
#                 "channel": channel,
#                 "item_code": parent_item_code
#             }

#     def get_gl_monthly(account):
#         gl_rows = frappe.db.sql("""
#             SELECT MONTH(posting_date) AS month, SUM(debit - credit) AS amount
#             FROM `tabGL Entry`
#             WHERE account = %s AND posting_date BETWEEN %s AND %s
#             GROUP BY month
#         """, (account, start_date, end_date), as_dict=True)
#         return {row.month: row.amount or 0 for row in gl_rows}

#     monthly_deductions = {code: get_gl_monthly(account) for code, account in deduction_accounts.items()}
#     months_list = list(months)
#     total_deduct_monthly = {m: sum(monthly_deductions[code].get(m, 0) for code in deduction_accounts) for m in months}

#     rebate_by_channel = get_monthly_rebate_by_channel(start_date, end_date)
#     discount_by_channel = get_monthly_discount_by_channel(start_date, end_date)
#     credit_note_deductions = get_credit_note_deductions_by_channel(start_date, end_date)

#     total_deductions_by_channel = defaultdict(lambda: defaultdict(float))
#     for channel, monthly_data in rebate_by_channel.items():
#         for m, v in monthly_data.items():
#             total_deductions_by_channel[channel][m] += v
#     for channel, monthly_data in discount_by_channel.items():
#         for m, v in monthly_data.items():
#             total_deductions_by_channel[channel][m] += v
#     for channel, deduction_types in credit_note_deductions.items():
#         for monthly_data in deduction_types.values():
#             for m, v in monthly_data.items():
#                 total_deductions_by_channel[channel][m] += v

#     channel_discount_rate = defaultdict(lambda: defaultdict(float))
#     for channel in channel_totals:
#         for m in months:
#             total_qty = channel_totals[channel][m]["qty"]
#             total_deductions = total_deductions_by_channel[channel][m]
#             channel_discount_rate[channel][m] = (total_deductions / total_qty) if total_qty else 0

#     discount_rate_per_month = {}
#     for m in months:
#         total_qty_month = sum(channel_totals[channel][m]["qty"] for channel in channel_totals)
#         discount_rate_per_month[m] = (total_deduct_monthly.get(m, 0) / total_qty_month) if total_qty_month else 0

#     data = []
#     totals_sales = defaultdict(float)
#     totals_qty = defaultdict(float)

#     # Sales Data Rows grouped by Channel and Item
#     for key in sales_data:
#         channel, item_code = key
#         meta = meta_data.get(key, {})
#         row = {
#             "channel": channel,
#             "item_code": item_code,
#             "item_name": meta.get("item_name", "")
#         }
#         total_sales_sum = 0
#         total_qty_sum = 0

#         for m in months:
#             m_abbr = calendar.month_abbr[m].lower()
#             sales = sales_data[key][m]["sales"]
#             qty = sales_data[key][m]["qty"]
#             rate = (sales / qty) if qty else 0

#             totals_sales[m] += sales
#             totals_qty[m] += qty

#             discount_rate = discount_rate_per_month.get(m, 0)
#             # Updated calculation: net_rate = rate - channel_discount_rate
#             net_rate = rate - channel_discount_rate[channel].get(m, 0)
#             channel_disc = total_deductions_by_channel[channel].get(m, 0)
#             channel_disc_rate = channel_discount_rate[channel].get(m, 0)

#             row[f"{m_abbr}_sales"] = round(sales, 2)
#             row[f"{m_abbr}_qty"] = round(qty, 2)
#             row[f"{m_abbr}_rate"] = round(rate, 2)
#             row[f"{m_abbr}_discount_rate"] = round(discount_rate, 4)
#             row[f"{m_abbr}_net_rate"] = round(net_rate, 4)
#             row[f"{m_abbr}_channel_discount"] = round(channel_disc, 2)
#             row[f"{m_abbr}_channel_discount_rate"] = round(channel_disc_rate, 4)

#             total_sales_sum += sales
#             total_qty_sum += qty

#         total_rate = (total_sales_sum / total_qty_sum) if total_qty_sum else 0
#         total_discount = sum(discount_rate_per_month.get(m, 0) for m in months) / 12
#         # Updated calculation: total_net_rate = total_rate - average channel_discount_rate
#         total_channel_disc_rate = sum(channel_discount_rate[channel].get(m, 0) for m in months) / 12
#         total_net_rate = total_rate - total_channel_disc_rate

#         row["total_sales"] = round(total_sales_sum, 2)
#         row["total_qty"] = round(total_qty_sum, 2)
#         row["total_rate"] = round(total_rate, 2)
#         row["total_net_rate"] = round(total_net_rate, 4)
#         data.append(row)

#     # Channel-wise total rows
#     for channel in channel_totals:
#         row = {
#             "channel": channel,
#             "item_code": "",
#             "item_name": f"Total for {channel}",
#         }
#         total_sales_sum = 0
#         total_qty_sum = 0

#         for m in months:
#             m_abbr = calendar.month_abbr[m].lower()
#             sales = channel_totals[channel][m]["sales"]
#             qty = channel_totals[channel][m]["qty"]
#             rate = (sales / qty) if qty else 0
#             discount_rate = discount_rate_per_month.get(m, 0)
#             # Updated calculation: net_rate = rate - channel_discount_rate
#             net_rate = rate - channel_discount_rate[channel].get(m, 0)
#             channel_disc = total_deductions_by_channel[channel].get(m, 0)
#             channel_disc_rate = channel_discount_rate[channel].get(m, 0)

#             row[f"{m_abbr}_sales"] = round(sales, 2)
#             row[f"{m_abbr}_qty"] = round(qty, 2)
#             row[f"{m_abbr}_rate"] = round(rate, 2)
#             row[f"{m_abbr}_discount_rate"] = round(discount_rate, 4)
#             row[f"{m_abbr}_net_rate"] = round(net_rate, 4)
#             row[f"{m_abbr}_channel_discount"] = round(channel_disc, 2)
#             row[f"{m_abbr}_channel_discount_rate"] = round(channel_disc_rate, 4)

#             total_sales_sum += sales
#             total_qty_sum += qty

#         total_rate = (total_sales_sum / total_qty_sum) if total_qty_sum else 0
#         # Updated calculation: total_net_rate = total_rate - average channel_discount_rate
#         total_channel_disc_rate = sum(channel_discount_rate[channel].get(m, 0) for m in months) / 12
#         total_net_rate = total_rate - total_channel_disc_rate

#         row["total_sales"] = round(total_sales_sum, 2)
#         row["total_qty"] = round(total_qty_sum, 2)
#         row["total_rate"] = round(total_rate, 2)
#         row["total_net_rate"] = round(total_net_rate, 4)
#         data.append(row)

#     # Total row for all sales grouped by channel
#     total_row = {
#         "channel": "TOTAL",
#         "item_code": "",
#         "item_name": "Total of All Items",
#     }
#     total_sales_sum_all = 0
#     total_qty_sum_all = 0
#     for m in months:
#         m_abbr = calendar.month_abbr[m].lower()
#         sales = totals_sales[m]
#         qty = totals_qty[m]
#         rate = (sales / qty) if qty else 0
#         discount_rate = discount_rate_per_month.get(m, 0)
#         # Updated calculation: net_rate = rate - average channel_discount_rate across all channels
#         avg_channel_disc_rate = sum(channel_discount_rate[ch].get(m, 0) for ch in channel_totals) / len(channel_totals) if channel_totals else 0
#         net_rate = rate - avg_channel_disc_rate
#         channel_disc = sum(total_deductions_by_channel[ch].get(m, 0) for ch in channel_totals)
#         channel_disc_rate = avg_channel_disc_rate

#         total_row[f"{m_abbr}_sales"] = round(sales, 2)
#         total_row[f"{m_abbr}_qty"] = round(qty, 2)
#         total_row[f"{m_abbr}_rate"] = round(rate, 2)
#         total_row[f"{m_abbr}_discount_rate"] = round(discount_rate, 4)
#         total_row[f"{m_abbr}_net_rate"] = round(net_rate, 4)
#         total_row[f"{m_abbr}_channel_discount"] = round(channel_disc, 2)
#         total_row[f"{m_abbr}_channel_discount_rate"] = round(channel_disc_rate, 4)

#         total_sales_sum_all += sales
#         total_qty_sum_all += qty

#     total_rate_all = (total_sales_sum_all / total_qty_sum_all) if total_qty_sum_all else 0
#     # Updated calculation: total_net_rate = total_rate - average channel_discount_rate
#     total_avg_channel_disc_rate = sum(sum(channel_discount_rate[ch].get(m, 0) for m in months) / 12 for ch in channel_totals) / len(channel_totals) if channel_totals else 0
#     total_net_rate_all = total_rate_all - total_avg_channel_disc_rate
#     total_row["total_sales"] = round(total_sales_sum_all, 2)
#     total_row["total_qty"] = round(total_qty_sum_all, 2)
#     total_row["total_rate"] = round(total_rate_all, 2)
#     total_row["total_net_rate"] = round(total_net_rate_all, 4)

#     data.append(total_row)

#     return data



# # import frappe
# # from collections import defaultdict
# # import calendar

# # CHANNEL_MAPPING = {
# #     "DIRECT DISTRIBUTION DD": [
# #         "EATRIES", "LARGE GROCERY", "MINIMARKET", "SMALL GROCERY",
# #         "SUPERMARKET B", "WATER SHOP", "DIRECT DISTRIBUTION DD"
# #     ],
# #     "DISTRIBUTOR": [
# #         "DISTRIBUTOR A", "DISTRIBUTOR B", "DISTRIBUTOR C", "DISTRIBUTOR"
# #     ],
# #     "HOME DELIVERY HD": [
# #         "HOUSE", "MOSQUE", "OFFICE", "SCHOOL", "HOME DELIVERY HD"
# #     ],
# #     "HORECA HO": [
# #         "CAFÉ", "CARE", "CATERING", "COMMERCIAL", "GOVERNMENTAL",
# #         "HOTEL", "INSTITUTIONAL", "RESTAURANT", "HORECA HO", "CAFE"
# #     ],
# #     "KEY ACCOUNT KA": [
# #         "E-COMMERCE", "HYPERMARKET", "SUPERMARKET-A", "SUPERMARKET-B", "KEY ACCOUNT  KA"
# #     ],
# #     "MARKETING": [
# #         "MARKETING", "DONATION", "EVENT", "SPONSORSHIP"
# #     ],
# #     "OTHER MISCELLANEOUS": [
# #         "OTHER MISCELLANEOUS", "OTHER  MISCELLANEOUS"
# #     ],
# #     "WHOLESALE": [
# #         "WHOLESALE WS", "WAREHOUSE", "WHOLESALE A", "WHOLESALE-B", "WHOLESALE-C"
# #     ]
# # }

# # def get_channel(customer_group):
# #     if not customer_group:
# #         return ""
# #     customer_group_upper = customer_group.strip().upper()
# #     for channel, groups in CHANNEL_MAPPING.items():
# #         if customer_group_upper in (g.upper() for g in groups):
# #             return channel
# #     return ""

# # def execute(filters=None):
# #     filters = filters or {}
# #     year = filters.get("year")
# #     if not year:
# #         frappe.throw("Please select a year")

# #     columns = get_columns()
# #     data = get_data(year)
# #     return columns, data

# # def get_columns():
# #     months = [calendar.month_abbr[m] for m in range(1, 13)]
# #     columns = [
# #         {"label": "Channel", "fieldname": "channel", "fieldtype": "Data", "width": 150},
# #         {"label": "Item Code", "fieldname": "item_code", "fieldtype": "Data", "width": 140},
# #         {"label": "Item Name", "fieldname": "item_name", "fieldtype": "Data", "width": 250},
# #     ]
# #     for m in months:
# #         col_prefix = m.lower()
# #         columns.append({"label": f"{m} Sales", "fieldname": f"{col_prefix}_sales", "fieldtype": "Currency", "width": 100})
# #         columns.append({"label": f"{m} Qty", "fieldname": f"{col_prefix}_qty", "fieldtype": "Float", "width": 80})
# #         columns.append({"label": f"{m} Rate", "fieldname": f"{col_prefix}_rate", "fieldtype": "Currency", "width": 80})
# #         columns.append({"label": f"{m} Discount Rate", "fieldname": f"{col_prefix}_discount_rate", "fieldtype": "Float", "width": 110})
# #         columns.append({"label": f"{m} Net Rate", "fieldname": f"{col_prefix}_net_rate", "fieldtype": "Float", "width": 110})
# #     columns += [
# #         {"label": "Total Sales", "fieldname": "total_sales", "fieldtype": "Currency", "width": 110},
# #         {"label": "Total Qty", "fieldname": "total_qty", "fieldtype": "Float", "width": 90},
# #         {"label": "Total Rate", "fieldname": "total_rate", "fieldtype": "Currency", "width": 90},
# #         {"label": "Total Net Rate", "fieldname": "total_net_rate", "fieldtype": "Currency", "width": 110},
# #     ]
# #     return columns

# # def get_data(year):
# #     start_date = f"{year}-01-01"
# #     end_date = f"{year}-12-31"

# #     item_codes = (
# #         '6287016760027', '6287016760041', '6287016760034',
# #         '6287016760058', '6287016760119', '6287016760157', '6287016760164'
# #     )

# #     deduction_accounts = {
# #         "41010105": "41010105 - Sales Rebate/Trade Discount -حسم المبيعات /الخصم التجاري - ABNA",
# #         "516101": "516101 - Registerion Fees -رسوم التسجيل - ABNA",
# #         "516102": "516102 - Listing Fees -رسوم أدخال اصناف - ABNA",
# #         "516107": "516107 - Flyer Fees -رسوم فلاير - ABNA",
# #         "41010103": "41010103 - Discount Allowance -الخصم المسموح به - ABNA"
# #     }

# #     months = range(1, 13)

# #     # Aggregate data keyed by (channel, item_code)
# #     sales_data = defaultdict(lambda: defaultdict(lambda: {"sales": 0, "qty": 0}))
# #     meta_data = {}

# #     # Query sales invoices grouped by item_code, customer_group, month (to get customer_group for channel mapping)
# #     sales_results = frappe.db.sql("""
# #         SELECT
# #             sii.item_code,
# #             sii.item_name,
# #             si.customer_group,
# #             MONTH(si.posting_date) AS month,
# #             SUM(sii.qty) AS total_qty,
# #             SUM(sii.base_net_amount) AS total_sales
# #         FROM `tabSales Invoice` si
# #         JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
# #         WHERE
# #             si.docstatus = 1
# #             AND si.posting_date BETWEEN %s AND %s
# #             AND sii.item_code IN %s
# #         GROUP BY sii.item_code, si.customer_group, month
# #     """, (start_date, end_date, item_codes), as_dict=True)

# #     for r in sales_results:
# #         channel = get_channel(r.customer_group)
# #         key = (channel, r.item_code)
# #         sales_data[key][r.month]["sales"] += r.total_sales or 0
# #         sales_data[key][r.month]["qty"] += r.total_qty or 0

# #         meta_data[key] = {
# #             "item_name": r.item_name,
# #             "channel": channel,
# #         }

# #     def get_gl_monthly(account):
# #         gl_rows = frappe.db.sql("""
# #             SELECT MONTH(posting_date) AS month, SUM(debit - credit) AS amount
# #             FROM `tabGL Entry`
# #             WHERE account = %s AND posting_date BETWEEN %s AND %s
# #             GROUP BY month
# #         """, (account, start_date, end_date), as_dict=True)
# #         return {row.month: row.amount or 0 for row in gl_rows}

# #     monthly_deductions = {code: get_gl_monthly(account) for code, account in deduction_accounts.items()}

# #     total_deduct_monthly = {m: sum(monthly_deductions[code].get(m, 0) for code in deduction_accounts) for m in months}

# #     discount_rate_per_month = {}
# #     for m in months:
# #         total_qty_month = sum(sales_data[key][m]["qty"] for key in sales_data)
# #         discount_rate_per_month[m] = (total_deduct_monthly.get(m, 0) / total_qty_month) if total_qty_month else 0

# #     data = []
# #     totals_sales = defaultdict(float)
# #     totals_qty = defaultdict(float)

# #     for key in sales_data:
# #         channel, item_code = key
# #         meta = meta_data.get(key, {})
# #         row = {
# #             "item_code": item_code,
# #             "item_name": meta.get("item_name", ""),
# #             "channel": channel
# #         }
# #         total_sales_sum = 0
# #         total_qty_sum = 0

# #         for m in months:
# #             m_abbr = calendar.month_abbr[m].lower()
# #             sales = sales_data[key][m]["sales"]
# #             qty = sales_data[key][m]["qty"]
# #             rate = (sales / qty) if qty else 0

# #             totals_sales[m] += sales
# #             totals_qty[m] += qty

# #             discount_rate = discount_rate_per_month.get(m, 0)
# #             net_rate = rate - discount_rate

# #             row[f"{m_abbr}_sales"] = round(sales, 2)
# #             row[f"{m_abbr}_qty"] = round(qty, 2)
# #             row[f"{m_abbr}_rate"] = round(rate, 2)
# #             row[f"{m_abbr}_discount_rate"] = round(discount_rate, 4)
# #             row[f"{m_abbr}_net_rate"] = round(net_rate, 4)

# #             total_sales_sum += sales
# #             total_qty_sum += qty

# #         total_rate = (total_sales_sum / total_qty_sum) if total_qty_sum else 0
# #         total_discount = sum(discount_rate_per_month.get(m, 0) for m in months) / 12
# #         total_net_rate = total_rate - total_discount

# #         row["total_sales"] = round(total_sales_sum, 2)
# #         row["total_qty"] = round(total_qty_sum, 2)
# #         row["total_rate"] = round(total_rate, 2)
# #         row["total_net_rate"] = round(total_net_rate, 4)
# #         data.append(row)

# #     # Total row
# #     total_row = {
# #         "item_code": "TOTAL",
# #         "item_name": "Total of All Items",
# #         "channel": ""
# #     }
# #     total_sales_sum_all = 0
# #     total_qty_sum_all = 0
# #     for m in months:
# #         m_abbr = calendar.month_abbr[m].lower()
# #         sales = totals_sales[m]
# #         qty = totals_qty[m]
# #         rate = (sales / qty) if qty else 0
# #         discount_rate = discount_rate_per_month.get(m, 0)
# #         net_rate = rate - discount_rate

# #         total_row[f"{m_abbr}_sales"] = round(sales, 2)
# #         total_row[f"{m_abbr}_qty"] = round(qty, 2)
# #         total_row[f"{m_abbr}_rate"] = round(rate, 2)
# #         total_row[f"{m_abbr}_discount_rate"] = round(discount_rate, 4)
# #         total_row[f"{m_abbr}_net_rate"] = round(net_rate, 4)

# #         total_sales_sum_all += sales
# #         total_qty_sum_all += qty

# #     total_row["total_sales"] = round(total_sales_sum_all, 2)
# #     total_row["total_qty"] = round(total_qty_sum_all, 2)
# #     total_row["total_rate"] = round((total_sales_sum_all / total_qty_sum_all) if total_qty_sum_all else 0, 2)
# #     total_row["total_net_rate"] = round(total_row["total_rate"] - (sum(discount_rate_per_month.values()) / 12), 4)
# #     data.append(total_row)

# #     # Deduction rows
# #     def make_deduction_row(code, name, monthly_data):
# #         row = {
# #             "item_code": code,
# #             "item_name": name,
# #             "channel": ""
# #         }
# #         total_amt = 0
# #         for m in months:
# #             m_abbr = calendar.month_abbr[m].lower()
# #             amt = monthly_data.get(m, 0)
# #             row[f"{m_abbr}_sales"] = round(amt, 2)
# #             row[f"{m_abbr}_qty"] = 0
# #             row[f"{m_abbr}_rate"] = 0
# #             row[f"{m_abbr}_discount_rate"] = 0
# #             row[f"{m_abbr}_net_rate"] = 0
# #             total_amt += amt
# #         row["total_sales"] = round(total_amt, 2)
# #         row["total_qty"] = 0
# #         row["total_rate"] = 0
# #         row["total_net_rate"] = 0
# #         return row

# #     for code, monthly in monthly_deductions.items():
# #         data.append(make_deduction_row(code, code.replace("_", " ").title(), monthly))

# #     data.append(make_deduction_row("Total Deduction", "Total Deductions (All)", total_deduct_monthly))

# #     # Discount Rate summary row
# #     discount_rate_row = {
# #         "item_code": "Discount Rate",
# #         "item_name": "Discount Rate = Total Deduct / Total Qty",
# #         "channel": "",
# #     }
# #     for m in months:
# #         m_abbr = calendar.month_abbr[m].lower()
# #         val = discount_rate_per_month.get(m, 0)
# #         discount_rate_row[f"{m_abbr}_sales"] = round(val, 4)
# #         discount_rate_row[f"{m_abbr}_qty"] = 0
# #         discount_rate_row[f"{m_abbr}_rate"] = 0
# #         discount_rate_row[f"{m_abbr}_discount_rate"] = 0
# #         discount_rate_row[f"{m_abbr}_net_rate"] = 0
# #     discount_rate_row["total_sales"] = 0
# #     discount_rate_row["total_qty"] = 0
# #     discount_rate_row["total_rate"] = 0
# #     discount_rate_row["total_net_rate"] = 0
# #     data.append(discount_rate_row)

# #     return data


# # import frappe
# # from collections import defaultdict
# # import calendar

# # CHANNEL_MAPPING = {
# #     "DIRECT DISTRIBUTION DD": [
# #         "EATRIES", "LARGE GROCERY", "MINIMARKET", "SMALL GROCERY",
# #         "SUPERMARKET B", "WATER SHOP", "DIRECT DISTRIBUTION DD"
# #     ],
# #     "DISTRIBUTOR": [
# #         "DISTRIBUTOR A", "DISTRIBUTOR B", "DISTRIBUTOR C", "DISTRIBUTOR"
# #     ],
# #     "HOME DELIVERY HD": [
# #         "HOUSE", "MOSQUE", "OFFICE", "SCHOOL", "HOME DELIVERY HD"
# #     ],
# #     "HORECA HO": [
# #         "CAFÉ", "CARE", "CATERING", "COMMERCIAL", "GOVERNMENTAL",
# #         "HOTEL", "INSTITUTIONAL", "RESTAURANT", "HORECA HO","CAFE"
# #     ],
# #     "KEY ACCOUNT KA": [
# #         "E-COMMERCE", "HYPERMARKET", "SUPERMARKET-A", "SUPERMARKET-B", "KEY ACCOUNT  KA"
# #     ],
# #     "MARKETING": [
# #         "MARKETING", "DONATION", "EVENT", "SPONSORSHIP"
# #     ],
# #     "OTHER MISCELLANEOUS": [
# #         "OTHER MISCELLANEOUS","OTHER  MISCELLANEOUS"
# #     ],
# #     "WHOLESALE": [
# #         "WHOLESALE WS", "WAREHOUSE", "WHOLESALE A", "WHOLESALE-B", "WHOLESALE-C"
# #     ]
# # }

# # def get_channel(customer_group):
# #     if not customer_group:
# #         return ""
# #     customer_group_upper = customer_group.strip().upper()
# #     for channel, groups in CHANNEL_MAPPING.items():
# #         if customer_group_upper in (g.upper() for g in groups):
# #             return channel
# #     return ""

# # def execute(filters=None):
# #     filters = filters or {}
# #     year = filters.get("year")
# #     if not year:
# #         frappe.throw("Please select a year")

# #     columns = get_columns(year)
# #     data = get_data(year)
# #     return columns, data

# # def get_columns(year):
# #     months = [calendar.month_abbr[m] for m in range(1, 13)]
# #     columns = [
# #         {"label": "Customer", "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 200},
# #         {"label": "Channel", "fieldname": "channel", "fieldtype": "Data", "width": 150},
# #         {"label": "Customer Group", "fieldname": "customer_group", "fieldtype": "Link", "options": "Customer Group", "width": 180},
# #         {"label": "Item Code", "fieldname": "item_code", "fieldtype": "Data", "width": 140},
# #         {"label": "Item Name", "fieldname": "item_name", "fieldtype": "Data", "width": 250},
# #     ]
# #     for m in months:
# #         col_prefix = m.lower()
# #         columns.append({"label": f"{m} Sales", "fieldname": f"{col_prefix}_sales", "fieldtype": "Currency", "width": 100})
# #         columns.append({"label": f"{m} Qty", "fieldname": f"{col_prefix}_qty", "fieldtype": "Float", "width": 80})
# #         columns.append({"label": f"{m} Rate", "fieldname": f"{col_prefix}_rate", "fieldtype": "Currency", "width": 80})
# #         columns.append({"label": f"{m} Discount Rate", "fieldname": f"{col_prefix}_discount_rate", "fieldtype": "Float", "width": 110})
# #         columns.append({"label": f"{m} Net Rate", "fieldname": f"{col_prefix}_net_rate", "fieldtype": "Float", "width": 110})
# #     columns += [
# #         {"label": "Total Sales", "fieldname": "total_sales", "fieldtype": "Currency", "width": 110},
# #         {"label": "Total Qty", "fieldname": "total_qty", "fieldtype": "Float", "width": 90},
# #         {"label": "Total Rate", "fieldname": "total_rate", "fieldtype": "Currency", "width": 90},
# #         {"label": "Total Net Rate", "fieldname": "total_net_rate", "fieldtype": "Currency", "width": 110},
# #     ]
# #     return columns

# # def get_data(year):
# #     start_date = f"{year}-01-01"
# #     end_date = f"{year}-12-31"

# #     item_codes = (
# #         '6287016760027', '6287016760041', '6287016760034',
# #         '6287016760058', '6287016760119', '6287016760157', '6287016760164'
# #     )

# #     deduction_accounts = {
# #         "Rebate": "41010105 - Sales Rebate/Trade Discount -حسم المبيعات /الخصم التجاري - ABNA",
# #         "Registerion": "516101 - Registerion Fees -رسوم التسجيل - ABNA",
# #         "Listing": "516102 - Listing Fees -رسوم أدخال اصناف - ABNA",
# #         "Flyer": "516107 - Flyer Fees -رسوم فلاير - ABNA",
# #         "Discount": "41010103 - Discount Allowance -الخصم المسموح به - ABNA"
# #     }

# #     months = range(1, 13)
# #     sales_data = defaultdict(lambda: defaultdict(lambda: {"sales": 0, "qty": 0}))
# #     meta_data = {}

# #     sales_results = frappe.db.sql("""
# #         SELECT
# #             sii.item_code,
# #             sii.item_name,
# #             si.customer,
# #             si.customer_group,
# #             MONTH(si.posting_date) AS month,
# #             SUM(sii.qty) AS total_qty,
# #             SUM(sii.base_net_amount) AS total_sales
# #         FROM `tabSales Invoice` si
# #         JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
# #         WHERE
# #             si.docstatus = 1
# #             AND si.posting_date BETWEEN %s AND %s
# #             AND sii.item_code IN %s
# #         GROUP BY sii.item_code, si.customer, month
# #     """, (start_date, end_date, item_codes), as_dict=True)

# #     for r in sales_results:
# #         key = (r.item_code, r.customer)
# #         sales_data[key][r.month]["sales"] += r.total_sales or 0
# #         sales_data[key][r.month]["qty"] += r.total_qty or 0

# #         mapped_channel = get_channel(r.customer_group)

# #         meta_data[key] = {
# #             "item_name": r.item_name,
# #             "customer": r.customer,
# #             "customer_group": r.customer_group,
# #             "channel": mapped_channel
# #         }

# #     def get_gl_monthly(account):
# #         gl_rows = frappe.db.sql("""
# #             SELECT MONTH(posting_date) AS month, SUM(debit - credit) AS amount
# #             FROM `tabGL Entry`
# #             WHERE account = %s AND posting_date BETWEEN %s AND %s
# #             GROUP BY month
# #         """, (account, start_date, end_date), as_dict=True)
# #         return {row.month: row.amount or 0 for row in gl_rows}

# #     monthly_deductions = {code: get_gl_monthly(account) for code, account in deduction_accounts.items()}

# #     total_deduct_monthly = {m: sum(monthly_deductions[code].get(m, 0) for code in deduction_accounts) for m in months}

# #     discount_rate_per_month = {}
# #     for m in months:
# #         total_qty_month = sum(sales_data[key][m]["qty"] for key in sales_data)
# #         discount_rate_per_month[m] = (total_deduct_monthly.get(m, 0) / total_qty_month) if total_qty_month else 0

# #     data = []
# #     totals_sales = defaultdict(float)
# #     totals_qty = defaultdict(float)

# #     for key in sales_data:
# #         item_code, customer = key
# #         meta = meta_data.get(key, {})
# #         row = {
# #             "item_code": item_code,
# #             "item_name": meta.get("item_name", ""),
# #             "customer": meta.get("customer", ""),
# #             "customer_group": meta.get("customer_group", ""),
# #             "channel": meta.get("channel", "")
# #         }
# #         total_sales_sum = 0
# #         total_qty_sum = 0

# #         for m in months:
# #             m_abbr = calendar.month_abbr[m].lower()
# #             sales = sales_data[key][m]["sales"]
# #             qty = sales_data[key][m]["qty"]
# #             rate = (sales / qty) if qty else 0

# #             totals_sales[m] += sales
# #             totals_qty[m] += qty

# #             discount_rate = discount_rate_per_month.get(m, 0)
# #             net_rate = rate - discount_rate

# #             row[f"{m_abbr}_sales"] = round(sales, 2)
# #             row[f"{m_abbr}_qty"] = round(qty, 2)
# #             row[f"{m_abbr}_rate"] = round(rate, 2)
# #             row[f"{m_abbr}_discount_rate"] = round(discount_rate, 4)
# #             row[f"{m_abbr}_net_rate"] = round(net_rate, 4)

# #             total_sales_sum += sales
# #             total_qty_sum += qty

# #         total_rate = (total_sales_sum / total_qty_sum) if total_qty_sum else 0
# #         total_discount = sum(discount_rate_per_month.get(m, 0) for m in months) / 12
# #         total_net_rate = total_rate - total_discount

# #         row["total_sales"] = round(total_sales_sum, 2)
# #         row["total_qty"] = round(total_qty_sum, 2)
# #         row["total_rate"] = round(total_rate, 2)
# #         row["total_net_rate"] = round(total_net_rate, 4)
# #         data.append(row)

# #     # Total row
# #     total_row = {
# #         "item_code": "TOTAL",
# #         "item_name": "Total of All Items",
# #         "customer": "",
# #         "customer_group": "",
# #         "channel": ""
# #     }
# #     total_sales_sum_all = 0
# #     total_qty_sum_all = 0
# #     for m in months:
# #         m_abbr = calendar.month_abbr[m].lower()
# #         sales = totals_sales[m]
# #         qty = totals_qty[m]
# #         rate = (sales / qty) if qty else 0
# #         discount_rate = discount_rate_per_month.get(m, 0)
# #         net_rate = rate - discount_rate

# #         total_row[f"{m_abbr}_sales"] = round(sales, 2)
# #         total_row[f"{m_abbr}_qty"] = round(qty, 2)
# #         total_row[f"{m_abbr}_rate"] = round(rate, 2)
# #         total_row[f"{m_abbr}_discount_rate"] = round(discount_rate, 4)
# #         total_row[f"{m_abbr}_net_rate"] = round(net_rate, 4)

# #         total_sales_sum_all += sales
# #         total_qty_sum_all += qty

# #     total_row["total_sales"] = round(total_sales_sum_all, 2)
# #     total_row["total_qty"] = round(total_qty_sum_all, 2)
# #     total_row["total_rate"] = round((total_sales_sum_all / total_qty_sum_all) if total_qty_sum_all else 0, 2)
# #     total_row["total_net_rate"] = round(total_row["total_rate"] - (sum(discount_rate_per_month.values())/12), 4)
# #     data.append(total_row)

# #     # Deduction rows
# #     def make_deduction_row(code, name, monthly_data):
# #         row = {
# #             "item_code": code,
# #             "item_name": name,
# #             "customer": "",
# #             "customer_group": "",
# #             "channel": ""
# #         }
# #         total_amt = 0
# #         for m in months:
# #             m_abbr = calendar.month_abbr[m].lower()
# #             amt = monthly_data.get(m, 0)
# #             row[f"{m_abbr}_sales"] = round(amt, 2)
# #             row[f"{m_abbr}_qty"] = 0
# #             row[f"{m_abbr}_rate"] = 0
# #             row[f"{m_abbr}_discount_rate"] = 0
# #             row[f"{m_abbr}_net_rate"] = 0
# #             total_amt += amt
# #         row["total_sales"] = round(total_amt, 2)
# #         row["total_qty"] = 0
# #         row["total_rate"] = 0
# #         row["total_net_rate"] = 0
# #         return row

# #     for code, monthly in monthly_deductions.items():
# #         data.append(make_deduction_row(code, code.replace("_", " ").title(), monthly))

# #     data.append(make_deduction_row("Total Deduction", "Total Deductions (All)", total_deduct_monthly))

# #     # Discount Rate summary row
# #     discount_rate_row = {
# #         "item_code": "Discount Rate",
# #         "item_name": "Discount Rate = Total Deduct / Total Qty",
# #         "customer": "",
# #         "customer_group": "",
# #         "channel": "",
# #     }
# #     for m in months:
# #         m_abbr = calendar.month_abbr[m].lower()
# #         val = discount_rate_per_month.get(m, 0)
# #         discount_rate_row[f"{m_abbr}_sales"] = round(val, 4)
# #         discount_rate_row[f"{m_abbr}_qty"] = 0
# #         discount_rate_row[f"{m_abbr}_rate"] = 0
# #         discount_rate_row[f"{m_abbr}_discount_rate"] = 0
# #         discount_rate_row[f"{m_abbr}_net_rate"] = 0
# #     discount_rate_row["total_sales"] = 0
# #     discount_rate_row["total_qty"] = 0
# #     discount_rate_row["total_rate"] = 0
# #     discount_rate_row["total_net_rate"] = 0
# #     data.append(discount_rate_row)

# #     return data


# # import frappe
# # from collections import defaultdict
# # import calendar

# # CHANNEL_MAPPING = {
# #     "DIRECT DISTRIBUTION DD": [
# #         "EATRIES", "LARGE GROCERY", "MINIMARKET", "SMALL GROCERY",
# #         "SUPERMARKET B", "WATER SHOP", "DIRECT DISTRIBUTION DD"
# #     ],
# #     "DISTRIBUTOR": [
# #         "DISTRIBUTOR A", "DISTRIBUTOR B", "DISTRIBUTOR C", "DISTRIBUTOR"
# #     ],
# #     "HOME DELIVERY HD": [
# #         "HOUSE", "MOSQUE", "OFFICE", "SCHOOL", "HOME DELIVERY HD"
# #     ],
# #     "HORECA HO": [
# #         "CAFÉ", "CARE", "CATERING", "COMMERCIAL", "GOVERNMENTAL",
# #         "HOTEL", "INSTITUTIONAL", "RESTAURANT", "HORECA HO","CAFE"
# #     ],
# #     "KEY ACCOUNT KA": [
# #         "E-COMMERCE", "HYPERMARKET", "SUPERMARKET-A", "SUPERMARKET-B", "KEY ACCOUNT  KA"
# #     ],
# #     "MARKETING": [
# #         "MARKETING", "DONATION", "EVENT", "SPONSORSHIP"
# #     ],
# #     "OTHER MISCELLANEOUS": [
# #         "OTHER MISCELLANEOUS","OTHER  MISCELLANEOUS"
# #     ],
# #     "WHOLESALE": [
# #         "WHOLESALE WS", "WAREHOUSE", "WHOLESALE A", "WHOLESALE-B", "WHOLESALE-C"
# #     ]
# # }

# # def get_channel(customer_group):
# #     if not customer_group:
# #         return ""
# #     customer_group_upper = customer_group.strip().upper()
# #     for channel, groups in CHANNEL_MAPPING.items():
# #         if customer_group_upper in (g.upper() for g in groups):
# #             return channel
# #     return ""

# # def execute(filters=None):
# #     filters = filters or {}
# #     year = filters.get("year")
# #     if not year:
# #         frappe.throw("Please select a year")

# #     columns = get_columns(year)
# #     data = get_data(year)
# #     return columns, data

# # def get_columns(year):
# #     months = [calendar.month_abbr[m] for m in range(1, 13)]
# #     columns = [
# #         {"label": "Customer", "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 200},
# #         {"label": "Channel", "fieldname": "channel", "fieldtype": "Data", "width": 150},
# #         {"label": "Customer Group", "fieldname": "customer_group", "fieldtype": "Link", "options": "Customer Group", "width": 180},
# #         {"label": "Item Code", "fieldname": "item_code", "fieldtype": "Data", "width": 140},
# #         {"label": "Item Name", "fieldname": "item_name", "fieldtype": "Data", "width": 250},
# #     ]
# #     for m in months:
# #         col_prefix = m.lower()
# #         columns.append({"label": f"{m} Sales", "fieldname": f"{col_prefix}_sales", "fieldtype": "Currency", "width": 100})
# #         columns.append({"label": f"{m} Qty", "fieldname": f"{col_prefix}_qty", "fieldtype": "Float", "width": 80})
# #         columns.append({"label": f"{m} Rate", "fieldname": f"{col_prefix}_rate", "fieldtype": "Currency", "width": 80})
# #         columns.append({"label": f"{m} Discount Rate", "fieldname": f"{col_prefix}_discount_rate", "fieldtype": "Float", "width": 110})
# #         columns.append({"label": f"{m} Net Rate", "fieldname": f"{col_prefix}_net_rate", "fieldtype": "Float", "width": 110})
# #     columns += [
# #         {"label": "Total Sales", "fieldname": "total_sales", "fieldtype": "Currency", "width": 110},
# #         {"label": "Total Qty", "fieldname": "total_qty", "fieldtype": "Float", "width": 90},
# #         {"label": "Total Rate", "fieldname": "total_rate", "fieldtype": "Currency", "width": 90},
# #         {"label": "Total Net Rate", "fieldname": "total_net_rate", "fieldtype": "Currency", "width": 110},
# #     ]
# #     return columns

# # def get_monthly_rebate_by_customer(start_date, end_date):
# #     results = frappe.db.sql("""
# #         SELECT
# #             party AS customer,
# #             MONTH(posting_date) AS month,
# #             SUM(rebate_received_amount) AS rebate_amount
# #         FROM `tabRebate`
# #         WHERE
# #             docstatus = 1
# #             AND party_type = 'Customer'
# #             AND posting_date BETWEEN %s AND %s
# #         GROUP BY party, MONTH(posting_date)
# #     """, (start_date, end_date), as_dict=True)

# #     rebate_data = defaultdict(lambda: defaultdict(float))
# #     for row in results:
# #         rebate_data[row.customer][row.month] += row.rebate_amount or 0

# #     return rebate_data

# # def get_customer_groups(customers):
# #     if not customers:
# #         return {}
# #     customer_groups = frappe.db.sql("""
# #         SELECT name, customer_group FROM `tabCustomer`
# #         WHERE name IN %s
# #     """, (tuple(customers),), as_dict=True)
# #     return {c.name: c.customer_group for c in customer_groups}

# # def get_data(year):
# #     start_date = f"{year}-01-01"
# #     end_date = f"{year}-12-31"

# #     item_codes = (
# #         '6287016760027', '6287016760041', '6287016760034',
# #         '6287016760058', '6287016760119', '6287016760157', '6287016760164'
# #     )

# #     deduction_accounts = {
# #         "Rebate": "41010105 - Sales Rebate/Trade Discount -حسم المبيعات /الخصم التجاري - ABNA",
# #         "Registerion": "516101 - Registerion Fees -رسوم التسجيل - ABNA",
# #         "Listing": "516102 - Listing Fees -رسوم أدخال اصناف - ABNA",
# #         "Flyer": "516107 - Flyer Fees -رسوم فلاير - ABNA",
# #         "Discount": "41010103 - Discount Allowance -الخصم المسموح به - ABNA"
# #     }

# #     months = range(1, 13)
# #     sales_data = defaultdict(lambda: defaultdict(lambda: {"sales": 0, "qty": 0}))
# #     meta_data = {}

# #     sales_results = frappe.db.sql("""
# #         SELECT
# #             sii.item_code,
# #             sii.item_name,
# #             si.customer,
# #             si.customer_group,
# #             MONTH(si.posting_date) AS month,
# #             SUM(sii.qty) AS total_qty,
# #             SUM(sii.base_net_amount) AS total_sales
# #         FROM `tabSales Invoice` si
# #         JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
# #         WHERE
# #             si.docstatus = 1
# #             AND si.posting_date BETWEEN %s AND %s
# #             AND sii.item_code IN %s
# #         GROUP BY sii.item_code, si.customer, month
# #     """, (start_date, end_date, item_codes), as_dict=True)

# #     for r in sales_results:
# #         key = (r.item_code, r.customer)
# #         sales_data[key][r.month]["sales"] += r.total_sales or 0
# #         sales_data[key][r.month]["qty"] += r.total_qty or 0

# #         mapped_channel = get_channel(r.customer_group)

# #         meta_data[key] = {
# #             "item_name": r.item_name,
# #             "customer": r.customer,
# #             "customer_group": r.customer_group,
# #             "channel": mapped_channel
# #         }

# #     def get_gl_monthly(account):
# #         gl_rows = frappe.db.sql("""
# #             SELECT MONTH(posting_date) AS month, SUM(debit - credit) AS amount
# #             FROM `tabGL Entry`
# #             WHERE account = %s AND posting_date BETWEEN %s AND %s
# #             GROUP BY month
# #         """, (account, start_date, end_date), as_dict=True)
# #         return {row.month: row.amount or 0 for row in gl_rows}

# #     monthly_deductions = {code: get_gl_monthly(account) for code, account in deduction_accounts.items()}

# #     total_deduct_monthly = {m: sum(monthly_deductions[code].get(m, 0) for code in deduction_accounts) for m in months}

# #     discount_rate_per_month = {}
# #     for m in months:
# #         total_qty_month = sum(sales_data[key][m]["qty"] for key in sales_data)
# #         discount_rate_per_month[m] = (total_deduct_monthly.get(m, 0) / total_qty_month) if total_qty_month else 0

# #     data = []
# #     totals_sales = defaultdict(float)
# #     totals_qty = defaultdict(float)

# #     # Fetch rebate data from Rebate doctype
# #     rebate_by_customer = get_monthly_rebate_by_customer(start_date, end_date)
# #     rebate_customers = list(rebate_by_customer.keys())
# #     rebate_customer_groups = get_customer_groups(rebate_customers)

# #     for key in sales_data:
# #         item_code, customer = key
# #         meta = meta_data.get(key, {})
# #         row = {
# #             "item_code": item_code,
# #             "item_name": meta.get("item_name", ""),
# #             "customer": meta.get("customer", ""),
# #             "customer_group": meta.get("customer_group", ""),
# #             "channel": meta.get("channel", "")
# #         }
# #         total_sales_sum = 0
# #         total_qty_sum = 0

# #         for m in months:
# #             m_abbr = calendar.month_abbr[m].lower()
# #             sales = sales_data[key][m]["sales"]
# #             qty = sales_data[key][m]["qty"]
# #             rate = (sales / qty) if qty else 0

# #             totals_sales[m] += sales
# #             totals_qty[m] += qty

# #             discount_rate = discount_rate_per_month.get(m, 0)
# #             net_rate = rate - discount_rate

# #             row[f"{m_abbr}_sales"] = round(sales, 2)
# #             row[f"{m_abbr}_qty"] = round(qty, 2)
# #             row[f"{m_abbr}_rate"] = round(rate, 2)
# #             row[f"{m_abbr}_discount_rate"] = round(discount_rate, 4)
# #             row[f"{m_abbr}_net_rate"] = round(net_rate, 4)

# #             total_sales_sum += sales
# #             total_qty_sum += qty

# #         total_rate = (total_sales_sum / total_qty_sum) if total_qty_sum else 0
# #         total_discount = sum(discount_rate_per_month.get(m, 0) for m in months) / 12
# #         total_net_rate = total_rate - total_discount

# #         row["total_sales"] = round(total_sales_sum, 2)
# #         row["total_qty"] = round(total_qty_sum, 2)
# #         row["total_rate"] = round(total_rate, 2)
# #         row["total_net_rate"] = round(total_net_rate, 4)
# #         data.append(row)

# #     # Total row
# #     total_row = {
# #         "item_code": "TOTAL",
# #         "item_name": "Total of All Items",
# #         "customer": "",
# #         "customer_group": "",
# #         "channel": ""
# #     }
# #     total_sales_sum_all = 0
# #     total_qty_sum_all = 0
# #     for m in months:
# #         m_abbr = calendar.month_abbr[m].lower()
# #         sales = totals_sales[m]
# #         qty = totals_qty[m]
# #         rate = (sales / qty) if qty else 0
# #         discount_rate = discount_rate_per_month.get(m, 0)
# #         net_rate = rate - discount_rate

# #         total_row[f"{m_abbr}_sales"] = round(sales, 2)
# #         total_row[f"{m_abbr}_qty"] = round(qty, 2)
# #         total_row[f"{m_abbr}_rate"] = round(rate, 2)
# #         total_row[f"{m_abbr}_discount_rate"] = round(discount_rate, 4)
# #         total_row[f"{m_abbr}_net_rate"] = round(net_rate, 4)

# #         total_sales_sum_all += sales
# #         total_qty_sum_all += qty

# #     total_row["total_sales"] = round(total_sales_sum_all, 2)
# #     total_row["total_qty"] = round(total_qty_sum_all, 2)
# #     total_row["total_rate"] = round((total_sales_sum_all / total_qty_sum_all) if total_qty_sum_all else 0, 2)
# #     total_row["total_net_rate"] = round(total_row["total_rate"] - (sum(discount_rate_per_month.values())/12), 4)
# #     data.append(total_row)

# #     # Deduction rows
# #     def make_deduction_row(code, name, monthly_data):
# #         row = {
# #             "item_code": code,
# #             "item_name": name,
# #             "customer": "",
# #             "customer_group": "",
# #             "channel": ""
# #         }
# #         total_amt = 0
# #         for m in months:
# #             m_abbr = calendar.month_abbr[m].lower()
# #             amt = monthly_data.get(m, 0)
# #             row[f"{m_abbr}_sales"] = round(amt, 2)
# #             row[f"{m_abbr}_qty"] = 0
# #             row[f"{m_abbr}_rate"] = 0
# #             row[f"{m_abbr}_discount_rate"] = 0
# #             row[f"{m_abbr}_net_rate"] = 0
# #             total_amt += amt
# #         row["total_sales"] = round(total_amt, 2)
# #         row["total_qty"] = 0
# #         row["total_rate"] = 0
# #         row["total_net_rate"] = 0
# #         return row

# #     for code, monthly in monthly_deductions.items():
# #         data.append(make_deduction_row(code, code.replace("_", " ").title(), monthly))

# #     data.append(make_deduction_row("Total Deduction", "Total Deductions (All)", total_deduct_monthly))

# #     # Discount Rate summary row
# #     discount_rate_row = {
# #         "item_code": "Discount Rate",
# #         "item_name": "Discount Rate = Total Deduct / Total Qty",
# #         "customer": "",
# #         "customer_group": "",
# #         "channel": "",
# #     }
# #     for m in months:
# #         m_abbr = calendar.month_abbr[m].lower()
# #         val = discount_rate_per_month.get(m, 0)
# #         discount_rate_row[f"{m_abbr}_sales"] = round(val, 4)
# #         discount_rate_row[f"{m_abbr}_qty"] = 0
# #         discount_rate_row[f"{m_abbr}_rate"] = 0
# #         discount_rate_row[f"{m_abbr}_discount_rate"] = 0
# #         discount_rate_row[f"{m_abbr}_net_rate"] = 0
# #     discount_rate_row["total_sales"] = 0
# #     discount_rate_row["total_qty"] = 0
# #     discount_rate_row["total_rate"] = 0
# #     discount_rate_row["total_net_rate"] = 0
# #     data.append(discount_rate_row)

# #     # --- Add rebate amount breakdown rows per customer with customer group and channel ---
# #     for customer, monthly_rebates in rebate_by_customer.items():
# #         customer_group = rebate_customer_groups.get(customer, "")
# #         channel = get_channel(customer_group)
# #         row = {
# #             "item_code": "REBATE",
# #             "item_name": "Rebate Breakdown",
# #             "customer": customer,
# #             "customer_group": customer_group,
# #             "channel": channel,
# #         }
# #         total_rebate = 0
# #         for m in months:
# #             m_abbr = calendar.month_abbr[m].lower()
# #             rebate = monthly_rebates.get(m, 0)
# #             row[f"{m_abbr}_sales"] = round(rebate, 2)
# #             row[f"{m_abbr}_qty"] = 0
# #             row[f"{m_abbr}_rate"] = 0
# #             row[f"{m_abbr}_discount_rate"] = 0
# #             row[f"{m_abbr}_net_rate"] = 0
# #             total_rebate += rebate

# #         row["total_sales"] = round(total_rebate, 2)
# #         row["total_qty"] = 0
# #         row["total_rate"] = 0
# #         row["total_net_rate"] = 0
# #         data.append(row)

# #     return data


# # import frappe
# # from collections import defaultdict
# # import calendar

# # CHANNEL_MAPPING = {
# #     "DIRECT DISTRIBUTION DD": [
# #         "EATRIES", "LARGE GROCERY", "MINIMARKET", "SMALL GROCERY",
# #         "SUPERMARKET B", "WATER SHOP", "DIRECT DISTRIBUTION DD"
# #     ],
# #     "DISTRIBUTOR": [
# #         "DISTRIBUTOR A", "DISTRIBUTOR B", "DISTRIBUTOR C", "DISTRIBUTOR"
# #     ],
# #     "HOME DELIVERY HD": [
# #         "HOUSE", "MOSQUE", "OFFICE", "SCHOOL", "HOME DELIVERY HD"
# #     ],
# #     "HORECA HO": [
# #         "CAFÉ", "CARE", "CATERING", "COMMERCIAL", "GOVERNMENTAL",
# #         "HOTEL", "INSTITUTIONAL", "RESTAURANT", "HORECA HO", "CAFE"
# #     ],
# #     "KEY ACCOUNT KA": [
# #         "E-COMMERCE", "HYPERMARKET", "SUPERMARKET-A", "SUPERMARKET-B", "KEY ACCOUNT  KA"
# #     ],
# #     "MARKETING": [
# #         "MARKETING", "DONATION", "EVENT", "SPONSORSHIP"
# #     ],
# #     "OTHER MISCELLANEOUS": [
# #         "OTHER MISCELLANEOUS", "OTHER  MISCELLANEOUS"
# #     ],
# #     "WHOLESALE": [
# #         "WHOLESALE WS", "WAREHOUSE", "WHOLESALE A", "WHOLESALE-B", "WHOLESALE-C"
# #     ]
# # }

# # def get_channel(customer_group):
# #     if not customer_group:
# #         return ""
# #     customer_group_upper = customer_group.strip().upper()
# #     for channel, groups in CHANNEL_MAPPING.items():
# #         if customer_group_upper in (g.upper() for g in groups):
# #             return channel
# #     return ""

# # def execute(filters=None):
# #     filters = filters or {}
# #     year = filters.get("year")
# #     if not year:
# #         frappe.throw("Please select a year")

# #     columns = get_columns(year)
# #     data = get_data(year)
# #     return columns, data

# # def get_columns(year):
# #     months = [calendar.month_abbr[m] for m in range(1, 13)]
# #     columns = [
# #         {"label": "Customer", "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 200},
# #         {"label": "Channel", "fieldname": "channel", "fieldtype": "Data", "width": 150},
# #         {"label": "Customer Group", "fieldname": "customer_group", "fieldtype": "Link", "options": "Customer Group", "width": 180},
# #         {"label": "Item Code", "fieldname": "item_code", "fieldtype": "Data", "width": 140},
# #         {"label": "Item Name", "fieldname": "item_name", "fieldtype": "Data", "width": 250},
# #     ]
# #     for m in months:
# #         col_prefix = m.lower()
# #         columns.append({"label": f"{m} Sales", "fieldname": f"{col_prefix}_sales", "fieldtype": "Currency", "width": 100})
# #         columns.append({"label": f"{m} Qty", "fieldname": f"{col_prefix}_qty", "fieldtype": "Float", "width": 80})
# #         columns.append({"label": f"{m} Rate", "fieldname": f"{col_prefix}_rate", "fieldtype": "Currency", "width": 80})
# #         columns.append({"label": f"{m} Discount Rate", "fieldname": f"{col_prefix}_discount_rate", "fieldtype": "Float", "width": 110})
# #         columns.append({"label": f"{m} Net Rate", "fieldname": f"{col_prefix}_net_rate", "fieldtype": "Float", "width": 110})
# #     columns += [
# #         {"label": "Total Sales", "fieldname": "total_sales", "fieldtype": "Currency", "width": 110},
# #         {"label": "Total Qty", "fieldname": "total_qty", "fieldtype": "Float", "width": 90},
# #         {"label": "Total Rate", "fieldname": "total_rate", "fieldtype": "Currency", "width": 90},
# #         {"label": "Total Net Rate", "fieldname": "total_net_rate", "fieldtype": "Currency", "width": 110},
# #     ]
# #     return columns

# # def get_monthly_rebate_by_customer(start_date, end_date):
# #     results = frappe.db.sql("""
# #         SELECT
# #             party AS customer,
# #             MONTH(posting_date) AS month,
# #             SUM(rebate_received_amount) AS rebate_amount
# #         FROM `tabRebate`
# #         WHERE
# #             docstatus = 1
# #             AND party_type = 'Customer'
# #             AND posting_date BETWEEN %s AND %s
# #         GROUP BY party, MONTH(posting_date)
# #     """, (start_date, end_date), as_dict=True)

# #     rebate_data = defaultdict(lambda: defaultdict(float))
# #     for row in results:
# #         rebate_data[row.customer][row.month] += row.rebate_amount or 0

# #     return rebate_data

# # def get_monthly_discount_by_customer(start_date, end_date):
# #     results = frappe.db.sql("""
# #         SELECT
# #             customer,
# #             MONTH(posting_date) AS month,
# #             SUM(promtion_amount) AS discount_amount
# #         FROM `tabCustomer Promotion`
# #         WHERE
# #             docstatus = 1
# #             AND posting_date BETWEEN %s AND %s
# #         GROUP BY customer, MONTH(posting_date)
# #     """, (start_date, end_date), as_dict=True)

# #     discount_data = defaultdict(lambda: defaultdict(float))
# #     for row in results:
# #         discount_data[row.customer][row.month] += row.discount_amount or 0

# #     return discount_data

# # def get_credit_note_deductions_by_customer(start_date, end_date):
# #     deduction_accounts = {
# #         "Flyer": "516107 - Flyer Fees -رسوم فلاير - ABNA",
# #         "Listing": "516102 - Listing Fees -رسوم أدخال اصناف - ABNA",
# #         "Registerion": "516101 - Registerion Fees -رسوم التسجيل - ABNA"
# #     }

# #     accounts_list = list(deduction_accounts.values())
# #     placeholders = ', '.join(['%s'] * len(accounts_list))

# #     query = f"""
# #         SELECT
# #             cn.customer,
# #             MONTH(cn.posting_date) AS month,
# #             cni.account,
# #             SUM(cni.debit - cni.credit) AS amount
# #         FROM `tabCredit Note` cn
# #         JOIN `tabJournal Entry Account` cni ON cni.parent = cn.name
# #         WHERE
# #             cn.docstatus = 1
# #             AND cn.posting_date BETWEEN %s AND %s
# #             AND cni.account IN ({placeholders})
# #         GROUP BY cn.customer, cni.account, MONTH(cn.posting_date)
# #     """

# #     params = [start_date, end_date] + accounts_list

# #     results = frappe.db.sql(query, params, as_dict=True)

# #     data = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))
# #     account_to_type = {v: k for k, v in deduction_accounts.items()}

# #     for row in results:
# #         deduction_type = account_to_type.get(row.account, "Unknown")
# #         data[row.customer][deduction_type][row.month] += row.amount or 0

# #     return data

# # def get_customer_groups(customers):
# #     if not customers:
# #         return {}
# #     customer_groups = frappe.db.sql("""
# #         SELECT name, customer_group FROM `tabCustomer`
# #         WHERE name IN %s
# #     """, (tuple(customers),), as_dict=True)
# #     return {c.name: c.customer_group for c in customer_groups}

# # def get_data(year):
# #     start_date = f"{year}-01-01"
# #     end_date = f"{year}-12-31"

# #     item_codes = (
# #         '6287016760027', '6287016760041', '6287016760034',
# #         '6287016760058', '6287016760119', '6287016760157', '6287016760164'
# #     )

# #     deduction_accounts = {
# #         "Rebate": "41010105 - Sales Rebate/Trade Discount -حسم المبيعات /الخصم التجاري - ABNA",
# #         "Registerion": "516101 - Registerion Fees -رسوم التسجيل - ABNA",
# #         "Listing": "516102 - Listing Fees -رسوم أدخال اصناف - ABNA",
# #         "Flyer": "516107 - Flyer Fees -رسوم فلاير - ABNA",
# #         "Discount": "41010103 - Discount Allowance -الخصم المسموح به - ABNA"
# #     }

# #     months = range(1, 13)
# #     sales_data = defaultdict(lambda: defaultdict(lambda: {"sales": 0, "qty": 0}))
# #     meta_data = {}

# #     sales_results = frappe.db.sql("""
# #         SELECT
# #             sii.item_code,
# #             sii.item_name,
# #             si.customer,
# #             si.customer_group,
# #             MONTH(si.posting_date) AS month,
# #             SUM(sii.qty) AS total_qty,
# #             SUM(sii.base_net_amount) AS total_sales
# #         FROM `tabSales Invoice` si
# #         JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
# #         WHERE
# #             si.docstatus = 1
# #             AND si.posting_date BETWEEN %s AND %s
# #             AND sii.item_code IN %s
# #         GROUP BY sii.item_code, si.customer, month
# #     """, (start_date, end_date, item_codes), as_dict=True)

# #     for r in sales_results:
# #         key = (r.item_code, r.customer)
# #         sales_data[key][r.month]["sales"] += r.total_sales or 0
# #         sales_data[key][r.month]["qty"] += r.total_qty or 0

# #         mapped_channel = get_channel(r.customer_group)

# #         meta_data[key] = {
# #             "item_name": r.item_name,
# #             "customer": r.customer,
# #             "customer_group": r.customer_group,
# #             "channel": mapped_channel
# #         }

# #     def get_gl_monthly(account):
# #         gl_rows = frappe.db.sql("""
# #             SELECT MONTH(posting_date) AS month, SUM(debit - credit) AS amount
# #             FROM `tabGL Entry`
# #             WHERE account = %s AND posting_date BETWEEN %s AND %s
# #             GROUP BY month
# #         """, (account, start_date, end_date), as_dict=True)
# #         return {row.month: row.amount or 0 for row in gl_rows}

# #     monthly_deductions = {code: get_gl_monthly(account) for code, account in deduction_accounts.items()}

# #     total_deduct_monthly = {m: sum(monthly_deductions[code].get(m, 0) for code in deduction_accounts) for m in months}

# #     discount_rate_per_month = {}
# #     for m in months:
# #         total_qty_month = sum(sales_data[key][m]["qty"] for key in sales_data)
# #         discount_rate_per_month[m] = (total_deduct_monthly.get(m, 0) / total_qty_month) if total_qty_month else 0

# #     data = []
# #     totals_sales = defaultdict(float)
# #     totals_qty = defaultdict(float)

# #     # Fetch rebate data from Rebate doctype
# #     rebate_by_customer = get_monthly_rebate_by_customer(start_date, end_date)
# #     rebate_customers = list(rebate_by_customer.keys())
# #     rebate_customer_groups = get_customer_groups(rebate_customers)

# #     for key in sales_data:
# #         item_code, customer = key
# #         meta = meta_data.get(key, {})
# #         row = {
# #             "item_code": item_code,
# #             "item_name": meta.get("item_name", ""),
# #             "customer": meta.get("customer", ""),
# #             "customer_group": meta.get("customer_group", ""),
# #             "channel": meta.get("channel", "")
# #         }
# #         total_sales_sum = 0
# #         total_qty_sum = 0

# #         for m in months:
# #             m_abbr = calendar.month_abbr[m].lower()
# #             sales = sales_data[key][m]["sales"]
# #             qty = sales_data[key][m]["qty"]
# #             rate = (sales / qty) if qty else 0

# #             totals_sales[m] += sales
# #             totals_qty[m] += qty

# #             discount_rate = discount_rate_per_month.get(m, 0)
# #             net_rate = rate - discount_rate

# #             row[f"{m_abbr}_sales"] = round(sales, 2)
# #             row[f"{m_abbr}_qty"] = round(qty, 2)
# #             row[f"{m_abbr}_rate"] = round(rate, 2)
# #             row[f"{m_abbr}_discount_rate"] = round(discount_rate, 4)
# #             row[f"{m_abbr}_net_rate"] = round(net_rate, 4)

# #             total_sales_sum += sales
# #             total_qty_sum += qty

# #         total_rate = (total_sales_sum / total_qty_sum) if total_qty_sum else 0
# #         total_discount = sum(discount_rate_per_month.get(m, 0) for m in months) / 12
# #         total_net_rate = total_rate - total_discount

# #         row["total_sales"] = round(total_sales_sum, 2)
# #         row["total_qty"] = round(total_qty_sum, 2)
# #         row["total_rate"] = round(total_rate, 2)
# #         row["total_net_rate"] = round(total_net_rate, 4)
# #         data.append(row)

# #     # Total row
# #     total_row = {
# #         "item_code": "TOTAL",
# #         "item_name": "Total of All Items",
# #         "customer": "",
# #         "customer_group": "",
# #         "channel": ""
# #     }
# #     total_sales_sum_all = 0
# #     total_qty_sum_all = 0
# #     for m in months:
# #         m_abbr = calendar.month_abbr[m].lower()
# #         sales = totals_sales[m]
# #         qty = totals_qty[m]
# #         rate = (sales / qty) if qty else 0
# #         discount_rate = discount_rate_per_month.get(m, 0)
# #         net_rate = rate - discount_rate

# #         total_row[f"{m_abbr}_sales"] = round(sales, 2)
# #         total_row[f"{m_abbr}_qty"] = round(qty, 2)
# #         total_row[f"{m_abbr}_rate"] = round(rate, 2)
# #         total_row[f"{m_abbr}_discount_rate"] = round(discount_rate, 4)
# #         total_row[f"{m_abbr}_net_rate"] = round(net_rate, 4)

# #         total_sales_sum_all += sales
# #         total_qty_sum_all += qty

# #     total_row["total_sales"] = round(total_sales_sum_all, 2)
# #     total_row["total_qty"] = round(total_qty_sum_all, 2)
# #     total_row["total_rate"] = round((total_sales_sum_all / total_qty_sum_all) if total_qty_sum_all else 0, 2)
# #     total_row["total_net_rate"] = round(total_row["total_rate"] - (sum(discount_rate_per_month.values()) / 12), 4)
# #     data.append(total_row)

# #     # Deduction rows
# #     def make_deduction_row(code, name, monthly_data):
# #         row = {
# #             "item_code": code,
# #             "item_name": name,
# #             "customer": "",
# #             "customer_group": "",
# #             "channel": ""
# #         }
# #         total_amt = 0
# #         for m in months:
# #             m_abbr = calendar.month_abbr[m].lower()
# #             amt = monthly_data.get(m, 0)
# #             row[f"{m_abbr}_sales"] = round(amt, 2)
# #             row[f"{m_abbr}_qty"] = 0
# #             row[f"{m_abbr}_rate"] = 0
# #             row[f"{m_abbr}_discount_rate"] = 0
# #             row[f"{m_abbr}_net_rate"] = 0
# #             total_amt += amt
# #         row["total_sales"] = round(total_amt, 2)
# #         row["total_qty"] = 0
# #         row["total_rate"] = 0
# #         row["total_net_rate"] = 0
# #         return row

# #     for code, monthly in monthly_deductions.items():
# #         data.append(make_deduction_row(code, code.replace("_", " ").title(), monthly))

# #     data.append(make_deduction_row("Total Deduction", "Total Deductions (All)", total_deduct_monthly))

# #     # Discount Rate summary row
# #     discount_rate_row = {
# #         "item_code": "Discount Rate",
# #         "item_name": "Discount Rate = Total Deduct / Total Qty",
# #         "customer": "",
# #         "customer_group": "",
# #         "channel": "",
# #     }
# #     for m in months:
# #         m_abbr = calendar.month_abbr[m].lower()
# #         val = discount_rate_per_month.get(m, 0)
# #         discount_rate_row[f"{m_abbr}_sales"] = round(val, 4)
# #         discount_rate_row[f"{m_abbr}_qty"] = 0
# #         discount_rate_row[f"{m_abbr}_rate"] = 0
# #         discount_rate_row[f"{m_abbr}_discount_rate"] = 0
# #         discount_rate_row[f"{m_abbr}_net_rate"] = 0
# #     discount_rate_row["total_sales"] = 0
# #     discount_rate_row["total_qty"] = 0
# #     discount_rate_row["total_rate"] = 0
# #     discount_rate_row["total_net_rate"] = 0
# #     data.append(discount_rate_row)

# #     # --- Add rebate amount breakdown rows per customer with customer group and channel ---
# #     for customer, monthly_rebates in rebate_by_customer.items():
# #         customer_group = rebate_customer_groups.get(customer, "")
# #         channel = get_channel(customer_group)
# #         row = {
# #             "item_code": "REBATE",
# #             "item_name": "Rebate Breakdown",
# #             "customer": customer,
# #             "customer_group": customer_group,
# #             "channel": channel,
# #         }
# #         total_rebate = 0
# #         for m in months:
# #             m_abbr = calendar.month_abbr[m].lower()
# #             rebate = monthly_rebates.get(m, 0)
# #             row[f"{m_abbr}_sales"] = round(-rebate, 2)
# #             row[f"{m_abbr}_qty"] = 0
# #             row[f"{m_abbr}_rate"] = 0
# #             row[f"{m_abbr}_discount_rate"] = 0
# #             row[f"{m_abbr}_net_rate"] = 0
# #             total_rebate += rebate

# #         row["total_sales"] = round(-total_rebate, 2)
# #         row["total_qty"] = 0
# #         row["total_rate"] = 0
# #         row["total_net_rate"] = 0
# #         data.append(row)

# #     # --- Add discount amount breakdown rows per customer with customer group and channel ---
# #     discount_by_customer = get_monthly_discount_by_customer(start_date, end_date)
# #     discount_customers = list(discount_by_customer.keys())
# #     discount_customer_groups = get_customer_groups(discount_customers)

# #     for customer, monthly_discounts in discount_by_customer.items():
# #         customer_group = discount_customer_groups.get(customer, "")
# #         channel = get_channel(customer_group)
# #         row = {
# #             "item_code": "DISCOUNT",
# #             "item_name": "Discount Breakdown",
# #             "customer": customer,
# #             "customer_group": customer_group,
# #             "channel": channel,
# #         }
# #         total_discount = 0
# #         for m in months:
# #             m_abbr = calendar.month_abbr[m].lower()
# #             discount = monthly_discounts.get(m, 0)
# #             row[f"{m_abbr}_sales"] = round(-discount, 2)
# #             row[f"{m_abbr}_qty"] = 0
# #             row[f"{m_abbr}_rate"] = 0
# #             row[f"{m_abbr}_discount_rate"] = 0
# #             row[f"{m_abbr}_net_rate"] = 0
# #             total_discount += discount

# #         row["total_sales"] = round(-total_discount, 2)
# #         row["total_qty"] = 0
# #         row["total_rate"] = 0
# #         row["total_net_rate"] = 0
# #         data.append(row)

# #     # --- Add Flyer, Listing, Registerion breakdown rows per customer from Credit Note ---
# #     credit_note_deductions = get_credit_note_deductions_by_customer(start_date, end_date)
# #     credit_note_customers = list(credit_note_deductions.keys())
# #     credit_note_customer_groups = get_customer_groups(credit_note_customers)

# #     for customer, deductions in credit_note_deductions.items():
# #         customer_group = credit_note_customer_groups.get(customer, "")
# #         channel = get_channel(customer_group)

# #         for deduction_type, monthly_values in deductions.items():
# #             row = {
# #                 "item_code": "CREDIT NOTE - " + deduction_type.upper(),
# #                 "item_name": f"{deduction_type} Deduction Breakdown",
# #                 "customer": customer,
# #                 "customer_group": customer_group,
# #                 "channel": channel,
# #             }
# #             total_amount = 0
# #             for m in months:
# #                 m_abbr = calendar.month_abbr[m].lower()
# #                 amount = monthly_values.get(m, 0)
# #                 row[f"{m_abbr}_sales"] = round(-amount, 2)
# #                 row[f"{m_abbr}_qty"] = 0
# #                 row[f"{m_abbr}_rate"] = 0
# #                 row[f"{m_abbr}_discount_rate"] = 0
# #                 row[f"{m_abbr}_net_rate"] = 0
# #                 total_amount += amount

# #             row["total_sales"] = round(-total_amount, 2)
# #             row["total_qty"] = 0
# #             row["total_rate"] = 0
# #             row["total_net_rate"] = 0
# #             data.append(row)

    

# #     return data


# # import frappe
# # from collections import defaultdict
# # import calendar

# # CHANNEL_MAPPING = {
# #     "DIRECT DISTRIBUTION DD": [
# #         "EATRIES", "LARGE GROCERY", "MINIMARKET", "SMALL GROCERY",
# #         "SUPERMARKET B", "WATER SHOP", "DIRECT DISTRIBUTION DD"
# #     ],
# #     "DISTRIBUTOR": [
# #         "DISTRIBUTOR A", "DISTRIBUTOR B", "DISTRIBUTOR C", "DISTRIBUTOR"
# #     ],
# #     "HOME DELIVERY HD": [
# #         "HOUSE", "MOSQUE", "OFFICE", "SCHOOL", "HOME DELIVERY HD"
# #     ],
# #     "HORECA HO": [
# #         "CAFÉ", "CARE", "CATERING", "COMMERCIAL", "GOVERNMENTAL",
# #         "HOTEL", "INSTITUTIONAL", "RESTAURANT", "HORECA HO", "CAFE"
# #     ],
# #     "KEY ACCOUNT KA": [
# #         "E-COMMERCE", "HYPERMARKET", "SUPERMARKET-A", "SUPERMARKET-B", "KEY ACCOUNT  KA"
# #     ],
# #     "MARKETING": [
# #         "MARKETING", "DONATION", "EVENT", "SPONSORSHIP"
# #     ],
# #     "OTHER MISCELLANEOUS": [
# #         "OTHER MISCELLANEOUS", "OTHER  MISCELLANEOUS"
# #     ],
# #     "WHOLESALE": [
# #         "WHOLESALE WS", "WAREHOUSE", "WHOLESALE A", "WHOLESALE-B", "WHOLESALE-C"
# #     ]
# # }

# # def get_channel(customer_group):
# #     if not customer_group:
# #         return ""
# #     customer_group_upper = customer_group.strip().upper()
# #     for channel, groups in CHANNEL_MAPPING.items():
# #         if customer_group_upper in (g.upper() for g in groups):
# #             return channel
# #     return ""

# # def execute(filters=None):
# #     filters = filters or {}
# #     year = filters.get("year")
# #     if not year:
# #         frappe.throw("Please select a year")

# #     columns = get_columns(year)
# #     data = get_data(year)
# #     return columns, data

# # def get_columns(year):
# #     months = [calendar.month_abbr[m] for m in range(1, 13)]
# #     columns = [
# #         {"label": "Channel", "fieldname": "channel", "fieldtype": "Data", "width": 150},
# #         {"label": "Item Code", "fieldname": "item_code", "fieldtype": "Data", "width": 140},
# #         {"label": "Item Name", "fieldname": "item_name", "fieldtype": "Data", "width": 250},
# #     ]
# #     for m in months:
# #         col_prefix = m.lower()
# #         columns.append({"label": f"{m} Sales", "fieldname": f"{col_prefix}_sales", "fieldtype": "Currency", "width": 100})
# #         columns.append({"label": f"{m} Qty", "fieldname": f"{col_prefix}_qty", "fieldtype": "Float", "width": 80})
# #         columns.append({"label": f"{m} Rate", "fieldname": f"{col_prefix}_rate", "fieldtype": "Currency", "width": 80})
# #         columns.append({"label": f"{m} Discount Rate", "fieldname": f"{col_prefix}_discount_rate", "fieldtype": "Float", "width": 110})
# #         columns.append({"label": f"{m} Net Rate", "fieldname": f"{col_prefix}_net_rate", "fieldtype": "Float", "width": 110})
# #     columns += [
# #         {"label": "Total Sales", "fieldname": "total_sales", "fieldtype": "Currency", "width": 110},
# #         {"label": "Total Qty", "fieldname": "total_qty", "fieldtype": "Float", "width": 90},
# #         {"label": "Total Rate", "fieldname": "total_rate", "fieldtype": "Currency", "width": 90},
# #         {"label": "Total Net Rate", "fieldname": "total_net_rate", "fieldtype": "Currency", "width": 110},
# #     ]
# #     return columns

# # def get_monthly_rebate_by_channel(start_date, end_date):
# #     results = frappe.db.sql("""
# #         SELECT
# #             cu.customer_group,
# #             MONTH(r.posting_date) AS month,
# #             SUM(r.rebate_received_amount) AS rebate_amount
# #         FROM `tabRebate` r
# #         JOIN `tabCustomer` cu ON cu.name = r.party
# #         WHERE
# #             r.docstatus = 1
# #             AND r.party_type = 'Customer'
# #             AND r.posting_date BETWEEN %s AND %s
# #         GROUP BY cu.customer_group, MONTH(r.posting_date)
# #     """, (start_date, end_date), as_dict=True)

# #     rebate_data = defaultdict(lambda: defaultdict(float))
# #     for row in results:
# #         channel = get_channel(row.customer_group)
# #         rebate_data[channel][row.month] += row.rebate_amount or 0

# #     return rebate_data

# # def get_monthly_discount_by_channel(start_date, end_date):
# #     results = frappe.db.sql("""
# #         SELECT
# #             cu.customer_group,
# #             MONTH(cp.posting_date) AS month,
# #             SUM(cp.promtion_amount) AS discount_amount
# #         FROM `tabCustomer Promotion` cp
# #         JOIN `tabCustomer` cu ON cu.name = cp.customer
# #         WHERE
# #             cp.docstatus = 1
# #             AND cp.posting_date BETWEEN %s AND %s
# #         GROUP BY cu.customer_group, MONTH(cp.posting_date)
# #     """, (start_date, end_date), as_dict=True)

# #     discount_data = defaultdict(lambda: defaultdict(float))
# #     for row in results:
# #         channel = get_channel(row.customer_group)
# #         discount_data[channel][row.month] += row.discount_amount or 0

# #     return discount_data

# # def get_credit_note_deductions_by_channel(start_date, end_date):
# #     deduction_accounts = {
# #         "Flyer": "516107 - Flyer Fees -رسوم فلاير - ABNA",
# #         "Listing": "516102 - Listing Fees -رسوم أدخال اصناف - ABNA",
# #         "Registerion": "516101 - Registerion Fees -رسوم التسجيل - ABNA"
# #     }

# #     accounts_list = list(deduction_accounts.values())
# #     placeholders = ', '.join(['%s'] * len(accounts_list))

# #     query = f"""
# #         SELECT
# #             cu.customer_group,
# #             MONTH(cn.posting_date) AS month,
# #             cni.account,
# #             SUM(cni.debit - cni.credit) AS amount
# #         FROM `tabCredit Note` cn
# #         JOIN `tabJournal Entry Account` cni ON cni.parent = cn.name
# #         JOIN `tabCustomer` cu ON cu.name = cn.customer
# #         WHERE
# #             cn.docstatus = 1
# #             AND cn.posting_date BETWEEN %s AND %s
# #             AND cni.account IN ({placeholders})
# #         GROUP BY cu.customer_group, cni.account, MONTH(cn.posting_date)
# #     """

# #     params = [start_date, end_date] + accounts_list

# #     results = frappe.db.sql(query, params, as_dict=True)

# #     data = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))
# #     account_to_type = {v: k for k, v in deduction_accounts.items()}

# #     for row in results:
# #         channel = get_channel(row.customer_group)
# #         deduction_type = account_to_type.get(row.account, "Unknown")
# #         data[channel][deduction_type][row.month] += row.amount or 0

# #     return data

# # def get_data(year):
# #     start_date = f"{year}-01-01"
# #     end_date = f"{year}-12-31"

# #     # All relevant item codes
# #     item_codes = (
# #         '6287016760027', '6287016760041', '6287016760034',
# #         '6287016760058', '6287016760119', '6287016760157', '6287016760164'
# #     )

# #     # Define item grouping mapping (child item_code -> parent item_code)
# #     item_group_map = {
# #         '6287016760119': '6287016760027',
# #         '6287016760157': '6287016760027',
# #         '6287016760058': '6287016760041',
# #         '6287016760164': '6287016760041',
# #     }

# #     deduction_accounts = {
# #         "Rebate": "41010105 - Sales Rebate/Trade Discount -حسم المبيعات /الخصم التجاري - ABNA",
# #         "Registerion": "516101 - Registerion Fees -رسوم التسجيل - ABNA",
# #         "Listing": "516102 - Listing Fees -رسوم أدخال اصناف - ABNA",
# #         "Flyer": "516107 - Flyer Fees -رسوم فلاير - ABNA",
# #         "Discount": "41010103 - Discount Allowance -الخصم المسموح به - ABNA"
# #     }

# #     months = range(1, 13)

# #     sales_results = frappe.db.sql("""
# #         SELECT
# #             sii.item_code,
# #             sii.item_name,
# #             si.customer_group,
# #             MONTH(si.posting_date) AS month,
# #             SUM(sii.qty) AS total_qty,
# #             SUM(sii.base_net_amount) AS total_sales
# #         FROM `tabSales Invoice` si
# #         JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
# #         WHERE
# #             si.docstatus = 1
# #             AND si.posting_date BETWEEN %s AND %s
# #             AND sii.item_code IN %s
# #         GROUP BY sii.item_code, si.customer_group, month
# #     """, (start_date, end_date, item_codes), as_dict=True)

# #     sales_data = defaultdict(lambda: defaultdict(lambda: {"sales": 0, "qty": 0}))
# #     meta_data = {}
# #     channel_totals = defaultdict(lambda: defaultdict(lambda: {"sales": 0, "qty": 0}))

# #     for r in sales_results:
# #         # Map child item to parent if exists
# #         parent_item_code = item_group_map.get(r.item_code, r.item_code)
# #         channel = get_channel(r.customer_group)
# #         key = (channel, parent_item_code)

# #         sales_data[key][r.month]["sales"] += r.total_sales or 0
# #         sales_data[key][r.month]["qty"] += r.total_qty or 0

# #         # Aggregate channel-wise totals
# #         channel_totals[channel][r.month]["sales"] += r.total_sales or 0
# #         channel_totals[channel][r.month]["qty"] += r.total_qty or 0

# #         if key not in meta_data:
# #             # Get parent item name from DB or fallback
# #             if parent_item_code == r.item_code:
# #                 item_name = r.item_name
# #             else:
# #                 item_name = frappe.db.get_value("Item", parent_item_code, "item_name") or r.item_name

# #             meta_data[key] = {
# #                 "item_name": item_name,
# #                 "channel": channel,
# #                 "item_code": parent_item_code
# #             }

# #     def get_gl_monthly(account):
# #         gl_rows = frappe.db.sql("""
# #             SELECT MONTH(posting_date) AS month, SUM(debit - credit) AS amount
# #             FROM `tabGL Entry`
# #             WHERE account = %s AND posting_date BETWEEN %s AND %s
# #             GROUP BY month
# #         """, (account, start_date, end_date), as_dict=True)
# #         return {row.month: row.amount or 0 for row in gl_rows}

# #     monthly_deductions = {code: get_gl_monthly(account) for code, account in deduction_accounts.items()}
# #     months_list = list(months)
# #     total_deduct_monthly = {m: sum(monthly_deductions[code].get(m, 0) for code in deduction_accounts) for m in months}

# #     # Calculate channel-wise total deductions
# #     rebate_by_channel = get_monthly_rebate_by_channel(start_date, end_date)
# #     discount_by_channel = get_monthly_discount_by_channel(start_date, end_date)
# #     credit_note_deductions = get_credit_note_deductions_by_channel(start_date, end_date)

# #     total_deductions_by_channel = defaultdict(lambda: defaultdict(float))
# #     for channel, monthly_data in rebate_by_channel.items():
# #         for m, v in monthly_data.items():
# #             total_deductions_by_channel[channel][m] += v
# #     for channel, monthly_data in discount_by_channel.items():
# #         for m, v in monthly_data.items():
# #             total_deductions_by_channel[channel][m] += v
# #     for channel, deduction_types in credit_note_deductions.items():
# #         for monthly_data in deduction_types.values():
# #             for m, v in monthly_data.items():
# #                 total_deductions_by_channel[channel][m] += v

# #     # Calculate channel-wise discount rate (Total Deductions / Sales Qty)
# #     channel_discount_rate = defaultdict(lambda: defaultdict(float))
# #     for channel in channel_totals:
# #         for m in months:
# #             total_qty = channel_totals[channel][m]["qty"]
# #             total_deductions = total_deductions_by_channel[channel][m]
# #             channel_discount_rate[channel][m] = (total_deductions / total_qty) if total_qty else 0

# #     # Overall discount rate for net rate calculations (unchanged)
# #     discount_rate_per_month = {}
# #     for m in months:
# #         total_qty_month = sum(channel_totals[channel][m]["qty"] for channel in channel_totals)
# #         discount_rate_per_month[m] = (total_deduct_monthly.get(m, 0) / total_qty_month) if total_qty_month else 0

# #     data = []
# #     totals_sales = defaultdict(float)
# #     totals_qty = defaultdict(float)

# #     # Sales Data Rows grouped by Channel and Item
# #     for key in sales_data:
# #         channel, item_code = key
# #         meta = meta_data.get(key, {})
# #         row = {
# #             "channel": channel,
# #             "item_code": item_code,
# #             "item_name": meta.get("item_name", "")
# #         }
# #         total_sales_sum = 0
# #         total_qty_sum = 0

# #         for m in months:
# #             m_abbr = calendar.month_abbr[m].lower()
# #             sales = sales_data[key][m]["sales"]
# #             qty = sales_data[key][m]["qty"]
# #             rate = (sales / qty) if qty else 0

# #             totals_sales[m] += sales
# #             totals_qty[m] += qty

# #             discount_rate = discount_rate_per_month.get(m, 0)
# #             net_rate = rate - discount_rate

# #             row[f"{m_abbr}_sales"] = round(sales, 2)
# #             row[f"{m_abbr}_qty"] = round(qty, 2)
# #             row[f"{m_abbr}_rate"] = round(rate, 2)
# #             row[f"{m_abbr}_discount_rate"] = round(discount_rate, 4)
# #             row[f"{m_abbr}_net_rate"] = round(net_rate, 4)

# #             total_sales_sum += sales
# #             total_qty_sum += qty

# #         total_rate = (total_sales_sum / total_qty_sum) if total_qty_sum else 0
# #         total_discount = sum(discount_rate_per_month.get(m, 0) for m in months) / 12
# #         total_net_rate = total_rate - total_discount

# #         row["total_sales"] = round(total_sales_sum, 2)
# #         row["total_qty"] = round(total_qty_sum, 2)
# #         row["total_rate"] = round(total_rate, 2)
# #         row["total_net_rate"] = round(total_net_rate, 4)
# #         data.append(row)

# #     # Channel-wise total rows
# #     for channel in channel_totals:
# #         row = {
# #             "channel": channel,
# #             "item_code": "",
# #             "item_name": f"Total for {channel}",
# #         }
# #         total_sales_sum = 0
# #         total_qty_sum = 0

# #         for m in months:
# #             m_abbr = calendar.month_abbr[m].lower()
# #             sales = channel_totals[channel][m]["sales"]
# #             qty = channel_totals[channel][m]["qty"]
# #             rate = (sales / qty) if qty else 0
# #             discount_rate = discount_rate_per_month.get(m, 0)
# #             net_rate = rate - discount_rate

# #             row[f"{m_abbr}_sales"] = round(sales, 2)
# #             row[f"{m_abbr}_qty"] = round(qty, 2)
# #             row[f"{m_abbr}_rate"] = round(rate, 2)
# #             row[f"{m_abbr}_discount_rate"] = round(discount_rate, 4)
# #             row[f"{m_abbr}_net_rate"] = round(net_rate, 4)

# #             total_sales_sum += sales
# #             total_qty_sum += qty

# #         total_rate = (total_sales_sum / total_qty_sum) if total_qty_sum else 0
# #         total_net_rate = total_rate - (sum(discount_rate_per_month.get(m, 0) for m in months) / 12)

# #         row["total_sales"] = round(total_sales_sum, 2)
# #         row["total_qty"] = round(total_qty_sum, 2)
# #         row["total_rate"] = round(total_rate, 2)
# #         row["total_net_rate"] = round(total_net_rate, 4)
# #         data.append(row)

# #     # Total row for all sales grouped by channel
# #     total_row = {
# #         "channel": "TOTAL",
# #         "item_code": "",
# #         "item_name": "Total of All Items",
# #     }
# #     total_sales_sum_all = 0
# #     total_qty_sum_all = 0
# #     for m in months:
# #         m_abbr = calendar.month_abbr[m].lower()
# #         sales = totals_sales[m]
# #         qty = totals_qty[m]
# #         rate = (sales / qty) if qty else 0
# #         discount_rate = discount_rate_per_month.get(m, 0)
# #         net_rate = rate - discount_rate

# #         total_row[f"{m_abbr}_sales"] = round(sales, 2)
# #         total_row[f"{m_abbr}_qty"] = round(qty, 2)
# #         total_row[f"{m_abbr}_rate"] = round(rate, 2)
# #         total_row[f"{m_abbr}_discount_rate"] = round(discount_rate, 4)
# #         total_row[f"{m_abbr}_net_rate"] = round(net_rate, 4)

# #         total_sales_sum_all += sales
# #         total_qty_sum_all += qty

# #     total_row["total_sales"] = round(total_sales_sum_all, 2)
# #     total_row["total_qty"] = round(total_qty_sum_all, 2)
# #     total_row["total_rate"] = round((total_sales_sum_all / total_qty_sum_all) if total_qty_sum_all else 0, 2)
# #     total_row["total_net_rate"] = round(total_row["total_rate"] - (sum(discount_rate_per_month.values()) / 12), 4)
# #     data.append(total_row)

# #     # Deduction rows by channel
# #     def make_deduction_row(channel, code, name, monthly_data):
# #         row = {
# #             "channel": channel,
# #             "item_code": code,
# #             "item_name": name,
# #         }
# #         total_amt = 0
# #         for m in months:
# #             m_abbr = calendar.month_abbr[m].lower()
# #             amt = monthly_data.get(m, 0)
# #             row[f"{m_abbr}_sales"] = round(-amt, 2)  # Negative as deduction
# #             row[f"{m_abbr}_qty"] = 0
# #             row[f"{m_abbr}_rate"] = 0
# #             row[f"{m_abbr}_discount_rate"] = 0
# #             row[f"{m_abbr}_net_rate"] = 0
# #             total_amt += amt
# #         row["total_sales"] = round(-total_amt, 2)
# #         row["total_qty"] = 0
# #         row["total_rate"] = 0
# #         row["total_net_rate"] = 0
# #         return row

# #     # Add rebate rows grouped by channel
# #     for channel, monthly_data in rebate_by_channel.items():
# #         data.append(make_deduction_row(channel, "REBATE", "Rebate Breakdown", monthly_data))

# #     # Add discount rows grouped by channel
# #     for channel, monthly_data in discount_by_channel.items():
# #         data.append(make_deduction_row(channel, "DISCOUNT", "Discount Breakdown", monthly_data))

# #     # Add credit note deduction rows grouped by channel and deduction type
# #     for channel, deduction_types in credit_note_deductions.items():
# #         for deduction_type, monthly_values in deduction_types.items():
# #             data.append(make_deduction_row(channel, f"CREDIT NOTE - {deduction_type.upper()}",
# #                                           f"{deduction_type} Deduction Breakdown", monthly_values))

# #     # Total deductions by channel row
# #     for channel, monthly_totals in total_deductions_by_channel.items():
# #         data.append(make_deduction_row(channel, "TOTAL DEDUCTION", "Total Deductions (All)", monthly_totals))

# #     # Channel-wise discount rate rows (Total Deductions / Sales Qty), only if non-zero
# #     for channel in channel_totals:
# #         # Check if any month has a non-zero discount rate
# #         has_non_zero_discount = any(channel_discount_rate[channel][m] != 0 for m in months)
# #         if has_non_zero_discount:
# #             row = {
# #                 "channel": channel,
# #                 "item_code": "",
# #                 "item_name": f"Discount Rate for {channel} (Total Deductions / Sales Qty)",
# #             }
# #             for m in months:
# #                 m_abbr = calendar.month_abbr[m].lower()
# #                 discount_rate = channel_discount_rate[channel][m]
# #                 row[f"{m_abbr}_sales"] = round(discount_rate, 4)
# #                 row[f"{m_abbr}_qty"] = 0
# #                 row[f"{m_abbr}_rate"] = 0
# #                 row[f"{m_abbr}_discount_rate"] = 0
# #                 row[f"{m_abbr}_net_rate"] = 0
# #             row["total_sales"] = 0
# #             row["total_qty"] = 0
# #             row["total_rate"] = 0
# #             row["total_net_rate"] = 0
# #             data.append(row)

# #     return data


# import frappe
# from collections import defaultdict
# import calendar

# CHANNEL_MAPPING = {
#     "DIRECT DISTRIBUTION DD": [
#         "EATRIES", "LARGE GROCERY", "MINIMARKET", "SMALL GROCERY",
#         "SUPERMARKET B", "WATER SHOP", "DIRECT DISTRIBUTION DD"
#     ],
#     "DISTRIBUTOR": [
#         "DISTRIBUTOR A", "DISTRIBUTOR B", "DISTRIBUTOR C", "DISTRIBUTOR"
#     ],
#     "HOME DELIVERY HD": [
#         "HOUSE", "MOSQUE", "OFFICE", "SCHOOL", "HOME DELIVERY HD"
#     ],
#     "HORECA HO": [
#         "CAFÉ", "CARE", "CATERING", "COMMERCIAL", "GOVERNMENTAL",
#         "HOTEL", "INSTITUTIONAL", "RESTAURANT", "HORECA HO", "CAFE"
#     ],
#     "KEY ACCOUNT KA": [
#         "E-COMMERCE", "HYPERMARKET", "SUPERMARKET-A", "SUPERMARKET-B", "KEY ACCOUNT  KA"
#     ],
#     "MARKETING": [
#         "MARKETING", "DONATION", "EVENT", "SPONSORSHIP"
#     ],
#     "OTHER MISCELLANEOUS": [
#         "OTHER MISCELLANEOUS", "OTHER  MISCELLANEOUS"
#     ],
#     "WHOLESALE": [
#         "WHOLESALE WS", "WAREHOUSE", "WHOLESALE A", "WHOLESALE-B", "WHOLESALE-C"
#     ]
# }

# def get_channel(customer_group):
#     if not customer_group:
#         return ""
#     customer_group_upper = customer_group.strip().upper()
#     for channel, groups in CHANNEL_MAPPING.items():
#         if customer_group_upper in (g.upper() for g in groups):
#             return channel
#     return ""

# def execute(filters=None):
#     filters = filters or {}
#     year = filters.get("year")
#     if not year:
#         frappe.throw("Please select a year")

#     columns = get_columns(year)
#     data = get_data(year)
#     return columns, data

# def get_columns(year):
#     months = [calendar.month_abbr[m] for m in range(1, 13)]
#     columns = [
#         {"label": "Channel", "fieldname": "channel", "fieldtype": "Data", "width": 150},
#         {"label": "Item Code", "fieldname": "item_code", "fieldtype": "Data", "width": 140},
#         {"label": "Item Name", "fieldname": "item_name", "fieldtype": "Data", "width": 250},
#     ]

#     for m in months:
#         m_lower = m.lower()
#         columns.append({"label": f"{m} Sales", "fieldname": f"{m_lower}_sales", "fieldtype": "Currency", "width": 100})
#         columns.append({"label": f"{m} Qty", "fieldname": f"{m_lower}_qty", "fieldtype": "Float", "width": 80})
#         columns.append({"label": f"{m} Rate", "fieldname": f"{m_lower}_rate", "fieldtype": "Currency", "width": 80})
#         # columns.append({"label": f"{m} Discount Rate", "fieldname": f"{m_lower}_discount_rate", "fieldtype": "Float", "width": 110})
#         # columns.append({"label": f"{m} Net Rate", "fieldname": f"{m_lower}_net_rate", "fieldtype": "Float", "width": 110})
#         columns.append({"label": f"{m} Net Rate (After %)", "fieldname": f"{m_lower}_net_rate", "fieldtype": "Float", "width": 130})
#         columns.append({"label": f"{m} Channel Discount", "fieldname": f"{m_lower}_channel_discount", "fieldtype": "Currency", "width": 120})
#         # columns.append({"label": f"{m} Channel Discount Rate", "fieldname": f"{m_lower}_channel_discount_rate", "fieldtype": "Float", "width": 130})
#         columns.append({"label": f"{m} Channel Discount Rate (%)", "fieldname": f"{m_lower}_channel_discount_rate", "fieldtype": "Percent", "width": 130})

#     columns += [
#         {"label": "Total Sales", "fieldname": "total_sales", "fieldtype": "Currency", "width": 110},
#         {"label": "Total Qty", "fieldname": "total_qty", "fieldtype": "Float", "width": 90},
#         {"label": "Total Rate", "fieldname": "total_rate", "fieldtype": "Currency", "width": 90},
#         {"label": "Total Net Rate", "fieldname": "total_net_rate", "fieldtype": "Currency", "width": 110},
#     ]
#     return columns

# def get_monthly_rebate_by_channel(start_date, end_date):
#     results = frappe.db.sql("""
#         SELECT
#             cu.customer_group,
#             MONTH(r.posting_date) AS month,
#             SUM(r.rebate_received_amount) AS rebate_amount
#         FROM `tabRebate` r
#         JOIN `tabCustomer` cu ON cu.name = r.party
#         WHERE
#             r.docstatus = 1
#             AND r.party_type = 'Customer'
#             AND r.posting_date BETWEEN %s AND %s
#         GROUP BY cu.customer_group, MONTH(r.posting_date)
#     """, (start_date, end_date), as_dict=True)

#     rebate_data = defaultdict(lambda: defaultdict(float))
#     for row in results:
#         channel = get_channel(row.customer_group)
#         rebate_data[channel][row.month] += row.rebate_amount or 0

#     return rebate_data

# def get_monthly_discount_by_channel(start_date, end_date):
#     results = frappe.db.sql("""
#         SELECT
#             cu.customer_group,
#             MONTH(cp.posting_date) AS month,
#             SUM(cp.promtion_amount) AS discount_amount
#         FROM `tabCustomer Promotion` cp
#         JOIN `tabCustomer` cu ON cu.name = cp.customer
#         WHERE
#             cp.docstatus = 1
#             AND cp.posting_date BETWEEN %s AND %s
#         GROUP BY cu.customer_group, MONTH(cp.posting_date)
#     """, (start_date, end_date), as_dict=True)

#     discount_data = defaultdict(lambda: defaultdict(float))
#     for row in results:
#         channel = get_channel(row.customer_group)
#         discount_data[channel][row.month] += row.discount_amount or 0

#     return discount_data

# def get_credit_note_deductions_by_channel(start_date, end_date):
#     deduction_accounts = {
#         "Flyer": "516107 - Flyer Fees -رسوم فلاير - ABNA",
#         "Listing": "516102 - Listing Fees -رسوم أدخال اصناف - ABNA",
#         "Registerion": "516101 - Registerion Fees -رسوم التسجيل - ABNA"
#     }

#     accounts_list = list(deduction_accounts.values())
#     placeholders = ', '.join(['%s'] * len(accounts_list))

#     query = f"""
#         SELECT
#             cu.customer_group,
#             MONTH(cn.posting_date) AS month,
#             cni.account,
#             SUM(cni.debit - cni.credit) AS amount
#         FROM `tabCredit Note` cn
#         JOIN `tabJournal Entry Account` cni ON cni.parent = cn.name
#         JOIN `tabCustomer` cu ON cu.name = cn.customer
#         WHERE
#             cn.docstatus = 1
#             AND cn.posting_date BETWEEN %s AND %s
#             AND cni.account IN ({placeholders})
#         GROUP BY cu.customer_group, cni.account, MONTH(cn.posting_date)
#     """

#     params = [start_date, end_date] + accounts_list

#     results = frappe.db.sql(query, params, as_dict=True)

#     data = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))
#     account_to_type = {v: k for k, v in deduction_accounts.items()}

#     for row in results:
#         channel = get_channel(row.customer_group)
#         deduction_type = account_to_type.get(row.account, "Unknown")
#         data[channel][deduction_type][row.month] += row.amount or 0

#     return data

# # def get_data(year):
# #     start_date = f"{year}-01-01"
# #     end_date = f"{year}-12-31"

# #     # All relevant item codes
# #     item_codes = (
# #         '6287016760027', '6287016760041', '6287016760034',
# #         '6287016760058', '6287016760119', '6287016760157', '6287016760164'
# #     )

# #     # Define item grouping mapping (child item_code -> parent item_code)
# #     item_group_map = {
# #         '6287016760119': '6287016760027',
# #         '6287016760157': '6287016760027',
# #         '6287016760058': '6287016760041',
# #         '6287016760164': '6287016760041',
# #     }

# #     deduction_accounts = {
# #         "Rebate": "41010105 - Sales Rebate/Trade Discount -حسم المبيعات /الخصم التجاري - ABNA",
# #         "Registerion": "516101 - Registerion Fees -رسوم التسجيل - ABNA",
# #         "Listing": "516102 - Listing Fees -رسوم أدخال اصناف - ABNA",
# #         "Flyer": "516107 - Flyer Fees -رسوم فلاير - ABNA",
# #         "Discount": "41010103 - Discount Allowance -الخصم المسموح به - ABNA"
# #     }

# #     months = range(1, 13)

# #     sales_results = frappe.db.sql("""
# #         SELECT
# #             sii.item_code,
# #             sii.item_name,
# #             si.customer_group,
# #             MONTH(si.posting_date) AS month,
# #             SUM(sii.qty) AS total_qty,
# #             SUM(sii.base_net_amount) AS total_sales
# #         FROM `tabSales Invoice` si
# #         JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
# #         WHERE
# #             si.docstatus = 1
# #             AND si.posting_date BETWEEN %s AND %s
# #             AND sii.item_code IN %s
# #         GROUP BY sii.item_code, si.customer_group, month
# #     """, (start_date, end_date, item_codes), as_dict=True)

# #     sales_data = defaultdict(lambda: defaultdict(lambda: {"sales": 0, "qty": 0}))
# #     meta_data = {}
# #     channel_totals = defaultdict(lambda: defaultdict(lambda: {"sales": 0, "qty": 0}))

# #     for r in sales_results:
# #         # Map child item to parent if exists
# #         parent_item_code = item_group_map.get(r.item_code, r.item_code)
# #         channel = get_channel(r.customer_group)
# #         key = (channel, parent_item_code)

# #         sales_data[key][r.month]["sales"] += r.total_sales or 0
# #         sales_data[key][r.month]["qty"] += r.total_qty or 0

# #         # Aggregate channel-wise totals
# #         channel_totals[channel][r.month]["sales"] += r.total_sales or 0
# #         channel_totals[channel][r.month]["qty"] += r.total_qty or 0

# #         if key not in meta_data:
# #             # Get parent item name from DB or fallback
# #             if parent_item_code == r.item_code:
# #                 item_name = r.item_name
# #             else:
# #                 item_name = frappe.db.get_value("Item", parent_item_code, "item_name") or r.item_name

# #             meta_data[key] = {
# #                 "item_name": item_name,
# #                 "channel": channel,
# #                 "item_code": parent_item_code
# #             }

# #     def get_gl_monthly(account):
# #         gl_rows = frappe.db.sql("""
# #             SELECT MONTH(posting_date) AS month, SUM(debit - credit) AS amount
# #             FROM `tabGL Entry`
# #             WHERE account = %s AND posting_date BETWEEN %s AND %s
# #             GROUP BY month
# #         """, (account, start_date, end_date), as_dict=True)
# #         return {row.month: row.amount or 0 for row in gl_rows}

# #     monthly_deductions = {code: get_gl_monthly(account) for code, account in deduction_accounts.items()}
# #     months_list = list(months)
# #     total_deduct_monthly = {m: sum(monthly_deductions[code].get(m, 0) for code in deduction_accounts) for m in months}

# #     # Calculate channel-wise total deductions
# #     rebate_by_channel = get_monthly_rebate_by_channel(start_date, end_date)
# #     discount_by_channel = get_monthly_discount_by_channel(start_date, end_date)
# #     credit_note_deductions = get_credit_note_deductions_by_channel(start_date, end_date)

# #     total_deductions_by_channel = defaultdict(lambda: defaultdict(float))
# #     for channel, monthly_data in rebate_by_channel.items():
# #         for m, v in monthly_data.items():
# #             total_deductions_by_channel[channel][m] += v
# #     for channel, monthly_data in discount_by_channel.items():
# #         for m, v in monthly_data.items():
# #             total_deductions_by_channel[channel][m] += v
# #     for channel, deduction_types in credit_note_deductions.items():
# #         for monthly_data in deduction_types.values():
# #             for m, v in monthly_data.items():
# #                 total_deductions_by_channel[channel][m] += v

# #     # Calculate channel-wise discount rate (Total Deductions / Sales Qty)
# #     channel_discount_rate = defaultdict(lambda: defaultdict(float))
# #     for channel in channel_totals:
# #         for m in months:
# #             total_qty = channel_totals[channel][m]["qty"]
# #             total_deductions = total_deductions_by_channel[channel][m]
# #             channel_discount_rate[channel][m] = (total_deductions / total_qty) if total_qty else 0

# #     # Overall discount rate for net rate calculations (unchanged)
# #     discount_rate_per_month = {}
# #     for m in months:
# #         total_qty_month = sum(channel_totals[channel][m]["qty"] for channel in channel_totals)
# #         discount_rate_per_month[m] = (total_deduct_monthly.get(m, 0) / total_qty_month) if total_qty_month else 0

# #     data = []
# #     totals_sales = defaultdict(float)
# #     totals_qty = defaultdict(float)

# #     # Sales Data Rows grouped by Channel and Item
# #     for key in sales_data:
# #         channel, item_code = key
# #         meta = meta_data.get(key, {})
# #         row = {
# #             "channel": channel,
# #             "item_code": item_code,
# #             "item_name": meta.get("item_name", "")
# #         }
# #         total_sales_sum = 0
# #         total_qty_sum = 0

# #         for m in months:
# #             m_abbr = calendar.month_abbr[m].lower()
# #             sales = sales_data[key][m]["sales"]
# #             qty = sales_data[key][m]["qty"]
# #             rate = (sales / qty) if qty else 0

# #             totals_sales[m] += sales
# #             totals_qty[m] += qty

# #             discount_rate = discount_rate_per_month.get(m, 0)
# #             net_rate = rate - discount_rate
# #             channel_disc = total_deductions_by_channel[channel].get(m, 0)
# #             channel_disc_rate = channel_discount_rate[channel].get(m, 0)

# #             row[f"{m_abbr}_sales"] = round(sales, 2)
# #             row[f"{m_abbr}_qty"] = round(qty, 2)
# #             row[f"{m_abbr}_rate"] = round(rate, 2)
# #             row[f"{m_abbr}_discount_rate"] = round(discount_rate, 4)
# #             row[f"{m_abbr}_net_rate"] = round(net_rate, 4)
# #             row[f"{m_abbr}_channel_discount"] = round(channel_disc, 2)
# #             row[f"{m_abbr}_channel_discount_rate"] = round(channel_disc_rate, 4)

# #             total_sales_sum += sales
# #             total_qty_sum += qty

# #         total_rate = (total_sales_sum / total_qty_sum) if total_qty_sum else 0
# #         total_discount = sum(discount_rate_per_month.get(m, 0) for m in months) / 12
# #         total_net_rate = total_rate - total_discount

# #         row["total_sales"] = round(total_sales_sum, 2)
# #         row["total_qty"] = round(total_qty_sum, 2)
# #         row["total_rate"] = round(total_rate, 2)
# #         row["total_net_rate"] = round(total_net_rate, 4)
# #         data.append(row)

# #     # Channel-wise total rows
# #     for channel in channel_totals:
# #         row = {
# #             "channel": channel,
# #             "item_code": "",
# #             "item_name": f"Total for {channel}",
# #         }
# #         total_sales_sum = 0
# #         total_qty_sum = 0

# #         for m in months:
# #             m_abbr = calendar.month_abbr[m].lower()
# #             sales = channel_totals[channel][m]["sales"]
# #             qty = channel_totals[channel][m]["qty"]
# #             rate = (sales / qty) if qty else 0
# #             discount_rate = discount_rate_per_month.get(m, 0)
# #             net_rate = rate - discount_rate
# #             channel_disc = total_deductions_by_channel[channel].get(m, 0)
# #             channel_disc_rate = channel_discount_rate[channel].get(m, 0)

# #             row[f"{m_abbr}_sales"] = round(sales, 2)
# #             row[f"{m_abbr}_qty"] = round(qty, 2)
# #             row[f"{m_abbr}_rate"] = round(rate, 2)
# #             row[f"{m_abbr}_discount_rate"] = round(discount_rate, 4)
# #             row[f"{m_abbr}_net_rate"] = round(net_rate, 4)
# #             row[f"{m_abbr}_channel_discount"] = round(channel_disc, 2)
# #             row[f"{m_abbr}_channel_discount_rate"] = round(channel_disc_rate, 4)

# #             total_sales_sum += sales
# #             total_qty_sum += qty

# #         total_rate = (total_sales_sum / total_qty_sum) if total_qty_sum else 0
# #         total_net_rate = total_rate - (sum(discount_rate_per_month.get(m, 0) for m in months) / 12)

# #         row["total_sales"] = round(total_sales_sum, 2)
# #         row["total_qty"] = round(total_qty_sum, 2)
# #         row["total_rate"] = round(total_rate, 2)
# #         row["total_net_rate"] = round(total_net_rate, 4)
# #         data.append(row)

# #     # Total row for all sales grouped by channel
# #     total_row = {
# #         "channel": "TOTAL",
# #         "item_code": "",
# #         "item_name": "Total of All Items",
# #     }
# #     total_sales_sum_all = 0
# #     total_qty_sum_all = 0
# #     for m in months:
# #         m_abbr = calendar.month_abbr[m].lower()
# #         sales = totals_sales[m]
# #         qty = totals_qty[m]
# #         rate = (sales / qty) if qty else 0
# #         discount_rate = discount_rate_per_month.get(m, 0)
# #         net_rate = rate - discount_rate
# #         channel_disc = sum(total_deductions_by_channel[ch].get(m, 0) for ch in channel_totals)
# #         channel_disc_rate = sum(channel_discount_rate[ch].get(m, 0) for ch in channel_totals) / len(channel_totals) if channel_totals else 0

# #         total_row[f"{m_abbr}_sales"] = round(sales, 2)
# #         total_row[f"{m_abbr}_qty"] = round(qty, 2)
# #         total_row[f"{m_abbr}_rate"] = round(rate, 2)
# #         total_row[f"{m_abbr}_discount_rate"] = round(discount_rate, 4)
# #         total_row[f"{m_abbr}_net_rate"] = round(net_rate, 4)
# #         total_row[f"{m_abbr}_channel_discount"] = round(channel_disc, 2)
# #         total_row[f"{m_abbr}_channel_discount_rate"] = round(channel_disc_rate, 4)

# #         total_sales_sum_all += sales
# #         total_qty_sum_all += qty

# #     total_rate_all = (total_sales_sum_all / total_qty_sum_all) if total_qty_sum_all else 0
# #     total_net_rate_all = total_rate_all - (sum(discount_rate_per_month.get(m, 0) for m in months) / 12)
# #     total_row["total_sales"] = round(total_sales_sum_all, 2)
# #     total_row["total_qty"] = round(total_qty_sum_all, 2)
# #     total_row["total_rate"] = round(total_rate_all, 2)
# #     total_row["total_net_rate"] = round(total_net_rate_all, 4)

# #     data.append(total_row)

# #     return data

# def get_data(year):
#     start_date = f"{year}-01-01"
#     end_date = f"{year}-12-31"

#     # All relevant item codes
#     item_codes = (
#         '6287016760027', '6287016760041', '6287016760034',
#         '6287016760058', '6287016760119', '6287016760157', '6287016760164'
#     )

#     # Define item grouping mapping (child item_code -> parent item_code)
#     # item_group_map = {
#     #     '6287016760119': '6287016760027',
#     #     '6287016760157': '6287016760027',
#     #     '6287016760058': '6287016760041',
#     #     '6287016760164': '6287016760041',
#     # }

#     deduction_accounts = {
#         "Rebate": "41010105 - Sales Rebate/Trade Discount -حسم المبيعات /الخصم التجاري - ABNA",
#         "Registerion": "516101 - Registerion Fees -رسوم التسجيل - ABNA",
#         "Listing": "516102 - Listing Fees -رسوم أدخال اصناف - ABNA",
#         "Flyer": "516107 - Flyer Fees -رسوم فلاير - ABNA",
#         "Discount": "41010103 - Discount Allowance -الخصم المسموح به - ABNA"
#     }

#     months = range(1, 13)

#     sales_results = frappe.db.sql("""
#         SELECT
#             sii.item_code,
#             sii.item_name,
#             si.customer_group,
#             MONTH(si.posting_date) AS month,
#             SUM(sii.qty) AS total_qty,
#             SUM(sii.base_net_amount) AS total_sales
#         FROM `tabSales Invoice` si
#         JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
#         WHERE
#             si.docstatus = 1
#             AND si.posting_date BETWEEN %s AND %s
#             AND sii.item_code IN %s
#         GROUP BY sii.item_code, si.customer_group, month
#     """, (start_date, end_date, item_codes), as_dict=True)

#     sales_data = defaultdict(lambda: defaultdict(lambda: {"sales": 0, "qty": 0}))
#     meta_data = {}
#     channel_totals = defaultdict(lambda: defaultdict(lambda: {"sales": 0, "qty": 0}))

#     for r in sales_results:
#         # parent_item_code = item_group_map.get(r.item_code, r.item_code)
#         parent_item_code = r.item_code
#         channel = get_channel(r.customer_group)
#         key = (channel, parent_item_code)

#         sales_data[key][r.month]["sales"] += r.total_sales or 0
#         sales_data[key][r.month]["qty"] += r.total_qty or 0

#         channel_totals[channel][r.month]["sales"] += r.total_sales or 0
#         channel_totals[channel][r.month]["qty"] += r.total_qty or 0

#         if key not in meta_data:
#             if parent_item_code == r.item_code:
#                 item_name = r.item_name
#             else:
#                 item_name = frappe.db.get_value("Item", parent_item_code, "item_name") or r.item_name

#             meta_data[key] = {
#                 "item_name": item_name,
#                 "channel": channel,
#                 "item_code": parent_item_code
#             }

#     def get_gl_monthly(account):
#         gl_rows = frappe.db.sql("""
#             SELECT MONTH(posting_date) AS month, SUM(debit - credit) AS amount
#             FROM `tabGL Entry`
#             WHERE account = %s AND posting_date BETWEEN %s AND %s
#             GROUP BY month
#         """, (account, start_date, end_date), as_dict=True)
#         return {row.month: row.amount or 0 for row in gl_rows}

#     monthly_deductions = {code: get_gl_monthly(account) for code, account in deduction_accounts.items()}
#     months_list = list(months)
#     total_deduct_monthly = {m: sum(monthly_deductions[code].get(m, 0) for code in deduction_accounts) for m in months}

#     rebate_by_channel = get_monthly_rebate_by_channel(start_date, end_date)
#     discount_by_channel = get_monthly_discount_by_channel(start_date, end_date)
#     credit_note_deductions = get_credit_note_deductions_by_channel(start_date, end_date)

#     total_deductions_by_channel = defaultdict(lambda: defaultdict(float))
#     for channel, monthly_data in rebate_by_channel.items():
#         for m, v in monthly_data.items():
#             total_deductions_by_channel[channel][m] += v
#     for channel, monthly_data in discount_by_channel.items():
#         for m, v in monthly_data.items():
#             total_deductions_by_channel[channel][m] += v
#     for channel, deduction_types in credit_note_deductions.items():
#         for monthly_data in deduction_types.values():
#             for m, v in monthly_data.items():
#                 total_deductions_by_channel[channel][m] += v

#     channel_discount_rate = defaultdict(lambda: defaultdict(float))
#     # for channel in channel_totals:
#     #     for m in months:
#     #         total_qty = channel_totals[channel][m]["qty"]
#     #         total_deductions = total_deductions_by_channel[channel][m]
#     #         channel_discount_rate[channel][m] = (total_deductions / total_qty) if total_qty else 0

#     for channel in channel_totals:
#       for m in months:
#          total_sales = channel_totals[channel][m]["sales"]
#          total_deductions = total_deductions_by_channel[channel][m]
#          channel_discount_rate[channel][m] = (total_deductions / total_sales * 100) if total_sales else 0


#     discount_rate_per_month = {}
#     for m in months:
#         total_qty_month = sum(channel_totals[channel][m]["qty"] for channel in channel_totals)
#         discount_rate_per_month[m] = (total_deduct_monthly.get(m, 0) / total_qty_month) if total_qty_month else 0

#     data = []
#     totals_sales = defaultdict(float)
#     totals_qty = defaultdict(float)

#     # Sales Data Rows grouped by Channel and Item
#     for key in sales_data:
#         channel, item_code = key
#         meta = meta_data.get(key, {})
#         row = {
#             "channel": channel,
#             "item_code": item_code,
#             "item_name": meta.get("item_name", "")
#         }
#         total_sales_sum = 0
#         total_qty_sum = 0

#         for m in months:
#             m_abbr = calendar.month_abbr[m].lower()
#             sales = sales_data[key][m]["sales"]
#             qty = sales_data[key][m]["qty"]
#             rate = (sales / qty) if qty else 0

#             totals_sales[m] += sales
#             totals_qty[m] += qty

#             discount_rate = discount_rate_per_month.get(m, 0)
#             # Updated calculation: net_rate = rate - channel_discount_rate
#             # net_rate = rate - channel_discount_rate[channel].get(m, 0)
#             sc_percent = channel_discount_rate[channel].get(m, 0)
#             net_rate = rate * (100 - disc_percent) / 100
#             channel_disc = total_deductions_by_channel[channel].get(m, 0)
#             channel_disc_rate = channel_discount_rate[channel].get(m, 0)

#             row[f"{m_abbr}_sales"] = round(sales, 2)
#             row[f"{m_abbr}_qty"] = round(qty, 2)
#             row[f"{m_abbr}_rate"] = round(rate, 2)
#             row[f"{m_abbr}_discount_rate"] = round(discount_rate, 4)
#             row[f"{m_abbr}_net_rate"] = round(net_rate, 4)
#             row[f"{m_abbr}_channel_discount"] = round(channel_disc, 2)
#             row[f"{m_abbr}_channel_discount_rate"] = round(channel_disc_rate, 4)

#             total_sales_sum += sales
#             total_qty_sum += qty

#         total_rate = (total_sales_sum / total_qty_sum) if total_qty_sum else 0
#         total_discount = sum(discount_rate_per_month.get(m, 0) for m in months) / 12
#         # Updated calculation: total_net_rate = total_rate - average channel_discount_rate
#         total_channel_disc_rate = sum(channel_discount_rate[channel].get(m, 0) for m in months) / 12
#         total_net_rate = total_rate - total_channel_disc_rate

#         row["total_sales"] = round(total_sales_sum, 2)
#         row["total_qty"] = round(total_qty_sum, 2)
#         row["total_rate"] = round(total_rate, 2)
#         row["total_net_rate"] = round(total_net_rate, 4)
#         data.append(row)

#     # Channel-wise total rows
#     for channel in channel_totals:
#         row = {
#             "channel": channel,
#             "item_code": "",
#             "item_name": f"Total for {channel}",
#         }
#         total_sales_sum = 0
#         total_qty_sum = 0

#         for m in months:
#             m_abbr = calendar.month_abbr[m].lower()
#             sales = channel_totals[channel][m]["sales"]
#             qty = channel_totals[channel][m]["qty"]
#             rate = (sales / qty) if qty else 0
#             discount_rate = discount_rate_per_month.get(m, 0)
#             # Updated calculation: net_rate = rate - channel_discount_rate
#             # net_rate = rate - channel_discount_rate[channel].get(m, 0)
#             disc_percent = channel_discount_rate.get(channel, {}).get(m, 0)
#             net_rate = rate * (100 - disc_percent) / 100
#             channel_disc = total_deductions_by_channel[channel].get(m, 0)
#             channel_disc_rate = channel_discount_rate[channel].get(m, 0)

#             row[f"{m_abbr}_sales"] = round(sales, 2)
#             row[f"{m_abbr}_qty"] = round(qty, 2)
#             row[f"{m_abbr}_rate"] = round(rate, 2)
#             row[f"{m_abbr}_discount_rate"] = round(discount_rate, 4)
#             row[f"{m_abbr}_net_rate"] = round(net_rate, 4)
#             row[f"{m_abbr}_channel_discount"] = round(channel_disc, 2)
#             row[f"{m_abbr}_channel_discount_rate"] = round(channel_disc_rate, 4)

#             total_sales_sum += sales
#             total_qty_sum += qty

#         total_rate = (total_sales_sum / total_qty_sum) if total_qty_sum else 0
#         # Updated calculation: total_net_rate = total_rate - average channel_discount_rate
#         total_channel_disc_rate = sum(channel_discount_rate[channel].get(m, 0) for m in months) / 12
#         total_net_rate = total_rate - total_channel_disc_rate

#         row["total_sales"] = round(total_sales_sum, 2)
#         row["total_qty"] = round(total_qty_sum, 2)
#         row["total_rate"] = round(total_rate, 2)
#         row["total_net_rate"] = round(total_net_rate, 4)
#         data.append(row)

#     # Total row for all sales grouped by channel
#     total_row = {
#         "channel": "TOTAL",
#         "item_code": "",
#         "item_name": "Total of All Items",
#     }
#     total_sales_sum_all = 0
#     total_qty_sum_all = 0
#     for m in months:
#         m_abbr = calendar.month_abbr[m].lower()
#         sales = totals_sales[m]
#         qty = totals_qty[m]
#         rate = (sales / qty) if qty else 0
#         discount_rate = discount_rate_per_month.get(m, 0)
#         # Updated calculation: net_rate = rate - average channel_discount_rate across all channels
#         avg_channel_disc_rate = sum(channel_discount_rate[ch].get(m, 0) for ch in channel_totals) / len(channel_totals) if channel_totals else 0
#         # net_rate = rate - avg_channel_disc_rate
#         net_rate = rate * (100 - avg_channel_disc_rate) / 100
#         channel_disc = sum(total_deductions_by_channel[ch].get(m, 0) for ch in channel_totals)
#         channel_disc_rate = avg_channel_disc_rate

#         total_row[f"{m_abbr}_sales"] = round(sales, 2)
#         total_row[f"{m_abbr}_qty"] = round(qty, 2)
#         total_row[f"{m_abbr}_rate"] = round(rate, 2)
#         total_row[f"{m_abbr}_discount_rate"] = round(discount_rate, 4)
#         total_row[f"{m_abbr}_net_rate"] = round(net_rate, 4)
#         total_row[f"{m_abbr}_channel_discount"] = round(channel_disc, 2)
#         total_row[f"{m_abbr}_channel_discount_rate"] = round(channel_disc_rate, 4)

#         total_sales_sum_all += sales
#         total_qty_sum_all += qty

#     total_rate_all = (total_sales_sum_all / total_qty_sum_all) if total_qty_sum_all else 0
#     # Updated calculation: total_net_rate = total_rate - average channel_discount_rate
#     total_avg_channel_disc_rate = sum(sum(channel_discount_rate[ch].get(m, 0) for m in months) / 12 for ch in channel_totals) / len(channel_totals) if channel_totals else 0
#     # total_net_rate_all = total_rate_all - total_avg_channel_disc_rate
#     total_net_rate_all = total_rate_all * (100 - total_avg_channel_disc_rate) / 100
#     total_row["total_sales"] = round(total_sales_sum_all, 2)
#     total_row["total_qty"] = round(total_qty_sum_all, 2)
#     total_row["total_rate"] = round(total_rate_all, 2)
#     total_row["total_net_rate"] = round(total_net_rate_all, 4)

#     data.append(total_row)

#     return data


import frappe
from collections import defaultdict
import calendar

CHANNEL_MAPPING = {
    "DIRECT DISTRIBUTION DD": [
        "EATRIES", "LARGE GROCERY", "MINIMARKET", "SMALL GROCERY",
        "SUPERMARKET B", "WATER SHOP", "DIRECT DISTRIBUTION DD"
    ],
    "DISTRIBUTOR": [
        "DISTRIBUTOR A", "DISTRIBUTOR B", "DISTRIBUTOR C", "DISTRIBUTOR"
    ],
    "HOME DELIVERY HD": [
        "HOUSE", "MOSQUE", "OFFICE", "SCHOOL", "HOME DELIVERY HD"
    ],
    "HORECA HO": [
        "CAFÉ", "CARE", "CATERING", "COMMERCIAL", "GOVERNMENTAL",
        "HOTEL", "INSTITUTIONAL", "RESTAURANT", "HORECA HO", "CAFE"
    ],
    "KEY ACCOUNT KA": [
        "E-COMMERCE", "HYPERMARKET", "SUPERMARKET-A", "SUPERMARKET-B", "KEY ACCOUNT  KA"
    ],
    "MARKETING": [
        "MARKETING", "DONATION", "EVENT", "SPONSORSHIP"
    ],
    "OTHER MISCELLANEOUS": [
        "OTHER MISCELLANEOUS", "OTHER  MISCELLANEOUS"
    ],
    "WHOLESALE": [
        "WHOLESALE WS", "WAREHOUSE", "WHOLESALE A", "WHOLESALE-B", "WHOLESALE-C"
    ]
}

def get_channel(customer_group):
    if not customer_group:
        return ""
    customer_group_upper = customer_group.strip().upper()
    for channel, groups in CHANNEL_MAPPING.items():
        if customer_group_upper in (g.upper() for g in groups):
            return channel
    return ""

def execute(filters=None):
    filters = filters or {}
    year = filters.get("year")
    if not year:
        frappe.throw("Please select a year")

    columns = get_columns(year)
    data = get_data(year)
    return columns, data

def get_columns(year):
    months = [calendar.month_abbr[m] for m in range(1, 13)]
    columns = [
        {"label": "Channel", "fieldname": "channel", "fieldtype": "Data", "width": 150},
        {"label": "Item Code", "fieldname": "item_code", "fieldtype": "Data", "width": 140},
        {"label": "Item Name", "fieldname": "item_name", "fieldtype": "Data", "width": 250},
    ]

    for m in months:
        m_lower = m.lower()
        columns.append({"label": f"{m} Sales", "fieldname": f"{m_lower}_sales", "fieldtype": "Currency", "width": 100})
        columns.append({"label": f"{m} Qty", "fieldname": f"{m_lower}_qty", "fieldtype": "Float", "width": 80})
        columns.append({"label": f"{m} Rate", "fieldname": f"{m_lower}_rate", "fieldtype": "Currency", "width": 80})
        columns.append({"label": f"{m} Net Rate (After %)", "fieldname": f"{m_lower}_net_rate", "fieldtype": "Float", "width": 130})
        columns.append({"label": f"{m} Channel Discount", "fieldname": f"{m_lower}_channel_discount", "fieldtype": "Currency", "width": 120})
        columns.append({"label": f"{m} Channel Discount Rate (%)", "fieldname": f"{m_lower}_channel_discount_rate", "fieldtype": "Percent", "width": 130})

    columns += [
        {"label": "Total Sales", "fieldname": "total_sales", "fieldtype": "Currency", "width": 110},
        {"label": "Total Qty", "fieldname": "total_qty", "fieldtype": "Float", "width": 90},
        {"label": "Total Rate", "fieldname": "total_rate", "fieldtype": "Currency", "width": 90},
        {"label": "Total Net Rate", "fieldname": "total_net_rate", "fieldtype": "Currency", "width": 110},
    ]
    return columns

def get_monthly_rebate_by_channel(start_date, end_date):
    results = frappe.db.sql("""
        SELECT
            cu.customer_group,
            MONTH(r.posting_date) AS month,
            SUM(r.rebate_received_amount) AS rebate_amount
        FROM `tabRebate` r
        JOIN `tabCustomer` cu ON cu.name = r.party
        WHERE
            r.docstatus = 1
            AND r.party_type = 'Customer'
            AND r.posting_date BETWEEN %s AND %s
        GROUP BY cu.customer_group, MONTH(r.posting_date)
    """, (start_date, end_date), as_dict=True)

    rebate_data = defaultdict(lambda: defaultdict(float))
    for row in results:
        channel = get_channel(row.customer_group)
        rebate_data[channel][row.month] += row.rebate_amount or 0

    return rebate_data

def get_monthly_discount_by_channel(start_date, end_date):
    results = frappe.db.sql("""
        SELECT
            cu.customer_group,
            MONTH(cp.posting_date) AS month,
            SUM(cp.promtion_amount) AS discount_amount
        FROM `tabCustomer Promotion` cp
        JOIN `tabCustomer` cu ON cu.name = cp.customer
        WHERE
            cp.docstatus = 1
            AND cp.posting_date BETWEEN %s AND %s
        GROUP BY cu.customer_group, MONTH(cp.posting_date)
    """, (start_date, end_date), as_dict=True)

    discount_data = defaultdict(lambda: defaultdict(float))
    for row in results:
        channel = get_channel(row.customer_group)
        discount_data[channel][row.month] += row.discount_amount or 0

    return discount_data

def get_credit_note_deductions_by_channel(start_date, end_date):
    deduction_accounts = {
        "Flyer": "516107 - Flyer Fees -رسوم فلاير - ABNA",
        "Listing": "516102 - Listing Fees -رسوم أدخال اصناف - ABNA",
        "Registerion": "516101 - Registerion Fees -رسوم التسجيل - ABNA"
    }

    accounts_list = list(deduction_accounts.values())
    placeholders = ', '.join(['%s'] * len(accounts_list))

    query = """
        SELECT
            cu.customer_group,
            MONTH(cn.posting_date) AS month,
            cni.account,
            SUM(cni.debit - cni.credit) AS amount
        FROM `tabCredit Note` cn
        JOIN `tabJournal Entry Account` cni ON cni.parent = cn.name
        JOIN `tabCustomer` cu ON cu.name = cn.customer
        WHERE
            cn.docstatus = 1
            AND cn.posting_date BETWEEN %s AND %s
            AND cni.account IN ({})
        GROUP BY cu.customer_group, cni.account, MONTH(cn.posting_date)
    """.format(placeholders)

    params = [start_date, end_date] + accounts_list

    results = frappe.db.sql(query, params, as_dict=True)

    data = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))
    account_to_type = {v: k for k, v in deduction_accounts.items()}

    for row in results:
        channel = get_channel(row.customer_group)
        deduction_type = account_to_type.get(row.account, "Unknown")
        data[channel][deduction_type][row.month] += row.amount or 0

    return data

def get_data(year):
    start_date = f"{year}-01-01"
    end_date = f"{year}-12-31"

    # All relevant item codes
    item_codes = (
        '6287016760027', '6287016760041', '6287016760034',
        '6287016760058', '6287016760119', '6287016760157', '6287016760164'
    )

    deduction_accounts = {
        "Rebate": "41010105 - Sales Rebate/Trade Discount -حسم المبيعات /الخصم التجاري - ABNA",
        "Registerion": "516101 - Registerion Fees -رسوم التسجيل - ABNA",
        "Listing": "516102 - Listing Fees -رسوم أدخال اصناف - ABNA",
        "Flyer": "516107 - Flyer Fees -رسوم فلاير - ABNA",
        "Discount": "41010103 - Discount Allowance -الخصم المسموح به - ABNA"
    }

    months = range(1, 13)

    sales_results = frappe.db.sql("""
        SELECT
            sii.item_code,
            sii.item_name,
            si.customer_group,
            MONTH(si.posting_date) AS month,
            SUM(sii.qty) AS total_qty,
            SUM(sii.base_net_amount) AS total_sales
        FROM `tabSales Invoice` si
        JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
        WHERE
            si.docstatus = 1
            AND si.posting_date BETWEEN %s AND %s
            AND sii.item_code IN %s
        GROUP BY sii.item_code, si.customer_group, MONTH(si.posting_date)
    """, (start_date, end_date, item_codes), as_dict=True)

    sales_data = defaultdict(lambda: defaultdict(lambda: {"sales": 0, "qty": 0}))
    meta_data = {}
    channel_totals = defaultdict(lambda: defaultdict(lambda: {"sales": 0, "qty": 0}))

    for r in sales_results:
        parent_item_code = r.item_code
        channel = get_channel(r.customer_group)
        key = (channel, parent_item_code)

        sales_data[key][r.month]["sales"] += r.total_sales or 0
        sales_data[key][r.month]["qty"] += r.total_qty or 0

        channel_totals[channel][r.month]["sales"] += r.total_sales or 0
        channel_totals[channel][r.month]["qty"] += r.total_qty or 0

        if key not in meta_data:
            if parent_item_code == r.item_code:
                item_name = r.item_name
            else:
                item_name = frappe.db.get_value("Item", parent_item_code, "item_name") or r.item_name

            meta_data[key] = {
                "item_name": item_name,
                "channel": channel,
                "item_code": parent_item_code
            }

    def get_gl_monthly(account):
        gl_rows = frappe.db.sql("""
            SELECT MONTH(posting_date) AS month, SUM(debit - credit) AS amount
            FROM `tabGL Entry`
            WHERE account = %s AND posting_date BETWEEN %s AND %s
            GROUP BY MONTH(posting_date)
        """, (account, start_date, end_date), as_dict=True)
        return {row.month: row.amount or 0 for row in gl_rows}

    monthly_deductions = {code: get_gl_monthly(account) for code, account in deduction_accounts.items()}
    months_list = list(months)
    total_deduct_monthly = {m: sum(monthly_deductions[code].get(m, 0) for code in deduction_accounts) for m in months}

    rebate_by_channel = get_monthly_rebate_by_channel(start_date, end_date)
    discount_by_channel = get_monthly_discount_by_channel(start_date, end_date)
    credit_note_deductions = get_credit_note_deductions_by_channel(start_date, end_date)

    total_deductions_by_channel = defaultdict(lambda: defaultdict(float))
    for channel, monthly_data in rebate_by_channel.items():
        for m, v in monthly_data.items():
            total_deductions_by_channel[channel][m] += v
    for channel, monthly_data in discount_by_channel.items():
        for m, v in monthly_data.items():
            total_deductions_by_channel[channel][m] += v
    for channel, deduction_types in credit_note_deductions.items():
        for monthly_data in deduction_types.values():
            for m, v in monthly_data.items():
                total_deductions_by_channel[channel][m] += v

    channel_discount_rate = defaultdict(lambda: defaultdict(float))
    for channel in channel_totals:
        for m in months:
            total_sales = channel_totals[channel][m]["sales"]
            total_deductions = total_deductions_by_channel[channel][m]
            channel_discount_rate[channel][m] = (total_deductions / total_sales * 100) if total_sales else 0

    discount_rate_per_month = {}
    for m in months:
        total_qty_month = sum(channel_totals[channel][m]["qty"] for channel in channel_totals)
        discount_rate_per_month[m] = (total_deduct_monthly.get(m, 0) / total_qty_month) if total_qty_month else 0

    data = []
    totals_sales = defaultdict(float)
    totals_qty = defaultdict(float)

    # Sales Data Rows grouped by Channel and Item
    for key in sales_data:
        channel, item_code = key
        meta = meta_data.get(key, {})
        row = {
            "channel": channel,
            "item_code": item_code,
            "item_name": meta.get("item_name", "")
        }
        total_sales_sum = 0
        total_qty_sum = 0

        for m in months:
            m_abbr = calendar.month_abbr[m].lower()
            sales = sales_data[key][m]["sales"]
            qty = sales_data[key][m]["qty"]
            rate = (sales / qty) if qty else 0

            totals_sales[m] += sales
            totals_qty[m] += qty

            discount_rate = discount_rate_per_month.get(m, 0)
            net_rate = rate * (100 - channel_discount_rate[channel].get(m, 0)) / 100
            channel_disc = total_deductions_by_channel[channel].get(m, 0)
            channel_disc_rate = channel_discount_rate[channel].get(m, 0)

            row[f"{m_abbr}_sales"] = round(sales, 2)
            row[f"{m_abbr}_qty"] = round(qty, 2)
            row[f"{m_abbr}_rate"] = round(rate, 2)
            row[f"{m_abbr}_discount_rate"] = round(discount_rate, 4)
            row[f"{m_abbr}_net_rate"] = round(net_rate, 4)
            row[f"{m_abbr}_channel_discount"] = round(channel_disc, 2)
            row[f"{m_abbr}_channel_discount_rate"] = round(channel_disc_rate, 4)

            total_sales_sum += sales
            total_qty_sum += qty

        total_rate = (total_sales_sum / total_qty_sum) if total_qty_sum else 0
        total_channel_disc_rate = sum(channel_discount_rate[channel].get(m, 0) for m in months) / 12
        total_net_rate = total_rate * (100 - total_channel_disc_rate) / 100

        row["total_sales"] = round(total_sales_sum, 2)
        row["total_qty"] = round(total_qty_sum, 2)
        row["total_rate"] = round(total_rate, 2)
        row["total_net_rate"] = round(total_net_rate, 4)
        data.append(row)

    # Channel-wise total rows
    for channel in channel_totals:
        row = {
            "channel": channel,
            "item_code": "",
            "item_name": f"Total for {channel}",
        }
        total_sales_sum = 0
        total_qty_sum = 0

        for m in months:
            m_abbr = calendar.month_abbr[m].lower()
            sales = channel_totals[channel][m]["sales"]
            qty = channel_totals[channel][m]["qty"]
            rate = (sales / qty) if qty else 0
            discount_rate = discount_rate_per_month.get(m, 0)
            net_rate = rate * (100 - channel_discount_rate[channel].get(m, 0)) / 100
            channel_disc = total_deductions_by_channel[channel].get(m, 0)
            channel_disc_rate = channel_discount_rate[channel].get(m, 0)

            row[f"{m_abbr}_sales"] = round(sales, 2)
            row[f"{m_abbr}_qty"] = round(qty, 2)
            row[f"{m_abbr}_rate"] = round(rate, 2)
            row[f"{m_abbr}_discount_rate"] = round(discount_rate, 4)
            row[f"{m_abbr}_net_rate"] = round(net_rate, 4)
            row[f"{m_abbr}_channel_discount"] = round(channel_disc, 2)
            row[f"{m_abbr}_channel_discount_rate"] = round(channel_disc_rate, 4)

            total_sales_sum += sales
            total_qty_sum += qty

        total_rate = (total_sales_sum / total_qty_sum) if total_qty_sum else 0
        total_channel_disc_rate = sum(channel_discount_rate[channel].get(m, 0) for m in months) / 12
        total_net_rate = total_rate * (100 - total_channel_disc_rate) / 100

        row["total_sales"] = round(total_sales_sum, 2)
        row["total_qty"] = round(total_qty_sum, 2)
        row["total_rate"] = round(total_rate, 2)
        row["total_net_rate"] = round(total_net_rate, 4)
        data.append(row)

    # Total row for all sales grouped by channel
    total_row = {
        "channel": "TOTAL",
        "item_code": "",
        "item_name": "Total of All Items",
    }
    total_sales_sum_all = 0
    total_qty_sum_all = 0
    for m in months:
        m_abbr = calendar.month_abbr[m].lower()
        sales = totals_sales[m]
        qty = totals_qty[m]
        rate = (sales / qty) if qty else 0
        discount_rate = discount_rate_per_month.get(m, 0)
        avg_channel_disc_rate = sum(channel_discount_rate[ch].get(m, 0) for ch in channel_totals) / len(channel_totals) if channel_totals else 0
        net_rate = rate * (100 - avg_channel_disc_rate) / 100
        channel_disc = sum(total_deductions_by_channel[ch].get(m, 0) for ch in channel_totals)
        channel_disc_rate = avg_channel_disc_rate

        total_row[f"{m_abbr}_sales"] = round(sales, 2)
        total_row[f"{m_abbr}_qty"] = round(qty, 2)
        total_row[f"{m_abbr}_rate"] = round(rate, 2)
        total_row[f"{m_abbr}_discount_rate"] = round(discount_rate, 4)
        total_row[f"{m_abbr}_net_rate"] = round(net_rate, 4)
        total_row[f"{m_abbr}_channel_discount"] = round(channel_disc, 2)
        total_row[f"{m_abbr}_channel_discount_rate"] = round(channel_disc_rate, 4)

        total_sales_sum_all += sales
        total_qty_sum_all += qty

    total_rate_all = (total_sales_sum_all / total_qty_sum_all) if total_qty_sum_all else 0
    total_avg_channel_disc_rate = sum(sum(channel_discount_rate[ch].get(m, 0) for m in months) / 12 for ch in channel_totals) / len(channel_totals) if channel_totals else 0
    total_net_rate_all = total_rate_all * (100 - total_avg_channel_disc_rate) / 100
    total_row["total_sales"] = round(total_sales_sum_all, 2)
    total_row["total_qty"] = round(total_qty_sum_all, 2)
    total_row["total_rate"] = round(total_rate_all, 2)
    total_row["total_net_rate"] = round(total_net_rate_all, 4)

    data.append(total_row)

    return data