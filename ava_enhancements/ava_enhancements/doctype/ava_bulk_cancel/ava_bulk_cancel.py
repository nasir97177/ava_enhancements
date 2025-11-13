# Copyright (c) 2022, Furqan Asghar and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import json


class AvaBulkCancel(Document):
	pass


# @frappe.whitelist()
def cancel_all_bg():
	ava_bulk_cancel_entry = frappe.db.get_value('Ava Enhancements Settings', 'Ava Enhancements Settings', 'ava_bulk_cancel_entry')
	if ava_bulk_cancel_entry:
		doc = frappe.get_doc('Ava Bulk Cancel', ava_bulk_cancel_entry)
		if doc.to_cancel_entries:
			for d in doc.to_cancel_entries:
				if not d.is_cancelled:
					if not frappe.db.exists(doc.doctype_name, {'name': d.link_name, 'docstatus': 2}):
						frappe.get_doc(doc.doctype_name, d.link_name).cancel()
						frappe.db.commit()
					d.is_cancelled = 1

		doc.save()
	# return doc


@frappe.whitelist()
def cancel_all(doctype, docname):
	doc = frappe.get_doc(doctype, docname)
	if doc.to_cancel_entries:
		for d in doc.to_cancel_entries:
			if not d.is_cancelled:
				if not frappe.db.exists(doc.doctype_name, {'name': d.link_name, 'docstatus': 2}):
					frappe.get_doc(doc.doctype_name, d.link_name).cancel()
					frappe.db.commit()
				d.is_cancelled = 1

	doc.save()
	return doc
