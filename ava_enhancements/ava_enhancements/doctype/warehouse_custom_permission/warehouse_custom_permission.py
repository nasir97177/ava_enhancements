# Copyright (c) 2022, Furqan Asghar and contributors
# For license information, please see license.txt

import json
import frappe
from frappe import _
from frappe.utils import cstr
from frappe.model.document import Document


class WarehouseCustomPermission(Document):
	def validate(self):
		self.validate_duplicate()

	def validate_duplicate(self):
		allowed_swh = [swh.warehouse for swh in self.allowed_source_warehouses]
		allowed_twh = [twh.warehouse for twh in self.allowed_target_warehouses]
		allowed_swh_count = {}
		allowed_twh_count = {}
		for swh in allowed_swh:
			allowed_swh_count[swh] = allowed_swh.count(swh)

		repeated_swh = []
		for swh, count in allowed_swh_count.items():
			if count > 1:
				repeated_swh.append(swh)

		for twh in allowed_twh:
			allowed_twh_count[twh] = allowed_twh.count(twh)

		repeated_twh = []
		for twh, count in allowed_twh_count.items():
			if count > 1:
				repeated_twh.append(twh)

		msg = []
		if repeated_swh:
			msg.append(cstr('Please remove repeated Source Warehouse: ' + ', '.join(repeated_swh)))
		if repeated_twh:
			msg.append(cstr('Please remove repeated Target Warehouse: ' + ', '.join(repeated_twh)))

		if msg:
			frappe.throw('<br>'.join(msg))


@frappe.whitelist()
def create_custom_perm(user, row):
	row = frappe._dict(json.loads(row))
	args = dict(
		doctype="User Permission",
		user=user,
		allow='Warehouse',
		for_value=row.warehouse,
		apply_to_all_doctypes=1,
		# applicable_for=applicable_for,
		# hide_descendants=0
	)
	perm_doc = frappe.get_doc(args)
	perm_doc.save()
	frappe.db.set_value(row.doctype, row.name, 'perm_link', perm_doc.name)
	return {'perm': perm_doc.name}


@frappe.whitelist()
def remove_custom_perm(row):
	row = frappe._dict(json.loads(row))
	frappe.db.set_value(row.doctype, row.name, 'perm_link', '')
	frappe.delete_doc('User Permission', row.get('perm_link'))
	return {'success': 1}
