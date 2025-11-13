# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "ava_enhancements"
app_title = "Ava Enhancements"
app_publisher = "Furqan Asghar"
app_description = "Ava Water customization and additional features for ERPNext"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "furqan.asghar@ava-water.com, furqan.79000@gmail.com"
app_license = "MIT"


# Document Events
doc_events = {
	"Sales Invoice": {
		"validate": [
			"ava_enhancements.main.is_payment_cash_customer"
		],
		"before_cancel": [
			"ava_enhancements.ava_enhancements.doctype.ava_cash_collection.ava_cash_collection.cancellation_restriction_sales_invoice",
		]
	},
	"Address": {
		"after_insert": [
			"ava_enhancements.main.update_territory_in_customer"
		]
	},
	"Asset": {
		"on_update_after_submit": [
			"ava_enhancements.asset_overrides.on_update_asset"
		]
	},
	"Sales Order": {
		"on_change": [
			"ava_enhancements.ava_woocommerce_connection.woorder_status_change"
		],
		"on_cancel": [
			"ava_enhancements.main.sales_order_cancel_validation",
		]
	},
	"Payment Entry": {
		"before_cancel": [
			"ava_enhancements.ava_enhancements.doctype.ava_cash_collection.ava_cash_collection.cancellation_restriction_payment_entry",
		]
	},
	# "Stock Entry": {
	# 	"validate": [
	# 		"ava_enhancements.main.validate_custom_warehouse_permission"
	# 	]
	# }
}

# include js in doctype views
doctype_js = {
	"Address" : "public/js/address.js",
	"Customer" : "public/js/customer.js",
	"Territory" : "public/js/territory.js",
	"Sales Order" : "public/js/sales_order.js",
	"Asset" : "public/js/asset.js",
	# "Stock Entry" : "public/js/stock_entry.js",
	}

# Scheduled Tasks
scheduler_events = {
	# "*/5 * * * *" every 5 min job to fetch salla orders

	"cron": {
		"*/5 * * * *": [
			"ava_enhancements.ava_woocommerce_connection.woorders_background_job",
			"ava_enhancements.ava_salla_connection.salla_orders_background_job"
		]
	},
	# "daily": [
	# 	"ava_enhancements.ava_enhancements.doctype.ava_bulk_cancel.ava_bulk_cancel.cancel_all_bg",
	# ],
}

fixtures = [
	{
		"dt": "Print Format",
		"filters": [["name", "in", ["Ava Cash Collection"]]]
	}
	# {"dt": "Custom Field", "filters": [
	# 	[
	# 		"dt", "in", ["Address", "Customer", "Customer Branch CT", "Territory", "Item", "Sales Order", "Sales Order Item", "Sales Invoice", "Sales Invoice Item", "Delivery Note", "Delivery Note Item"]
	# 	]
	# ]},
	# # 'Ava Enhancements Settings'
]
# Asset Overrides
from erpnext.assets.doctype.asset.asset import Asset as _Asset
from erpnext.assets.doctype.asset_value_adjustment.asset_value_adjustment import AssetValueAdjustment as _AssetValueAdjustment
from erpnext.assets.doctype.asset_repair.asset_repair import AssetRepair as _AssetRepair
from erpnext.assets.doctype.asset import depreciation as _depreciation
from ava_enhancements.asset_overrides import (
	ava_get_status_asset_py as _ava_get_status_asset_py,
	ava_on_cancel_adjustment_py as _ava_on_cancel_adjustment_py,
	ava_get_cwip_account_asset_py as _ava_get_cwip_account_asset_py,
	ava_set_missing_values_asset_py as _ava_set_missing_values_asset_py,
	ava_get_fixed_asset_account_asset_py as _ava_get_fixed_asset_account_asset_py,
	ava_get_gl_entries_for_asset_repair_py as _ava_get_gl_entries_for_asset_repair_py,
	ava_prepare_depreciation_data_asset_py as _ava_prepare_depreciation_data_asset_py,
	ava_make_depreciation_entry_depreciation_py as _ava_make_depreciation_entry_depreciation_py,
	ava_post_depreciation_entries_depreciation_py as _ava_post_depreciation_entries_depreciation_py,
	ava_cancel_asset_value_adjustment_entry_adjustment_py as _ava_cancel_asset_value_adjustment_entry_adjustment_py,
	ava_validate_expected_value_after_useful_life_asset_py as _ava_validate_expected_value_after_useful_life_asset_py,
	ava_make_depreciation_entry_for_asset_value_adjustment_py as _ava_make_depreciation_entry_for_asset_value_adjustment_py,
)

from erpnext.stock.doctype.delivery_note import delivery_note as _delivery_note
from ava_enhancements.delivery_note_overrides import ava_make_sales_invoice_delivery_note_py as _ava_make_sales_invoice_delivery_note_py
_delivery_note.make_sales_invoice = _ava_make_sales_invoice_delivery_note_py

# depreciation account customizations
_Asset.get_status = _ava_get_status_asset_py
_Asset.get_cwip_account = _ava_get_cwip_account_asset_py
_Asset.set_missing_values = _ava_set_missing_values_asset_py
_Asset.get_fixed_asset_account = _ava_get_fixed_asset_account_asset_py
_Asset.prepare_depreciation_data = _ava_prepare_depreciation_data_asset_py
_Asset.validate_expected_value_after_useful_life = _ava_validate_expected_value_after_useful_life_asset_py
_AssetRepair.get_gl_entries = _ava_get_gl_entries_for_asset_repair_py
_depreciation.make_depreciation_entry = _ava_make_depreciation_entry_depreciation_py
_depreciation.post_depreciation_entries = _ava_post_depreciation_entries_depreciation_py
_AssetValueAdjustment.on_cancel = _ava_on_cancel_adjustment_py
_AssetValueAdjustment.make_depreciation_entry = _ava_make_depreciation_entry_for_asset_value_adjustment_py
_AssetValueAdjustment.cancel_asset_value_adjustment_entry = _ava_cancel_asset_value_adjustment_entry_adjustment_py

override_whitelisted_methods = {
	"erpnext.assets.doctype.asset.asset.make_journal_entry": "ava_enhancements.asset_overrides.ava_make_journal_entry_asset_py",
	"erpnext.assets.doctype.asset.depreciation.make_depreciation_entry": "ava_enhancements.asset_overrides.ava_make_depreciation_entry_depreciation_py",
	"erpnext.selling.doctype.sales_order.sales_order.make_sales_invoice":  "ava_enhancements.sales_order_overrides.ava_make_sales_invoice_sales_order_py",
	"erpnext.stock.doctype.delivery_note.delivery_note.make_sales_invoice":  "ava_enhancements.delivery_note_overrides.ava_make_sales_invoice_delivery_note_py"
}

# # depreciation methods customizations
# _Asset.get_depreciation_rate = _get_depreciation_rate
# _Asset.get_depreciation_amount = _get_depreciation_amount
# _Asset.prepare_depreciation_data = _prepare_depreciation_data

#
# override_whitelisted_methods = {
# 	"erpnext.crm.doctype.lead.lead.make_customer": "ava_enhancements.main.make_customer_from_lead",
# 	"erpnext.crm.doctype.lead.lead.make_opportunity": "ava_enhancements.main.make_opportunity_from_lead"
# }
#
# from erpnext.crm.doctype.lead.lead import Lead
# from ava_enhancements.main import create_contact
#
# Lead.create_contact = create_contact
#
# override_whitelisted_methods = {
# 	"erpnext.crm.doctype.lead.lead.make_customer": "ava_enhancements.main.make_customer_from_lead",
# 	"erpnext.crm.doctype.lead.lead.make_opportunity": "ava_enhancements.main.make_opportunity_from_lead"
# }

override_whitelisted_methods = {
    "frappe.core.doctype.file.file.delete": "ava_enhancements.api.prevent_file_delete"
}

