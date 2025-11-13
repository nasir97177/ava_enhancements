# Copyright (c) 2022, Furqan Asghar and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.custom.doctype.custom_field.custom_field import create_custom_field
from frappe.model.document import Document


class AvaEcommerceSettings(Document):
	def validate(self):
		self.validate_settings()
		self.create_delete_custom_fields()

	def create_delete_custom_fields(self):
		if self.enable_woocommerce_sync:
			custom_fields = {}
			# create
			for doctype in ["Customer", "Sales Order"]:
				df = dict(fieldname='woocommerce_id', label='Woocommerce ID', fieldtype='Data', read_only=1, print_hide=1)
				create_custom_field(doctype, df)

				df = dict(fieldname='woo_col_brk', label='', fieldtype='Column Break', insert_after='woocommerce_id', read_only=1, print_hide=1)
				create_custom_field(doctype, df)

				df = dict(fieldname='woocommerce_link', label='Woocommerce Link', fieldtype='Data', insert_after='woo_col_brk', read_only=1, print_hide=1)
				create_custom_field(doctype, df)

			delivery_slot = dict(fieldname='delivery_slot', label='Delivery Slot', fieldtype='Select', options='\nMorning\nEvening', insert_after='delivery_date', read_only=1, print_hide=1)
			create_custom_field("Sales Order", delivery_slot)

			df = dict(fieldname='woocommerce_payment_method', label='Woocommerce Payment Method', insert_after='woocommerce_link', fieldtype='Data', read_only=1, print_hide=1)
			create_custom_field("Sales Order", df)

	def validate_settings(self):
		if self.enable_woocommerce_sync:
			if not self.woocommerce_server_url:
				frappe.throw(_("Please enter Woocommerce Server URL"))

			if not self.api_consumer_key:
				frappe.throw(_("Please enter API Consumer Key"))

			if not self.api_consumer_secret:
				frappe.throw(_("Please enter API Consumer Secret"))
