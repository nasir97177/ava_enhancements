from operator import itemgetter
import frappe
from frappe import _
from frappe.utils import cint, date_diff, flt, getdate
from six import iteritems
import erpnext
from erpnext.stock.report.stock_ageing.stock_ageing import FIFOSlots, get_average_age
from erpnext.stock.report.stock_ledger.stock_ledger import get_item_group_condition
from erpnext.stock.utils import add_additional_uom_columns, is_reposting_item_valuation_in_progress

# --------------------- Main Execution ---------------------

def execute(filters=None):
    is_reposting_item_valuation_in_progress()
    if not filters:
        filters = {}

    company_currency = erpnext.get_company_currency(filters.get("company")) \
        if filters.get("company") else frappe.db.get_single_value("Global Defaults", "default_currency")

    include_uom = filters.get("include_uom")
    columns = get_columns(filters)
    items = get_items(filters)
    sle = get_stock_ledger_entries(filters, items)

    if filters.get('show_stock_ageing_data'):
        filters['show_warehouse_wise_stock'] = True
        item_wise_fifo_queue = FIFOSlots(filters, sle).generate()

    if not sle:
        return columns, [], {}, {}

    iwb_map = get_item_warehouse_map(filters, sle)
    item_map = get_item_details(items, sle, filters)
    item_reorder_detail_map = get_item_reorder_details(item_map.keys())

    data = []
    conversion_factors = {}

    for (company, item, warehouse) in sorted(iwb_map):
        if item_map.get(item):
            qty_dict = iwb_map[(company, item, warehouse)]
            item_reorder_level = 0
            item_reorder_qty = 0
            if item + warehouse in item_reorder_detail_map:
                item_reorder_level = item_reorder_detail_map[item + warehouse]["warehouse_reorder_level"]
                item_reorder_qty = item_reorder_detail_map[item + warehouse]["warehouse_reorder_qty"]

            report_data = {
                'currency': company_currency,
                'item_code': item,
                'warehouse': warehouse,
                'company': company,
                'reorder_level': item_reorder_level,
                'reorder_qty': item_reorder_qty,
                'branch': get_branch(warehouse)
            }
            report_data.update(item_map[item])
            report_data.update(qty_dict)

            if include_uom:
                conversion_factors.setdefault(item, item_map[item].get("conversion_factor", 1))

            if filters.get('show_stock_ageing_data'):
                fifo_queue = item_wise_fifo_queue.get((item, warehouse), {}).get('fifo_queue', [])
                stock_ageing_data = {'average_age': 0, 'earliest_age': 0, 'latest_age': 0}
                if fifo_queue:
                    fifo_queue = sorted([f for f in fifo_queue if f[1]], key=itemgetter(1))
                    if fifo_queue:
                        stock_ageing_data['average_age'] = get_average_age(fifo_queue, filters.get("to_date"))
                        stock_ageing_data['earliest_age'] = date_diff(filters.get("to_date"), fifo_queue[0][1])
                        stock_ageing_data['latest_age'] = date_diff(filters.get("to_date"), fifo_queue[-1][1])
                report_data.update(stock_ageing_data)

            data.append(report_data)

    add_additional_uom_columns(columns, data, include_uom, conversion_factors)

    # --- Aggregate Branch + Item for Summary ---
    branch_summary = get_branch_wise_summary(data)

    # --- Generate Charts ---
    bar_chart = get_branch_item_stacked_chart(branch_summary)
    item_bar_chart = get_item_bar_chart(branch_summary)

    return columns, branch_summary, bar_chart, item_bar_chart

# --------------------- Branch-wise Aggregation ---------------------

def get_branch_wise_summary(data):
    """
    Aggregate Balance Qty by Branch and Item.
    Returns one row per item per branch with summed bal_qty.
    """
    agg_map = {}

    for d in data:
        branch = d.get('branch') or 'Other'
        item = d.get('item_code')
        key = (branch, item)

        if key not in agg_map:
            agg_map[key] = {
                'branch': branch,
                'item_code': item,
                'item_name': d.get('item_name'),
                'item_group': d.get('item_group'),
                'stock_uom': d.get('stock_uom'),
                'reorder_level': 0,
                'reorder_qty': 0,
                'bal_qty': 0.0,
            }

        agg_map[key]['bal_qty'] += flt(d.get('bal_qty', 0))
        agg_map[key]['reorder_level'] += flt(d.get('reorder_level', 0))
        agg_map[key]['reorder_qty'] += flt(d.get('reorder_qty', 0))

    return list(agg_map.values())

# --------------------- Branch-wise Stacked Bar Chart ---------------------

def get_branch_item_stacked_chart(data):
    """
    Generate stacked bar chart: x-axis = Branch, y-axis = Balance Qty, 
    each bar is split by Item.
    """
    branch_item_map = {}
    items_set = set()

    for d in data:
        branch = d.get('branch') or 'Other'
        item = d.get('item_code')
        bal_qty = flt(d.get('bal_qty', 0))

        items_set.add(item)
        branch_item_map.setdefault(branch, {}).setdefault(item, 0.0)
        branch_item_map[branch][item] += bal_qty

    labels = list(branch_item_map.keys())
    items_list = sorted(list(items_set))

    datasets = []
    for item in items_list:
        values = []
        for branch in labels:
            values.append(branch_item_map[branch].get(item, 0))
        datasets.append({
            "name": item,
            "values": values
        })

    chart = {
        "data": {
            "labels": labels,
            "datasets": datasets
        },
        "type": "bar",
        "fieldtype": "Float",
        "height": 400,
        "stacked": True
    }

    return chart

# --------------------- Item-wise Bar Chart ---------------------

def get_item_bar_chart(data):
    """
    Generate stacked bar chart: x-axis = Branch, y-axis = Balance Qty, 
    each bar is split by Item.
    """
    branch_item_map = {}
    items_set = set()

    for d in data:
        branch = d.get('branch') or 'Other'
        item = d.get('item_code')
        bal_qty = flt(d.get('bal_qty', 0))

        items_set.add(item)
        branch_item_map.setdefault(branch, {}).setdefault(item, 0.0)
        branch_item_map[branch][item] += bal_qty

    labels = list(branch_item_map.keys())
    items_list = sorted(list(items_set))

    datasets = []
    for item in items_list:
        values = []
        for branch in labels:
            values.append(branch_item_map[branch].get(item, 0))
        datasets.append({
            "name": item,
            "values": values
        })

    chart = {
        "data": {
            "labels": labels,
            "datasets": datasets
        },
        "type": "bar",
        "fieldtype": "Float",
        "height": 400,
        "stacked": True,
        "colors": [
            "#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0", "#9966FF",
            "#FF9F40", "#FFCD56", "#C9CBCF", "#36A2EB", "#4BC0C0"
        ][:len(items_list)]  # Limit colors to number of items
    }

    return chart

# --------------------- Branch Mapping ---------------------

def get_branch(warehouse_name):
    riyadh_warehouses = [
        "Finished Goods-RYD - ABNA", "In-Transit-RYD - ABNA",
        "R-1-ABNA","R-2 - ABNA","R-3 - ABNA","R-4 - ABNA","R-5 - ABNA","R-6 - ABNA",
        "R-7 -ABNA","R-8 - ABNA","R-9 - ABNA","R-10 - ABNA","R-11 - ABNA","R-12 - ABNA",
        "R-13 - ABNA","R-14 - ABNA","R-15- ABNA","R-16 - ABNA","R-17 - ABNA","R-18 - ABNA",
        "R-19 - ABNA"
    ]

    jeddah_warehouses = [
        "Finished Goods-JED - ABNA", "In-Transit-JED - ABNA",
        "J-1 - ABNA","J-2 - ABNA","J-3 - ABNA","J-4 - ABNA","J-5 - ABNA","J-6 - ABNA",
        "J-7 - ABNA","J-8 - ABNA","J-9 - ABNA","J-10 - ABNA","J-11 - ABNA"
    ]

    dammam_warehouses = [
        "Finished Goods-DMM - ABNA", "In-Transit-DMM - ABNA",
        "D-1 - ABNA","D-2 - ABNA","D-3 - ABNA","D-4 - ABNA","D-5 - ABNA","D-6 - ABNA","D-7 - ABNA"
    ]

    factory_warehouses = [
        "Finished Goods-Central Warehouse - ABNA"
    ]

    if warehouse_name in riyadh_warehouses:
        return "Riyadh"
    elif warehouse_name in jeddah_warehouses:
        return "Jeddah"
    elif warehouse_name in dammam_warehouses:
        return "Dammam"
    elif warehouse_name in factory_warehouses:
        return "Factory"
    else:
        return "Other"

# --------------------- Helper Functions ---------------------

def get_columns(filters):
    columns = [
        {"label": _("Item"), "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 250},
        {"label": _("Item Name"), "fieldname": "item_name", "width": 300},
        {"label": _("Item Group"), "fieldname": "item_group", "fieldtype": "Link", "options": "Item Group", "width": 120},
        {"label": _("Stock UOM"), "fieldname": "stock_uom", "fieldtype": "Link", "options": "UOM", "width": 90},
        {"label": _("Branch"), "fieldname": "branch", "width": 100},
        {"label": _("Balance Qty"), "fieldname": "bal_qty", "fieldtype": "Float", "width": 120},
        {"label": _("Reorder Level"), "fieldname": "reorder_level", "fieldtype": "Float", "width": 120},
        {"label": _("Reorder Qty"), "fieldname": "reorder_qty", "fieldtype": "Float", "width": 120},
    ]

    if filters.get('show_stock_ageing_data'):
        columns += [
            {'label': _('Average Age'), 'fieldname': 'average_age', 'width': 100},
            {'label': _('Earliest Age'), 'fieldname': 'earliest_age', 'width': 100},
            {'label': _('Latest Age'), 'fieldname': 'latest_age', 'width': 100}
        ]

    return columns

def get_conditions(filters):
    conditions = ""
    if not filters.get("from_date"):
        frappe.throw(_("'From Date' is required"))

    if filters.get("to_date"):
        conditions += " and sle.posting_date <= %s" % frappe.db.escape(filters.get("to_date"))
    else:
        frappe.throw(_("'To Date' is required"))

    if filters.get("company"):
        conditions += " and sle.company = %s" % frappe.db.escape(filters.get("company"))

    if filters.get("warehouse"):
        warehouse_details = frappe.db.get_value("Warehouse",
            filters.get("warehouse"), ["lft", "rgt"], as_dict=1)
        if warehouse_details:
            conditions += " and exists (select name from `tabWarehouse` wh \
                where wh.lft >= %s and wh.rgt <= %s and sle.warehouse = wh.name)" % (warehouse_details.lft,
                warehouse_details.rgt)

    if filters.get("warehouse_type") and not filters.get("warehouse"):
        conditions += " and exists (select name from `tabWarehouse` wh \
            where wh.warehouse_type = '%s' and sle.warehouse = wh.name)" % (filters.get("warehouse_type"))

    return conditions

def get_stock_ledger_entries(filters, items):
    item_conditions_sql = ''
    if items:
        item_conditions_sql = ' and sle.item_code in ({})'.format(
            ', '.join(frappe.db.escape(i, percent=False) for i in items)
        )

    conditions = get_conditions(filters)

    return frappe.db.sql("""
        select
            sle.item_code, warehouse, sle.posting_date, sle.actual_qty, sle.valuation_rate,
            sle.company, sle.voucher_type, sle.qty_after_transaction, sle.stock_value_difference,
            sle.item_code as name, sle.voucher_no, sle.stock_value, sle.batch_no
        from
            `tabStock Ledger Entry` sle
        where sle.docstatus < 2 %s %s
        and is_cancelled = 0
        order by sle.posting_date, sle.posting_time, sle.creation, sle.actual_qty
    """ % (item_conditions_sql, conditions), as_dict=1)

def get_item_warehouse_map(filters, sle):
    iwb_map = {}
    from_date = getdate(filters.get("from_date"))
    to_date = getdate(filters.get("to_date"))
    float_precision = cint(frappe.db.get_default("float_precision")) or 3

    for d in sle:
        key = (d.company, d.item_code, d.warehouse)
        if key not in iwb_map:
            iwb_map[key] = frappe._dict({
                "opening_qty": 0.0, "opening_val": 0.0,
                "in_qty": 0.0, "in_val": 0.0,
                "out_qty": 0.0, "out_val": 0.0,
                "bal_qty": 0.0, "bal_val": 0.0,
                "val_rate": 0.0
            })

        qty_dict = iwb_map[key]

        if d.voucher_type == "Stock Reconciliation" and not d.batch_no:
            qty_diff = flt(d.qty_after_transaction) - flt(qty_dict.bal_qty)
        else:
            qty_diff = flt(d.actual_qty)

        value_diff = flt(d.stock_value_difference)

        if d.posting_date < from_date or (d.posting_date == from_date
            and d.voucher_type == "Stock Reconciliation" and
            frappe.db.get_value("Stock Reconciliation", d.voucher_no, "purpose") == "Opening Stock"):
            qty_dict.opening_qty += qty_diff
            qty_dict.opening_val += value_diff

        elif from_date <= d.posting_date <= to_date:
            if flt(qty_diff, float_precision) >= 0:
                qty_dict.in_qty += qty_diff
                qty_dict.in_val += value_diff
            else:
                qty_dict.out_qty += abs(qty_diff)
                qty_dict.out_val += abs(value_diff)

        qty_dict.val_rate = d.valuation_rate
        qty_dict.bal_qty += qty_diff
        qty_dict.bal_val += value_diff

    iwb_map = filter_items_with_no_transactions(iwb_map, float_precision)
    return iwb_map

def filter_items_with_no_transactions(iwb_map, float_precision):
    for (company, item, warehouse) in sorted(list(iwb_map)):
        qty_dict = iwb_map[(company, item, warehouse)]
        no_transactions = True
        for key, val in iteritems(qty_dict):
            val = flt(val, float_precision)
            qty_dict[key] = val
            if key != "val_rate" and val:
                no_transactions = False
        if no_transactions:
            iwb_map.pop((company, item, warehouse))
    return iwb_map

def get_items(filters):
    allowed_groups = ['Carton', 'Fridge Pack', 'Green Pack', 'Bottle']
    conditions = []
    if filters.get("item_code"):
        conditions.append("item.name=%(item_code)s")
    else:
        conditions.append("item.item_group IN ({})".format(
            ','.join(frappe.db.escape(g, percent=False) for g in allowed_groups)
        ))
        if filters.get("brand"):
            conditions.append("item.brand=%(brand)s")

    items = []
    if conditions:
        items = frappe.db.sql_list("""select name from `tabItem` item where {}"""
            .format(" and ".join(conditions)), filters)
    return items

def get_item_details(items, sle, filters):
    item_details = {}
    if not items:
        items = []
    for item in items:
        d = frappe.db.get_value("Item", item,
            ["item_name", "item_group", "stock_uom", "brand"], as_dict=1)
        if d:
            item_details[item] = d
            item_details[item]["conversion_factor"] = 1
    return item_details

def get_item_reorder_details(items):
    reorder_map = {}
    for item in items:
        wh_reorder = frappe.db.sql("""
            select warehouse, warehouse_reorder_level, warehouse_reorder_qty
            from `tabItem Reorder`
            where parent=%s
        """, item, as_dict=1)
        for d in wh_reorder:
            key = item + d.warehouse
            reorder_map[key] = d
    return reorder_map