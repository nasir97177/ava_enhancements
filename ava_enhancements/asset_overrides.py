import sys
import json
import math
import frappe
from frappe import _
from frappe.utils import (
    add_days,
    add_months,
    cint,
    date_diff,
    flt,
    get_datetime,
    get_last_day,
    getdate,
    month_diff,
    nowdate,
    today,
    cstr
)
from six import string_types

import erpnext
from erpnext.accounts.general_ledger import make_reverse_gl_entries
from erpnext.assets.doctype.asset.depreciation import (
    get_depreciation_accounts,
    get_disposal_account_and_cost_center,
    get_credit_and_debit_accounts,
    get_depreciable_assets
)
from erpnext.assets.doctype.asset_category.asset_category import get_asset_category_account

from erpnext.accounts.doctype.accounting_dimension.accounting_dimension import get_checks_for_pl_and_bs_accounts

from erpnext.assets.doctype.asset.asset import get_depreciation_amount, get_item_details

# Modified ##### if args.get("depreciation_method") == 'Unit of Production'


def custom_get_depreciation_accounts(asset):
    fixed_asset_account = accumulated_depreciation_account = depreciation_expense_account = None

    accounts = {
        'fixed_asset_account': asset.fixed_asset_account,
        'accumulated_depreciation_account': asset.accumulated_depreciation_account,
        'depreciation_expense_account': asset.depreciation_expense_account
    }

    accounts = frappe._dict(accounts)
    if accounts:
        fixed_asset_account = accounts.fixed_asset_account
        accumulated_depreciation_account = accounts.accumulated_depreciation_account
        depreciation_expense_account = accounts.depreciation_expense_account

    if not accumulated_depreciation_account or not depreciation_expense_account:
        accounts = frappe.get_cached_value('Company', asset.company,
                                           ["accumulated_depreciation_account", "depreciation_expense_account"])

        if not accumulated_depreciation_account:
            accumulated_depreciation_account = accounts[0]
        if not depreciation_expense_account:
            depreciation_expense_account = accounts[1]

    if not fixed_asset_account or not accumulated_depreciation_account or not depreciation_expense_account:
        frappe.throw(_("Please set Depreciation related Accounts in Asset {0} or Company {1}")
                     .format(asset.name, asset.company))

    return fixed_asset_account, accumulated_depreciation_account, depreciation_expense_account


@frappe.whitelist()
def ava_make_journal_entry_asset_py(asset_name):
    asset = frappe.get_doc("Asset", asset_name)
    fixed_asset_account, accumulated_depreciation_account, depreciation_expense_account = \
        custom_get_depreciation_accounts(asset)

    depreciation_cost_center, depreciation_series = frappe.db.get_value("Company", asset.company,
                                                                        ["depreciation_cost_center",
                                                                         "series_for_depreciation_entry"])
    depreciation_cost_center = asset.cost_center or depreciation_cost_center

    je = frappe.new_doc("Journal Entry")
    je.voucher_type = "Depreciation Entry"
    je.naming_series = depreciation_series
    je.company = asset.company
    je.remark = "Depreciation Entry against asset {0}".format(asset_name)

    je.append("accounts", {
        "account": depreciation_expense_account,
        "reference_type": "Asset",
        "reference_name": asset.name,
        "cost_center": depreciation_cost_center
    })

    je.append("accounts", {
        "account": accumulated_depreciation_account,
        "reference_type": "Asset",
        "reference_name": asset.name
    })

    return je


@frappe.whitelist()
def ava_make_depreciation_entry_depreciation_py(asset_name, date=None):
    frappe.has_permission('Journal Entry', throw=True)

    if not date:
        date = today()

    asset = frappe.get_doc("Asset", asset_name)
    fixed_asset_account, accumulated_depreciation_account, depreciation_expense_account = \
        custom_get_depreciation_accounts(asset)

    depreciation_cost_center, depreciation_series = frappe.get_cached_value('Company', asset.company,
                                                                            ["depreciation_cost_center",
                                                                             "series_for_depreciation_entry"])

    depreciation_cost_center = asset.cost_center or depreciation_cost_center

    accounting_dimensions = get_checks_for_pl_and_bs_accounts()

    for d in asset.get("schedules"):
        if not d.journal_entry and getdate(d.schedule_date) <= getdate(date):
            je = frappe.new_doc("Journal Entry")
            je.voucher_type = "Depreciation Entry"
            je.naming_series = depreciation_series
            je.posting_date = d.schedule_date
            je.company = asset.company
            je.finance_book = d.finance_book
            je.remark = "Depreciation Entry against {0} worth {1}".format(asset_name, d.depreciation_amount)

            credit_account, debit_account = get_credit_and_debit_accounts(accumulated_depreciation_account,
                                                                          depreciation_expense_account)

            credit_entry = {
                "account": credit_account,
                "credit_in_account_currency": d.depreciation_amount,
                "reference_type": "Asset",
                "reference_name": asset.name,
                "cost_center": depreciation_cost_center
            }

            debit_entry = {
                "account": debit_account,
                "debit_in_account_currency": d.depreciation_amount,
                "reference_type": "Asset",
                "reference_name": asset.name,
                "cost_center": depreciation_cost_center
            }

            for dimension in accounting_dimensions:
                if asset.get(dimension['fieldname']) or dimension.get('mandatory_for_bs'):
                    credit_entry.update({
                        dimension['fieldname']: asset.get(dimension['fieldname']) or dimension.get('default_dimension')
                    })

                if asset.get(dimension['fieldname']) or dimension.get('mandatory_for_pl'):
                    debit_entry.update({
                        dimension['fieldname']: asset.get(dimension['fieldname']) or dimension.get('default_dimension')
                    })

            je.append("accounts", credit_entry)

            je.append("accounts", debit_entry)

            je.flags.ignore_permissions = True
            je.save()
            if not je.meta.get_workflow():
                je.submit()

            d.db_set("journal_entry", je.name)

            idx = cint(d.finance_book_id)
            finance_books = asset.get('finance_books')[idx - 1]
            finance_books.value_after_depreciation -= d.depreciation_amount
            finance_books.db_update()

    asset.set_status()

    return asset


def ava_get_cwip_account_asset_py(self, cwip_enabled=False):
    cwip_account = None
    try:
        cwip_account = self.capital_work_in_progress_account
    except Exception:
        # if no cwip account found in category or company and "cwip is enabled" then raise else silently pass
        if cwip_enabled:
            raise

    return cwip_account


def ava_get_fixed_asset_account_asset_py(self):
    if not self.fixed_asset_account:
        frappe.throw(
            _("Set {0} in asset category {1} for company {2}").format(
                frappe.bold("Fixed Asset Account"),
                frappe.bold(self.name),
                frappe.bold(self.company),
            ),
            title=_("Account not Found"),
        )
    return self.fixed_asset_account


def ava_on_cancel_adjustment_py(self):
    self.reschedule_depreciations(self.current_asset_value)
    self.cancel_asset_value_adjustment_entry()


def ava_cancel_asset_value_adjustment_entry_adjustment_py(self):
    if self.journal_entry:
        frappe.get_doc("Journal Entry", self.journal_entry).cancel()


def ava_make_depreciation_entry_for_asset_value_adjustment_py(self):
    asset = frappe.get_doc("Asset", self.asset)
    fixed_asset_account, accumulated_depreciation_account, depreciation_expense_account = \
        custom_get_depreciation_accounts(asset)

    depreciation_cost_center, depreciation_series = frappe.get_cached_value('Company',  asset.company,
        ["depreciation_cost_center", "series_for_depreciation_entry"])

    je = frappe.new_doc("Journal Entry")
    je.voucher_type = "Depreciation Entry"
    je.naming_series = depreciation_series
    je.posting_date = self.date
    je.company = self.company
    je.remark = "Depreciation Entry against {0} worth {1}".format(self.asset, self.difference_amount)
    je.finance_book = self.finance_book

    credit_entry = {
        "account": accumulated_depreciation_account,
        "credit_in_account_currency": self.difference_amount,
        "cost_center": depreciation_cost_center or self.cost_center
    }

    debit_entry = {
        "account": depreciation_expense_account,
        "debit_in_account_currency": self.difference_amount,
        "cost_center": depreciation_cost_center or self.cost_center
    }

    accounting_dimensions = get_checks_for_pl_and_bs_accounts()

    for dimension in accounting_dimensions:
        if dimension.get('mandatory_for_bs'):
            credit_entry.update({
                dimension['fieldname']: self.get(dimension['fieldname']) or dimension.get('default_dimension')
            })

        if dimension.get('mandatory_for_pl'):
            debit_entry.update({
                dimension['fieldname']: self.get(dimension['fieldname']) or dimension.get('default_dimension')
            })

    je.append("accounts", credit_entry)
    je.append("accounts", debit_entry)

    je.flags.ignore_permissions = True
    je.submit()

    self.db_set("journal_entry", je.name)


def ava_get_gl_entries_for_asset_repair_py(self):
    gl_entries = []
    repair_and_maintenance_account = frappe.db.get_value('Company', self.company, 'repair_and_maintenance_account')
    fixed_asset_account = frappe.get_value('Asset', self.asset, 'fixed_asset_account')
    expense_account = frappe.get_doc('Purchase Invoice', self.purchase_invoice).items[0].expense_account

    gl_entries.append(
        self.get_gl_dict({
            "account": expense_account,
            "credit": self.repair_cost,
            "credit_in_account_currency": self.repair_cost,
            "against": repair_and_maintenance_account,
            "voucher_type": self.doctype,
            "voucher_no": self.name,
            "cost_center": self.cost_center,
            "posting_date": getdate(),
            "company": self.company
        }, item=self)
    )

    if self.get('stock_consumption'):
        # creating GL Entries for each row in Stock Items based on the Stock Entry created for it
        stock_entry = frappe.get_doc('Stock Entry', self.stock_entry)
        for item in stock_entry.items:
            gl_entries.append(
                self.get_gl_dict({
                    "account": item.expense_account,
                    "credit": item.amount,
                    "credit_in_account_currency": item.amount,
                    "against": repair_and_maintenance_account,
                    "voucher_type": self.doctype,
                    "voucher_no": self.name,
                    "cost_center": self.cost_center,
                    "posting_date": getdate(),
                    "company": self.company
                }, item=self)
            )

    gl_entries.append(
        self.get_gl_dict({
            "account": fixed_asset_account,
            "debit": self.total_repair_cost,
            "debit_in_account_currency": self.total_repair_cost,
            "against": expense_account,
            "voucher_type": self.doctype,
            "voucher_no": self.name,
            "cost_center": self.cost_center,
            "posting_date": getdate(),
            "against_voucher_type": "Purchase Invoice",
            "against_voucher": self.purchase_invoice,
            "company": self.company
        }, item=self)
    )

    return gl_entries


@frappe.whitelist()
def ava_post_depreciation_entries_depreciation_py(date=None):
    if not cint(frappe.db.get_value("Accounts Settings", None, "book_asset_depreciation_entry_automatically")):
        return

    if not date:
        date = today()

    for asset in get_depreciable_assets(date):
        try:
            ava_make_depreciation_entry_depreciation_py(asset, date)
        except Exception as e:
            error_message = frappe.get_traceback()+"{0}\n".format(str(e))
            frappe.log_error(error_message, 'Error occured While automatically Creating depreciation entries for {0}'.format(asset))
        finally:
            frappe.db.commit()


def ava_get_status_asset_py(self):
    '''Returns status based on whether it is draft, submitted, scrapped or depreciated'''
    if self.docstatus == 0:
        status = "Draft"
    elif self.docstatus == 1:
        status = "Submitted"

        if self.journal_entry_for_scrap:
            status = "Scrapped"
        elif self.finance_books:
            idx = self.get_default_finance_book_idx() or 0

            expected_value_after_useful_life = self.finance_books[idx].expected_value_after_useful_life
            value_after_depreciation = self.finance_books[idx].value_after_depreciation

            journal_entries = []
            if self.get('schedules'):
                journal_entries = [d.journal_entry for d in self.get('schedules') if d.journal_entry]
            if journal_entries:
                if flt(value_after_depreciation) <= expected_value_after_useful_life:
                    status = "Fully Depreciated"
                elif flt(value_after_depreciation) < flt(self.gross_purchase_amount):
                    status = 'Partially Depreciated'
    elif self.docstatus == 2:
        status = "Cancelled"
    return status

def ava_validate_expected_value_after_useful_life_asset_py(self):
    for row in self.get('finance_books'):
        accumulated_depreciation_after_full_schedule = [d.accumulated_depreciation_amount
            for d in self.get("schedules") if cint(d.finance_book_id) == row.idx]

        if accumulated_depreciation_after_full_schedule:
            depreciation_methods = [d.depreciation_method for d in self.finance_books]
            accumulated_depreciation_after_full_schedule = max(accumulated_depreciation_after_full_schedule)

            asset_value_after_full_schedule = flt(
                flt(self.gross_purchase_amount) -
                flt(accumulated_depreciation_after_full_schedule), self.precision('gross_purchase_amount'))

            if (row.expected_value_after_useful_life and
                row.expected_value_after_useful_life < asset_value_after_full_schedule):
                frappe.throw(_("Depreciation Row {0}: Expected value after useful life must be greater than or equal to {1}")
                    .format(row.idx, asset_value_after_full_schedule))
            elif not row.expected_value_after_useful_life and 'Manual' not in depreciation_methods:
                row.expected_value_after_useful_life = asset_value_after_full_schedule

            if 'Manual' in depreciation_methods:
                if asset_value_after_full_schedule < 0 or accumulated_depreciation_after_full_schedule > flt(self.gross_purchase_amount):
                    frappe.throw('Invalid manual entry')

                for d in self.get("schedules"):
                    if not d.journal_entry and self._action=="update_after_submit":
                        d.db_update()


def ava_prepare_depreciation_data_asset_py(self, date_of_sale=None, date_of_return=None):
    if self.calculate_depreciation:
        self.value_after_depreciation = 0
        self.set_depreciation_rate()
        if 'Manual' not in [d.depreciation_method for d in self.finance_books]:
            self.make_depreciation_schedule(date_of_sale)
        self.set_accumulated_depreciation(date_of_sale, date_of_return)
    else:
        self.finance_books = []
        self.value_after_depreciation = (flt(self.gross_purchase_amount) -
            flt(self.opening_accumulated_depreciation))


def ava_set_missing_values_asset_py(self):
    if not self.asset_category:
        self.asset_category = frappe.get_cached_value("Item", self.item_code, "asset_category")

    if self.item_code and not self.get('finance_books'):
        finance_books = get_item_details(self.item_code, self.asset_category)
        self.set('finance_books', finance_books)

    if self.get('finance_books') and self.get('schedules'):
        for row in self.get('finance_books'):
            if not [d.journal_entry for d in self.get('schedules') if d.journal_entry]:
                row.value_after_depreciation = self.gross_purchase_amount

        depreciation_methods = [d.depreciation_method for d in self.finance_books]
        if 'Manual' in depreciation_methods:
            for d in self.get('schedules'):
                if not d.finance_book_id:
                    d.finance_book_id = [d.idx for d in self.finance_books if d.depreciation_method == 'Manual'][0]


def on_update_asset(self, method):
    if self.get('schedules'):
        if None in [d.finance_book_id for d in self.get('schedules')]:
            self.set_missing_values()

        self.set_accumulated_depreciation()
        self.validate_expected_value_after_useful_life()
        self.status = self.get_status()


