# import frappe
# from frappe.model.document import Document
# import json
# from frappe.utils import flt

# class ManualItemValuation(Document):
#     pass

# @frappe.whitelist()
# def manual_item_valuation(items, from_date, to_date):
#     """
#     Update Stock Ledger Entries with manual valuation rate,
#     stock_value = qty_after_transaction * valuation_rate
#     stock_value_difference = actual_qty * valuation_rate
#     """
#     items = json.loads(items)

#     for item in items:
#         item_code = item.get("item_code")
#         valuation_rate = flt(item.get("valuation_rate") or 0)

#         # Fetch Stock Ledger Entries
#         sle_list = frappe.get_all(
#             "Stock Ledger Entry",
#             filters={
#                 "item_code": item_code,
#                 "posting_date": ["between", [from_date, to_date]],
#                 "docstatus": 1
#             },
#             fields=["name", "actual_qty", "qty_after_transaction"]
#         )

#         for sle in sle_list:
#             actual_qty = flt(sle.actual_qty)
#             qty_after_transaction = flt(sle.qty_after_transaction)

#             # Calculate stock value and difference
#             stock_value = qty_after_transaction * valuation_rate
#             stock_value_difference = actual_qty * valuation_rate

#             # Update SLE
#             frappe.db.set_value("Stock Ledger Entry", sle.name, "valuation_rate", valuation_rate)
#             frappe.db.set_value("Stock Ledger Entry", sle.name, "stock_value", stock_value)
#             frappe.db.set_value("Stock Ledger Entry", sle.name, "stock_value_difference", stock_value_difference)

#         # Optional: update Item's default valuation rate
#         frappe.db.set_value("Item", item_code, "valuation_rate", valuation_rate)

#     frappe.db.commit()
#     return True


# import frappe
# from frappe.model.document import Document
# import json
# from frappe.utils import flt

# class ManualItemValuation(Document):
#     pass

# @frappe.whitelist()
# def manual_item_valuation(items, from_date, to_date):
#     """
#     Update SLE with manual valuation and update corresponding GL entries
#     for Finished Goods and COGS based on actual_qty sign.
#     """

#     items = json.loads(items)

#     # Target accounts
#     stock_account = "110304 - Finished Goods -المنتج التام - ABNA"
#     cogs_account = "6001 - Cost of Goods Sold -تكلفة البضاعة المباعة - ABNA"

#     for item in items:
#         item_code = item.get("item_code")
#         valuation_rate = flt(item.get("valuation_rate") or 0)

#         # Fetch relevant Stock Ledger Entries
#         sle_list = frappe.get_all(
#             "Stock Ledger Entry",
#             filters={
#                 "item_code": item_code,
#                 "posting_date": ["between", [from_date, to_date]],
#                 "docstatus": 1
#             },
#             fields=["name", "actual_qty", "qty_after_transaction", "voucher_no"]
#         )

#         # Accumulate totals by voucher_no with sign logic
#         voucher_totals = {}

#         for sle in sle_list:
#             actual_qty = flt(sle.actual_qty)
#             qty_after_transaction = flt(sle.qty_after_transaction)
#             voucher_no = sle.voucher_no

#             # Calculate stock values
#             stock_value = qty_after_transaction * valuation_rate
#             stock_value_difference = actual_qty * valuation_rate

#             # Update SLE fields
#             frappe.db.set_value("Stock Ledger Entry", sle.name, "valuation_rate", valuation_rate)
#             frappe.db.set_value("Stock Ledger Entry", sle.name, "stock_value", stock_value)
#             frappe.db.set_value("Stock Ledger Entry", sle.name, "stock_value_difference", stock_value_difference)

#             # Accumulate totals per voucher with direction based on actual_qty
#             if voucher_no not in voucher_totals:
#                 voucher_totals[voucher_no] = {"stock_value": 0, "cogs_value": 0}

#             if actual_qty >= 0:
#                 # Positive movement
#                 voucher_totals[voucher_no]["stock_value"] += stock_value
#                 voucher_totals[voucher_no]["cogs_value"] += stock_value_difference * -1
#             else:
#                 # Negative movement
#                 voucher_totals[voucher_no]["stock_value"] += stock_value * -1
#                 voucher_totals[voucher_no]["cogs_value"] += stock_value_difference

#         # Update GL Entries per voucher
#         for voucher_no, totals in voucher_totals.items():
#             gl_entries = frappe.get_all(
#                 "GL Entry",
#                 filters={
#                     "voucher_no": voucher_no,
#                     "account": ["in", [stock_account, cogs_account]],
#                     "docstatus": 1
#                 },
#                 fields=["name", "account"]
#             )

#             for gl in gl_entries:
#                 if gl.account == stock_account:
#                     if totals["stock_value"] >= 0:
#                         frappe.db.set_value("GL Entry", gl.name, "debit", totals["stock_value"])
#                         frappe.db.set_value("GL Entry", gl.name, "credit", 0)
#                     else:
#                         frappe.db.set_value("GL Entry", gl.name, "debit", 0)
#                         frappe.db.set_value("GL Entry", gl.name, "credit", abs(totals["stock_value"]))
#                 elif gl.account == cogs_account:
#                     if totals["cogs_value"] >= 0:
#                         frappe.db.set_value("GL Entry", gl.name, "debit", totals["cogs_value"])
#                         frappe.db.set_value("GL Entry", gl.name, "credit", 0)
#                     else:
#                         frappe.db.set_value("GL Entry", gl.name, "debit", 0)
#                         frappe.db.set_value("GL Entry", gl.name, "credit", abs(totals["cogs_value"]))

#         # Update item valuation rate
#         frappe.db.set_value("Item", item_code, "valuation_rate", valuation_rate)

#     frappe.db.commit()
#     return True



import frappe
from frappe.model.document import Document
import json
from frappe.utils import flt

class ManualItemValuation(Document):
    pass

@frappe.whitelist()
def manual_item_valuation(items, from_date, to_date):
    """
    Update SLE and GL Entries with manual valuation **only for Sales Invoices and Delivery Notes**
    
    Logic:
    - Qty Out (Delivery Note / Sales Invoice): COGS Debit, Stock Credit
    - Qty In  (should not apply here, skipped)
    """

    items = json.loads(items)

    stock_account = "110304 - Finished Goods -المنتج التام - ABNA"
    cogs_account = "6001 - Cost of Goods Sold -تكلفة البضاعة المباعة - ABNA"

    for item in items:
        item_code = item.get("item_code")
        valuation_rate = flt(item.get("valuation_rate") or 0)

        # Fetch Stock Ledger Entries for the item, only for Sales Invoice / Delivery Note
        sle_list = frappe.get_all(
            "Stock Ledger Entry",
            filters={
                "item_code": item_code,
                "posting_date": ["between", [from_date, to_date]],
                "docstatus": 1,
                "voucher_type": ["in", ["Sales Invoice", "Delivery Note"]]
            },
            fields=["name", "actual_qty", "qty_after_transaction", "voucher_no"]
        )

        for sle in sle_list:
            actual_qty = flt(sle.actual_qty)
            stock_value_diff = actual_qty * valuation_rate

            # Update SLE
            frappe.db.set_value("Stock Ledger Entry", sle.name, "valuation_rate", valuation_rate)
            frappe.db.set_value("Stock Ledger Entry", sle.name, "stock_value_difference", stock_value_diff)

            # Fetch GL Entries for this voucher
            gl_entries = frappe.get_all(
                "GL Entry",
                filters={
                    "voucher_no": sle.voucher_no,
                    "account": ["in", [stock_account, cogs_account]],
                    "docstatus": 1
                },
                fields=["name", "account"]
            )

            for gl in gl_entries:
                gl_doc = frappe.get_doc("GL Entry", gl.name)
                if gl.account == stock_account:
                    # Stock Account: Qty Out → Credit
                    gl_doc.debit = 0
                    gl_doc.credit = abs(stock_value_diff)
                elif gl.account == cogs_account:
                    # COGS Account: Qty Out → Debit
                    gl_doc.debit = abs(stock_value_diff)
                    gl_doc.credit = 0
                gl_doc.save(ignore_permissions=True)

        # Update Item valuation rate
        frappe.db.set_value("Item", item_code, "valuation_rate", valuation_rate)

    frappe.db.commit()
    return True
