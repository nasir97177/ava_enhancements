# Copyright (c) 2025, Furqan Asghar and contributors
# For license information, please see license.txt

# import frappe
# from frappe import _
# from frappe.utils import flt

# from erpnext.accounts.report.financial_statements import (
# 	get_columns,
# 	get_data,
# 	get_filtered_list_for_consolidated_report,
# 	get_period_list,
# )


# def execute(filters=None):
# 	period_list = get_period_list(
# 		filters.from_fiscal_year,
# 		filters.to_fiscal_year,
# 		filters.period_start_date,
# 		filters.period_end_date,
# 		filters.filter_based_on,
# 		filters.periodicity,
# 		company=filters.company,
# 	)

# 	income = get_data(
# 		filters.company,
# 		"",
# 		"Credit",
# 		period_list,
# 		filters=filters,
# 		accumulated_values=filters.accumulated_values,
# 		ignore_closing_entries=True,
# 		ignore_accumulated_values_for_fy=True,
# 	)

# 	expense = get_data(
# 		filters.company,
# 		"Expense",
# 		"Debit",
# 		period_list,
# 		filters=filters,
# 		accumulated_values=filters.accumulated_values,
# 		ignore_closing_entries=True,
# 		ignore_accumulated_values_for_fy=True,
# 	)

# 	net_profit_loss = get_net_profit_loss(
# 		income, expense, period_list, filters.company, filters.presentation_currency
# 	)

# 	data = []
# 	data.extend(income or [])
# 	data.extend(expense or [])
# 	if net_profit_loss:
# 		data.append(net_profit_loss)

# 	columns = get_columns(
# 		filters.periodicity, period_list, filters.accumulated_values, filters.company
# 	)

# 	chart = get_chart_data(filters, columns, income, expense, net_profit_loss)

# 	currency = filters.presentation_currency or frappe.get_cached_value(
# 		"Company", filters.company, "default_currency"
# 	)
# 	report_summary = get_report_summary(
# 		period_list, filters.periodicity, income, expense, net_profit_loss, currency, filters
# 	)

# 	return columns, data, None, chart, report_summary


# def get_report_summary(
# 	period_list, periodicity, income, expense, net_profit_loss, currency, filters, consolidated=False
# ):
# 	net_income, net_expense, net_profit = 0.0, 0.0, 0.0

# 	# from consolidated financial statement
# 	if filters.get("accumulated_in_group_company"):
# 		period_list = get_filtered_list_for_consolidated_report(filters, period_list)

# 	for period in period_list:
# 		key = period if consolidated else period.key
# 		if income:
# 			net_income += income[-2].get(key)
# 		if expense:
# 			net_expense += expense[-2].get(key)/12
# 		if net_profit_loss:
# 			net_profit += net_profit_loss.get(key)

# 	if len(period_list) == 1 and periodicity == "Yearly":
# 		profit_label = _("Profit This Year")
# 		income_label = _("")
# 		expense_label = _("Total Expense This Year")
# 	else:
# 		profit_label = _("Net Expense")
# 		income_label = _("")
# 		expense_label = _("Total Expense")

# 	return [
# 		# {"value": net_income, "label": income_label, "datatype": "Currency", "currency": currency},
# 		# {"type": "separator", "value": "-"},
# 		{"value": net_expense, "label": expense_label, "datatype": "Currency", "currency": currency},
# 		# {"type": "separator", "value": "=", "color": "blue"},
# 		# {
# 		# 	"value": net_profit,
# 		# 	"indicator": "Green" if net_profit > 0 else "Red",
# 		# 	"label": profit_label,
# 		# 	"datatype": "Currency",
# 		# 	"currency": currency,
# 		# },
# 	]


# def get_net_profit_loss(income, expense, period_list, company, currency=None, consolidated=False):
# 	total = 0
# 	net_profit_loss = {
# 		"account_name": "'" + _("Expenses for the year") + "'",
# 		"account": "'" + _("Expenses for the year") + "'",
# 		"warn_if_negative": True,
# 		"currency": currency or frappe.get_cached_value("Company", company, "default_currency"),
# 	}

# 	has_value = False

# 	for period in period_list:
# 		key = period if consolidated else period.key
# 		total_income = flt(income[-2][key], 3) if income else 0
# 		total_expense = flt(expense[-2][key], 3) if expense else 0

# 		net_profit_loss[key] = total_income - total_expense

# 		if net_profit_loss[key]:
# 			has_value = True

# 		total += flt(net_profit_loss[key])
# 		net_profit_loss["total"] = total

# 	if has_value:
# 		return net_profit_loss


# def get_chart_data(filters, columns, income, expense, net_profit_loss):
# 	labels = [d.get("label") for d in columns[2:]]

# 	income_data, expense_data, net_profit = [], [], []

# 	for p in columns[2:]:
# 		if income:
# 			income_data.append(income[-2].get(p.get("fieldname")))
# 		if expense:
# 			expense_data.append(expense[-2].get(p.get("fieldname")))
# 		if net_profit_loss:
# 			net_profit.append(net_profit_loss.get(p.get("fieldname")))

# 	datasets = []
# 	# if income_data:
# 	# 	datasets.append({"name": _("Income"), "values": income_data})
# 	if expense_data:
# 		datasets.append({"name": _("Expense"), "values": expense_data})
# 	# if net_profit:
# 	# 	datasets.append({"name": _("Net Profit/Loss"), "values": net_profit})

# 	chart = {"data": {"labels": labels, "datasets": datasets}}

# 	if not filters.accumulated_values:
# 		chart["type"] = "bar"
# 	else:
# 		chart["type"] = "line"

# 	chart["fieldtype"] = "Currency"

# 	return chart


# import frappe
# from frappe import _
# from frappe.utils import flt

# from erpnext.accounts.report.financial_statements import (
# 	get_columns,
# 	get_data,
# 	get_filtered_list_for_consolidated_report,
# 	get_period_list,
# )


# def execute(filters=None):
# 	period_list = get_period_list(
# 		filters.from_fiscal_year,
# 		filters.to_fiscal_year,
# 		filters.period_start_date,
# 		filters.period_end_date,
# 		filters.filter_based_on,
# 		filters.periodicity,
# 		company=filters.company,
# 	)

# 	income = get_data(
# 		filters.company,
# 		"",
# 		"Credit",
# 		period_list,
# 		filters=filters,
# 		accumulated_values=filters.accumulated_values,
# 		ignore_closing_entries=True,
# 		ignore_accumulated_values_for_fy=True,
# 	)

# 	expense = get_data(
# 		filters.company,
# 		"Expense",
# 		"Debit",
# 		period_list,
# 		filters=filters,
# 		accumulated_values=filters.accumulated_values,
# 		ignore_closing_entries=True,
# 		ignore_accumulated_values_for_fy=True,
# 	)

# 	net_profit_loss = get_net_profit_loss(
# 		income, expense, period_list, filters.company, filters.presentation_currency
# 	)

# 	data = []
# 	data.extend(income or [])
# 	data.extend(expense or [])
# 	if net_profit_loss:
# 		data.append(net_profit_loss)

# 	columns = get_columns(
# 		filters.periodicity, period_list, filters.accumulated_values, filters.company
# 	)

# 	chart = get_chart_data(filters, columns, income, expense, net_profit_loss)

# 	currency = filters.presentation_currency or frappe.get_cached_value(
# 		"Company", filters.company, "default_currency"
# 	)

# 	report_summary = get_report_summary(
# 		period_list, filters.periodicity, income, expense, net_profit_loss, currency, filters
# 	)

# 	return columns, data, None, chart, report_summary


# def get_report_summary(
# 	period_list, periodicity, income, expense, net_profit_loss, currency, filters, consolidated=False
# ):
# 	net_expense = 0.0
# 	num_periods = len(period_list)

# 	# from consolidated financial statement
# 	if filters.get("accumulated_in_group_company"):
# 		period_list = get_filtered_list_for_consolidated_report(filters, period_list)
# 		num_periods = len(period_list)

# 	for period in period_list:
# 		key = period if consolidated else period.key
# 		if expense:
# 			net_expense += flt(expense[-2].get(key))

# 	# Compute average
# 	avg_expense = net_expense / num_periods if num_periods else 0

# 	if len(period_list) == 1 and periodicity == "Yearly":
# 		expense_label = _("Total Expense This Year")
# 		avg_expense_label = _("Average Monthly Expense")
# 	else:
# 		expense_label = _("Total Expense ")
# 		avg_expense_label = _("Average Expense")

# 	return [
# 		{"value": net_expense, "label": expense_label, "datatype": "Currency", "currency": currency},
# 		{"value": avg_expense, "label": avg_expense_label, "datatype": "Currency", "currency": currency},
# 	]


# def get_net_profit_loss(income, expense, period_list, company, currency=None, consolidated=False):
# 	total = 0
# 	net_profit_loss = {
# 		"account_name": "'" + _("Expenses for the year") + "'",
# 		"account": "'" + _("Expenses for the year") + "'",
# 		"warn_if_negative": True,
# 		"currency": currency or frappe.get_cached_value("Company", company, "default_currency"),
# 	}

# 	has_value = False

# 	for period in period_list:
# 		key = period if consolidated else period.key
# 		total_income = flt(income[-2][key], 3) if income else 0
# 		total_expense = flt(expense[-2][key], 3) if expense else 0

# 		net_profit_loss[key] = total_income - total_expense

# 		if net_profit_loss[key]:
# 			has_value = True

# 		total += flt(net_profit_loss[key])
# 		net_profit_loss["total"] = total

# 	if has_value:
# 		return net_profit_loss


# def get_chart_data(filters, columns, income, expense, net_profit_loss):
# 	labels = [d.get("label") for d in columns[2:]]

# 	income_data, expense_data, net_profit = [], [], []

# 	for p in columns[2:]:
# 		if income:
# 			income_data.append(income[-2].get(p.get("fieldname")))
# 		if expense:
# 			expense_data.append(expense[-2].get(p.get("fieldname")))
# 		if net_profit_loss:
# 			net_profit.append(net_profit_loss.get(p.get("fieldname")))

# 	datasets = []
# 	# Uncomment to show income and profit if desired
# 	# if income_data:
# 	# 	datasets.append({"name": _("Income"), "values": income_data})
# 	if expense_data:
# 		datasets.append({"name": _("Expense"), "values": expense_data})
# 	# if net_profit:
# 	# 	datasets.append({"name": _("Net Profit/Loss"), "values": net_profit})

# 	chart = {"data": {"labels": labels, "datasets": datasets}}

# 	chart["type"] = "bar" if not filters.accumulated_values else "line"
# 	chart["fieldtype"] = "Currency"

# 	return chart
   

import frappe
from frappe import _
from frappe.utils import flt

from erpnext.accounts.report.financial_statements import (
	get_columns,
	get_data,
	get_period_list,
)


def execute(filters=None):
	period_list = get_period_list(
		filters.from_fiscal_year,
		filters.to_fiscal_year,
		filters.period_start_date,
		filters.period_end_date,
		filters.filter_based_on,
		filters.periodicity,
		company=filters.company,
	)

	expense = get_data(
		filters.company,
		"Expense",
		"Debit",
		period_list,
		filters=filters,
		accumulated_values=filters.accumulated_values,
		ignore_closing_entries=True,
		ignore_accumulated_values_for_fy=True,
	) or []

	excluded_accounts = get_excluded_accounts(filters.company)
	expense = filter_accounts(expense, excluded_accounts)

	columns = get_columns(
		filters.periodicity,
		period_list,
		filters.accumulated_values,
		filters.company
	)

	# Add final total row summing all months per account
	if expense:
		total_row = {"account": _("Total"), "account_name": _("Total")}
		for col in columns[2:]:  # Skip 'account' and 'account_name'
			fieldname = col.get("fieldname")
			total_row[fieldname] = sum(flt(row.get(fieldname)) for row in expense)
		expense.append(total_row)

	# Determine if 'total' column exists
	fieldnames = [col.get("fieldname") for col in columns]
	has_total_column = "total" in fieldnames

	# Calculate total_expense from grand total column only (once)
	if has_total_column:
		total_expense = flt(expense[-1].get("total")) or 0.0
		# Number of months (exclude account, account_name, and total)
		num_periods = len(columns) - 3
	else:
		# Fallback: sum all month columns but avoid double counting
		num_periods = len(columns) - 2
		total_expense = 0.0
		for col in columns[2:]:
			fieldname = col.get("fieldname")
			total_expense += flt(expense[-1].get(fieldname))

	avg_expense = total_expense / num_periods if num_periods else 0.0

	chart_title = _(
		"Total Expense: {total} | Average Expense: {avg}"
	).format(
		total=frappe.utils.fmt_money(total_expense, filters.presentation_currency),
		avg=frappe.utils.fmt_money(avg_expense, filters.presentation_currency),
	)

	chart = get_chart_data(columns, expense, chart_title)

	return columns, expense, None, chart


def get_excluded_accounts(company):
	excluded_account_names = set([
		"533102 - Packaging Material Consumption -استهلاك مواد التغليف - ABNA",
		"533101 - Raw Material Consumption -استهلاك المواد الخام - ABNA",
		"533108 - Semi Finished Material Consumption -استهلاك المنتج شبة التام - ABNA",
		"513 - Consumables Expenses -المصروفات المستهلكة - ABNA",
		"7001 - Factory Output -اقفال المصروفات التشغيلية في المنتج النهائي - ABNA",
		"6001 - Cost of Goods Sold -تكلفة البضاعة المباعة - ABNA"
	])

	group_account = "7 - Factory Output -اقفال المصروفات التشغيلية في المنتج النهائي - ABNA"
	try:
		group_doc = frappe.get_doc("Account", group_account)
		excluded_account_names.add(group_doc.name)

		child_accounts = frappe.get_all(
			"Account",
			filters={
				"lft": [">=", group_doc.lft],
				"rgt": ["<=", group_doc.rgt],
				"company": company
			},
			pluck="name"
		)
		excluded_account_names.update(child_accounts)
	except frappe.DoesNotExistError:
		pass

	return excluded_account_names


def filter_accounts(data, excluded_accounts):
	filtered = []
	for row in data:
		account_name = row.get("account")
		is_group = row.get("is_group", 0)
		account_label = (row.get("account_name") or "").lower().strip()
		if (
			account_name
			and account_name not in excluded_accounts
			and not is_group
			and not account_label.startswith("total")
		):
			filtered.append(row)
	return filtered


def get_chart_data(columns, expense_data, title):
	labels = []
	values = []

	# Skip first 2 columns: 'account', 'account_name'
	for col in columns[2:]:
		fieldname = col.get("fieldname")
		label = col.get("label")

		# Sum all expense rows except the total row for this period
		period_total = sum(flt(row.get(fieldname)) for row in expense_data if row.get("account") != _("Total"))
		labels.append(label)
		values.append(period_total)

	return {
		"data": {
			"labels": labels,
			"datasets": [
				{
					"name": _("Total Expenses"),
					"values": values
				}
			]
		},
		"type": "bar",
		"fieldtype": "Currency",
		"title": title
	}
