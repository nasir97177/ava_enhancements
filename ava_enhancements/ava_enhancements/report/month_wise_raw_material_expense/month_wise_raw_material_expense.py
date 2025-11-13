# Copyright (c) 2025, Furqan Asghar and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt

from erpnext.accounts.report.financial_statements import (
    get_columns,
    get_data,
    get_period_list,
)

def execute(filters=None):
    if not filters:
        filters = {}

    # Get period list
    period_list = get_period_list(
        filters.get("from_fiscal_year"),
        filters.get("to_fiscal_year"),
        filters.get("period_start_date"),
        filters.get("period_end_date"),
        filters.get("filter_based_on"),
        filters.get("periodicity"),
        company=filters.get("company"),
    )

    # Fetch expense data
    expense = get_data(
        filters.get("company"),
        "Expense",
        "Debit",
        period_list,
        filters=filters,
        accumulated_values=filters.get("accumulated_values"),
        ignore_closing_entries=True,
        ignore_accumulated_values_for_fy=True,
    ) or []

    # Filter to only include raw material and packaging accounts
    expense = filter_accounts(expense)

    # Prepare columns
    columns = get_columns(
        filters.get("periodicity"),
        period_list,
        filters.get("accumulated_values"),
        filters.get("company")
    )

    # Add final total row summing all months per account
    if expense:
        total_row = {"account": _("Total"), "account_name": _("Total")}
        for col in columns[2:]:  # Skip 'account' and 'account_name'
            fieldname = col.get("fieldname")
            total_row[fieldname] = sum(flt(row.get(fieldname)) for row in expense)
        expense.append(total_row)

    # Calculate total and average expense
    fieldnames = [col.get("fieldname") for col in columns]
    has_total_column = "total" in fieldnames

    if has_total_column:
        total_expense = flt(expense[-1].get("total")) or 0.0
        num_periods = len(columns) - 3  # Exclude account, account_name, total
    else:
        num_periods = len(columns) - 2
        total_expense = sum(flt(expense[-1].get(col.get("fieldname"))) for col in columns[2:])

    avg_expense = total_expense / num_periods if num_periods else 0.0

    chart_title = _(
        "Total Expense: {total} | Average Expense: {avg}"
    ).format(
        total=frappe.utils.fmt_money(total_expense, filters.get("presentation_currency")),
        avg=frappe.utils.fmt_money(avg_expense, filters.get("presentation_currency")),
    )

    # Prepare chart
    chart = get_chart_data(columns, expense, chart_title)

    return columns, expense, None, chart


def filter_accounts(data):
    """Allow only Raw Material and Packaging accounts."""
    allowed_accounts = {
        "533101 - Raw Material Consumption -استهلاك المواد الخام - ABNA",
        "533102 - Packaging Material Consumption -استهلاك مواد التغليف - ABNA"
    }
    filtered = []
    for row in data:
        account_name = row.get("account")
        is_group = row.get("is_group", 0)
        if account_name in allowed_accounts and not is_group:
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
        period_total = sum(
            flt(row.get(fieldname)) for row in expense_data if row.get("account") != _("Total")
        )
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
