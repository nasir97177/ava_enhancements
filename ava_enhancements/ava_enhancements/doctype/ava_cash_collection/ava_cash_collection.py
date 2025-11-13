# Copyright (c) 2022, Furqan Asghar and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import cstr, nowdate, flt
from erpnext.accounts.utils import get_account_currency, get_balance_on
from frappe.model.document import Document

class AvaCashCollection(Document):
	def on_submit(self):
		for d in self.sales_invoice_reference:
			frappe.db.set_value('Sales Invoice', d.sales_invoice, 'sales_invoice_closed', 1)

		for d in self.payment_entry_reference:
			frappe.db.set_value('Payment Entry', d.payment_entry, 'payment_entry_closed', 1)

		# mode_of_payment = account_paid_from = account_paid_to = None
		# paid_amount = received_amount = 0.0
		# for d in self.mode_of_payment:
		# 	default_account = frappe.get_value('Mode of Payment Account', {'parent': d.mode_of_payment}, 'default_account')
		# 	if frappe.db.exists("Branch Cash Accounts Child", {"cash_accounts": default_account}):
		# 		account_paid_from = default_account
		# 		paid_amount = received_amount = d.amount
		# 		mode_of_payment = d.mode_of_payment
		# 		break

		mode_of_payment = account_paid_from = account_paid_to = None
		cash_receive_amount = received_amount = 0.0
		for d in self.mode_of_payment:
			default_account = frappe.get_value('Mode of Payment Account', {'parent': d.mode_of_payment}, 'default_account')
			if frappe.db.exists("Branch Cash Accounts Child", {"cash_accounts": default_account}):
				account_paid_from = default_account
				cash_receive_amount = cash_receive_amount = d.amount
				mode_of_payment = d.mode_of_payment
				break
		



		if account_paid_from:
			account_paid_to = frappe.get_value('Branch Cash Accounts Child', {"cash_accounts": default_account}, 'parent')

		if not (account_paid_from or account_paid_to):
			frappe.throw('Not Accounts Set for Account paid from or Account paid to')

		pe = frappe.new_doc("Payment Entry")
		pe.payment_type = 'Internal Transfer'
		pe.posting_date = nowdate()
		pe.mode_of_payment = mode_of_payment
		pe.paid_from = account_paid_from
		pe.paid_to = account_paid_to
		pe.paid_from_account_currency = get_account_currency(account_paid_from)
		pe.paid_to_account_currency = get_account_currency(account_paid_to)
		pe.paid_amount = cash_receive_amount
		pe.received_amount = cash_receive_amount
		pe.receipts_voucher_numbers = self.name
		pe.paid_from_account_balance = get_balance_on(account_paid_from, nowdate())
		pe.paid_to_account_balance = get_balance_on(account_paid_to, nowdate())
		pe.submit()

		self.cash_transfer_payment_entry = pe.name

	# def before_cancel(self):
		# frappe.throw("Can't cancel because of Sales Invoice and payment Entries closed with Document")
		# for d in self.sales_invoice_reference:
		# 	frappe.db.set_value('Sales Invoice', d.sales_invoice, 'sales_invoice_closed', 0)
		#
		# for d in self.payment_entry_reference:
		# 	frappe.db.set_value('Payment Entry', d.payment_entry, 'payment_entry_closed', 0)


@frappe.whitelist()
def fetch_invoices_payments(date, pos_profile):
	sales_invoices_data = frappe.get_all('Sales Invoice', {
		'posting_date': date, 'pos_profile': pos_profile, 'cash_receive_amount': ['>', 0],
		'docstatus': 1, 'status': 'Paid', 'cash_entry': 'Cash', 'sales_invoice_closed': 0
	}, ['name', 'cash_receive_amount'])

	mode_of_payments = frappe.get_all('POS Payment Method', {'parent':  pos_profile}, ['mode_of_payment'])
	mode_of_payment = None

	if mode_of_payments:
		for mop in mode_of_payments:
			if frappe.db.exists('Mode of Payment', {"name": mop.mode_of_payment, "type": "Cash"}):
				mode_of_payment = mop.mode_of_payment
				break

	if not mode_of_payment:
		frappe.throw(cstr('No valid Cash Mode of Payment linked with this POS'))

	payment_entries_data = frappe.get_all('Payment Entry', {
		'posting_date': date, 'mode_of_payment': mode_of_payment,
		'docstatus': 1, 'payment_type': 'Receive', 'payment_entry_closed': 0
	}, ['name', 'paid_amount', 'mode_of_payment'])

	# frappe.msgprint(cstr(payment_entries_data))
	# total_sales_invoice_amount = flt(sum([d.paid_amount for d in sales_invoices_data]))
	total_sales_invoice_amount = flt(sum([d.cash_receive_amount for d in sales_invoices_data]))
	total_payment_entry_amount = flt(sum([d.paid_amount for d in payment_entries_data]))
	# total_received_amount = flt(total_sales_invoice_amount + total_payment_entry_amount)

	mode_of_payments = frappe._dict()
	for d in sales_invoices_data:
		inv_mops = frappe.get_all('Sales Invoice Payment', {'parent': d.name}, ['mode_of_payment', 'amount'])
		d.inv_mops = cstr(inv_mops)
		for inv_mop in inv_mops:
			mode_of_payments.setdefault(inv_mop.get('mode_of_payment'), 0.0)
			mode_of_payments[inv_mop.get('mode_of_payment')] += inv_mop.get('amount')

	for pe_mop in payment_entries_data:
		mode_of_payments.setdefault(pe_mop.get('mode_of_payment'), 0.0)
		mode_of_payments[pe_mop.get('mode_of_payment')] += pe_mop.get('paid_amount')
		# frappe.msgprint(cstr(pe_mop))

	return {
		'invoices': sales_invoices_data, 'payments': payment_entries_data,
		'total_sales_invoice_amount': total_sales_invoice_amount,
		'total_payment_entry_amount': total_payment_entry_amount,
		# 'total_received_amount': total_received_amount,
		'mode_of_payments': mode_of_payments
	}


def cancellation_restriction_payment_entry(self, method):
	if self.payment_entry_closed:
		frappe.throw('Cannot cancel Payment Entry for Cash Received')

	if frappe.db.exists('Ava Cash Collection', self.receipts_voucher_numbers):
		frappe.throw('Cannot cancel Payment Entry for Internal Transfer of Cash')

def cancellation_restriction_sales_invoice(self, method):
	if self.sales_invoice_closed:
		frappe.throw('Cannot cancel Sales Invoice for Cash Received')
