# Copyright (c) 2025, Furqan Asghar and contributors
# For license information, please see license.txt

# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from typing import Any, Dict, List, Optional, TypedDict

import frappe
from frappe import _
from frappe.query_builder.functions import Sum


class StockBalanceFilter(TypedDict):
    company: Optional[str]
    warehouse: Optional[str]
    show_disabled_warehouses: Optional[int]


SLEntry = Dict[str, Any]


def execute(filters=None):
    columns: List[Dict[str, Any]] = get_columns(filters)
    data: List[Dict[str, Any]] = get_data(filters)
    return columns, data


def get_warehouse_wise_balance(filters: StockBalanceFilter) -> Dict[str, float]:
    sle = frappe.qb.DocType("Stock Ledger Entry")

    query = (
        frappe.qb.from_(sle)
        .select(sle.warehouse, Sum(sle.stock_value_difference).as_("stock_balance"))
        .where((sle.docstatus < 2) & (sle.is_cancelled == 0))
        .groupby(sle.warehouse)
    )

    if filters.get("company"):
        query = query.where(sle.company == filters.get("company"))

    data = query.run(as_list=True)
    # Convert list of [warehouse, balance] to dict
    return {row[0]: row[1] for row in data} if data else {}


def get_warehouses(report_filters: StockBalanceFilter) -> List[Dict[str, Any]]:
    filters = {"company": report_filters.get("company"), "disabled": 0}
    if report_filters.get("show_disabled_warehouses"):
        filters["disabled"] = ("in", [0, report_filters["show_disabled_warehouses"]])

    return frappe.get_all(
        "Warehouse",
        fields=["name", "parent_warehouse", "is_group", "disabled"],
        filters=filters,
        order_by="lft",
    )


def get_data(filters: StockBalanceFilter) -> List[Dict[str, Any]]:
    warehouse_balance = get_warehouse_wise_balance(filters)
    warehouses = get_warehouses(filters)

    # Set stock_balance for each warehouse
    for warehouse in warehouses:
        warehouse["stock_balance"] = warehouse_balance.get(warehouse["name"], 0.0)

    update_indent(warehouses)
    set_balance_in_parent(warehouses)

    return warehouses


def update_indent(warehouses: List[Dict[str, Any]]) -> None:
    warehouse_map = {w["name"]: w for w in warehouses}

    def add_indent(warehouse_name: str, indent: int) -> None:
        warehouse = warehouse_map[warehouse_name]
        warehouse["indent"] = indent
        for child in warehouses:
            if child.get("parent_warehouse") == warehouse_name:
                add_indent(child["name"], indent + 1)

    # Start with top-level groups
    for warehouse in warehouses:
        if warehouse.get("is_group") and warehouse.get("indent") is None:
            add_indent(warehouse["name"], 0)


def set_balance_in_parent(warehouses: List[Dict[str, Any]]) -> None:
    warehouse_map = {w["name"]: w for w in warehouses}
    # Sort warehouses by indent descending
    warehouses_sorted = sorted(warehouses, key=lambda x: x.get("indent", 0), reverse=True)

    for warehouse in warehouses_sorted:
        parent_name = warehouse.get("parent_warehouse")
        if parent_name and parent_name in warehouse_map:
            warehouse_map[parent_name]["stock_balance"] += warehouse["stock_balance"]


def get_columns(filters: StockBalanceFilter) -> List[Dict[str, Any]]:
    columns: List[Dict[str, Any]] = [
        {
            "label": _("Warehouse"),
            "fieldname": "name",
            "fieldtype": "Link",
            "options": "Warehouse",
            "width": 200,
        },
        {
            "label": _("Stock Balance"),
            "fieldname": "stock_balance",
            "fieldtype": "Float",
            "width": 150,
        },
    ]

    if filters.get("show_disabled_warehouses"):
        columns.append(
            {
                "label": _("Warehouse Disabled?"),
                "fieldname": "disabled",
                "fieldtype": "Check",
                "width": 200,
            }
        )

    return columns

