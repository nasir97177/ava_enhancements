# Copyright (c) 2022, Furqan Asghar and contributors
# For license information, please see license.txt

import frappe
from frappe import _, scrub
from frappe.utils import add_days, add_to_date, flt, getdate, cstr, time_diff_in_hours
from six import iteritems

from erpnext.accounts.utils import get_fiscal_year


def execute(filters=None):
	return Analytics(filters).run()


class Analytics(object):
	def __init__(self, filters=None):
		self.filters = frappe._dict(filters or {})
		self.date_field = 'transaction_date'
		self.months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

	def run(self):
		self.get_columns()
		self.get_data()
		self.get_chart_data()

		# Skipping total row for tree-view reports
		skip_total_row = 0

		if self.filters.tree_type in ["Territory", "Warehouse", "Customer Group" ]:
			skip_total_row = 1

		# frappe.msgprint(cstr(self.data))
		return self.columns, self.data, None, self.chart
		# return self.columns, self.data, None, self.chart, None, skip_total_row

	def get_columns(self):
		self.columns = [
			{
				"label": _(self.filters.tree_type),
				"options": self.filters.tree_type,
				"fieldname": "entity",
				"fieldtype": "Link",
				"width": 140
			},
			{
				"label": _("Total Orders"),
				"fieldname": "so_total",
				"fieldtype": "Int",
				"width": 105
			},
			{
				"label": _("Total Qty"),
				"fieldname": "total_qty",
				"fieldtype": "Float",
				"width": 105
			},
			{
				"label": _("Total Value"),
				"fieldname": "base_net_total",
				"fieldtype": "Float",
				"width": 105
			},
			{
				"label": _("To Deliver and Bill Orders"),
				"fieldname": "so_undelivered",
				"fieldtype": "Int",
				"width": 180,
				"service_level_count": 1,
				"hidden": 1
			},
			{
				"label": _("To Deliver"),
				"fieldname": "so_to_deliver",
				"fieldtype": "Int",
				"width": 90,
				"service_level_count": 1,
				"hidden": 1
			},
			{
				"label": _("To Bill"),
				"fieldname": "so_to_bill",
				"fieldtype": "Int",
				"width": 90,
				"service_level_count": 1,
				"hidden": 1
			},
			{
				"label": _("Cancelled/Closed"),
				"fieldname": "cancelled_closed",
				"fieldtype": "Int",
				"width": 135,
				"service_level_count": 1,
				"hidden": 1
			},
			{
				"label": _("Completed Orders"),
				"fieldname": "so_delivered",
				"fieldtype": "Int",
				"width": 145,
				# "service_level_count": 1,
			},
			{
				"label": _("To Deliver and Bill Orders Qty"),
				"fieldname": "so_undelivered_qty",
				"fieldtype": "Int",
				"width": 180,
				"service_level_qty": 1,
				"hidden": 1
			},
			{
				"label": _("Completed Orders Qty"),
				"fieldname": "so_delivered_qty",
				"fieldtype": "Int",
				"width": 180,
				"service_level_qty": 1,
				"hidden": 1
			},
			{
				"label": _("To Bill Qty"),
				"fieldname": "so_to_bill_qty",
				"fieldtype": "Int",
				"width": 180,
				"service_level_qty": 1,
				"hidden": 1
			},
			{
				"label": _("Cancelled/Closed Qty"),
				"fieldname": "cancelled_closed_qty",
				"fieldtype": "Int",
				"width": 180,
				"service_level_qty": 1,
				"hidden": 1
			},
			{
				"label": _("To Deliver Qty"),
				"fieldname": "so_to_deliver_qty",
				"fieldtype": "Int",
				"width": 180,
				"service_level_qty": 1,
				"hidden": 1
			},
			{
				"label": _("To Deliver and Bill Orders Value"),
				"fieldname": "so_undelivered_val",
				"fieldtype": "Int",
				"width": 180,
				"service_level_val": 1,
				"hidden": 1
			},
			{
				"label": _("Completed Orders Value"),
				"fieldname": "so_delivered_val",
				"fieldtype": "Int",
				"width": 180,
				"service_level_val": 1,
				"hidden": 1
			},
			{
				"label": _("To Bill Value"),
				"fieldname": "so_to_bill_val",
				"fieldtype": "Int",
				"width": 180,
				"service_level_val": 1,
				"hidden": 1
			},
			{
				"label": _("Cancelled/Closed Value"),
				"fieldname": "cancelled_closed_val",
				"fieldtype": "Int",
				"width": 180,
				"service_level_val": 1,
				"hidden": 1
			},
			{
				"label": _("To Deliver Value"),
				"fieldname": "so_to_deliver_val",
				"fieldtype": "Int",
				"width": 180,
				"service_level_val": 1,
				"hidden": 1
			},
			{
				"label": _("Delivered 24 Hrs"),
				"fieldname": "so_delvr_24_hrs",
				"fieldtype": "Int",
				"width": 135,
				"service_level_count": 1,
				"hidden": 1
			},
			{
				"label": _("Delivered 48 Hrs"),
				"fieldname": "so_delvr_48_hrs",
				"fieldtype": "Int",
				"width": 135,
				"service_level_count": 1,
				"hidden": 1
			},
			{
				"label": _("Delivered after 48 Hrs"),
				"fieldname": "so_delvr_post_48_hrs",
				"fieldtype": "Int",
				"width": 170,
				"service_level_count": 1,
				"hidden": 1
			},
			{
				"label": _("% Delivered 24 Hrs"),
				"fieldname": "so_delvr_24_hrs_perc",
				"fieldtype": "Percentage",
				"width": 150,
				# "hidden": 1
			},
			{
				"label": _("% Delivered 48 Hrs"),
				"fieldname": "so_delvr_48_hrs_perc",
				"fieldtype": "Percentage",
				"width": 150,
				# "hidden": 1
			},
			{
				"label": _("% Delivered after 48 Hrs"),
				"fieldname": "so_delvr_post_48_hrs_perc",
				"fieldtype": "Percentage",
				"width": 190,
				# "hidden": 1
			}
		]

	def get_data(self):
		if self.filters.tree_type in ["Territory", "Warehouse", "Customer Group"]:
			self.get_sales_transactions_based_on_customer_or_territory_group()
			self.get_rows_by_group()

	def get_sales_transactions_based_on_customer_or_territory_group(self):
		if self.filters.tree_type == 'Customer Group':
			entity_field = 'customer_group as entity'
		elif self.filters.tree_type == 'Warehouse':
			entity_field = 'set_warehouse as entity'
		else:
			entity_field = "territory as entity"

		filters = {
			'docstatus': ['>', 0],
			'company': self.filters.company,
			self.date_field: ('between', [self.filters.from_date, self.filters.to_date])
		}

		if self.filters.territory:
			filters.update({'territory': self.filters.territory})

		if self.filters.warehouse:
			filters.update({'set_warehouse': self.filters.warehouse})

		if self.filters.customer_group:
			filters.update({'customer_group': self.filters.customer_group})

		self.entries = frappe.get_all('Sales Order',
			fields=[entity_field, 'status', 'name', 'base_net_total', 'total_qty', self.date_field, 'modified'],
			filters=filters
		)
		# frappe.msgprint(cstr(len(self.entries)))

		self.get_groups()

	def get_rows_by_group(self):
		self.get_entity_data()
		out = []
		count = 0
		for d in reversed(self.group_entries):

			row = {
				"entity": d.name,
				"indent": self.depth_map.get(d.name)
			}
			_so_delvr_post_48_hrs = _so_delvr_48_hrs = _so_delvr_24_hrs = _so_to_bill = _cancelled_closed = \
				_so_undelivered_qty = _so_delivered_qty = _so_to_bill_qty = _cancelled_closed_qty = _so_to_deliver_qty =\
				_so_undelivered_val = _so_delivered_val = _so_to_bill_val = _cancelled_closed_val = _so_to_deliver_val =\
				_so_to_deliver = _so_delivered = _so_undelivered = _base_net_total = _total_qty = _so_total = 0

			total_qty = flt(self.entity_data.get(d.name, {}).get('total_qty', 0.0))

			so_total = flt(self.entity_data.get(d.name, {}).get('so_total', 0.0))
			base_net_total = flt(self.entity_data.get(d.name, {}).get('base_net_total', 0.0))

			so_to_deliver = flt(self.entity_data.get(d.name, {}).get('so_to_deliver', 0.0))
			so_undelivered = flt(self.entity_data.get(d.name, {}).get('so_undelivered', 0.0))
			so_to_bill = flt(self.entity_data.get(d.name, {}).get('so_to_bill', 0.0))
			cancelled_closed = flt(self.entity_data.get(d.name, {}).get('cancelled_closed', 0.0))
			so_delivered = flt(self.entity_data.get(d.name, {}).get('so_delivered', 0.0))

			so_to_deliver_qty = flt(self.entity_data.get(d.name, {}).get('so_to_deliver_qty', 0.0))
			so_undelivered_qty = flt(self.entity_data.get(d.name, {}).get('so_undelivered_qty', 0.0))
			so_to_bill_qty = flt(self.entity_data.get(d.name, {}).get('so_to_bill_qty', 0.0))
			cancelled_closed_qty = flt(self.entity_data.get(d.name, {}).get('cancelled_closed_qty', 0.0))
			so_delivered_qty = flt(self.entity_data.get(d.name, {}).get('so_delivered_qty', 0.0))

			so_to_deliver_val = flt(self.entity_data.get(d.name, {}).get('so_to_deliver_val', 0.0))
			so_undelivered_val = flt(self.entity_data.get(d.name, {}).get('so_undelivered_val', 0.0))
			so_to_bill_val = flt(self.entity_data.get(d.name, {}).get('so_to_bill_val', 0.0))
			cancelled_closed_val = flt(self.entity_data.get(d.name, {}).get('cancelled_closed_val', 0.0))
			so_delivered_val = flt(self.entity_data.get(d.name, {}).get('so_delivered_val', 0.0))

			so_delvr_24_hrs = flt(self.entity_data.get(d.name, {}).get('so_delvr_24_hrs', 0.0))
			so_delvr_48_hrs = flt(self.entity_data.get(d.name, {}).get('so_delvr_48_hrs', 0.0))
			so_delvr_post_48_hrs = flt(self.entity_data.get(d.name, {}).get('so_delvr_post_48_hrs', 0.0))

			if d.parent and (self.filters.tree_type != "Order Type" or d.parent == "Order Types"):
				period_value = {
					'so_total': 0.0, 'total_qty': 0.0, 'base_net_total': 0.0, 'so_undelivered': 0.0,
					'so_to_deliver': 0.0, 'so_to_bill': 0.0, 'cancelled_closed': 0.0, 'so_delivered': 0.0,
					'so_undelivered_qty': 0, 'so_delivered_qty': 0, 'so_to_bill_qty': 0, 'cancelled_closed_qty': 0, 'so_to_deliver_qty': 0,
					'so_undelivered_val': 0, 'so_delivered_val': 0, 'so_to_bill_val': 0, 'cancelled_closed_val': 0, 'so_to_deliver_val': 0,
					'so_delvr_24_hrs': 0.0, 'so_delvr_48_hrs': 0.0, 'so_delvr_post_48_hrs': 0.0
				}
				self.entity_data.setdefault(d.parent, period_value)

				self.entity_data[d.parent]['so_total'] += so_total
				self.entity_data[d.parent]['total_qty'] += total_qty
				self.entity_data[d.parent]['base_net_total'] += base_net_total

				self.entity_data[d.parent]['so_undelivered'] += so_undelivered
				self.entity_data[d.parent]['so_to_deliver'] += so_to_deliver
				self.entity_data[d.parent]['so_to_bill'] += so_to_bill
				self.entity_data[d.parent]['cancelled_closed'] += cancelled_closed
				self.entity_data[d.parent]['so_delivered'] += so_delivered

				self.entity_data[d.parent]['so_undelivered_qty'] += so_undelivered_qty
				self.entity_data[d.parent]['so_to_deliver_qty'] += so_to_deliver_qty
				self.entity_data[d.parent]['so_to_bill_qty'] += so_to_bill_qty
				self.entity_data[d.parent]['cancelled_closed_qty'] += cancelled_closed_qty
				self.entity_data[d.parent]['so_delivered_qty'] += so_delivered_qty

				self.entity_data[d.parent]['so_undelivered_val'] += so_undelivered_val
				self.entity_data[d.parent]['so_to_deliver_val'] += so_to_deliver_val
				self.entity_data[d.parent]['so_to_bill_val'] += so_to_bill_val
				self.entity_data[d.parent]['cancelled_closed_val'] += cancelled_closed_val
				self.entity_data[d.parent]['so_delivered_val'] += so_delivered_val

				self.entity_data[d.parent]['so_delvr_24_hrs'] += so_delvr_24_hrs
				self.entity_data[d.parent]['so_delvr_48_hrs'] += so_delvr_48_hrs
				self.entity_data[d.parent]['so_delvr_post_48_hrs'] += so_delvr_post_48_hrs

			_so_total += so_total
			_total_qty += total_qty
			_base_net_total += base_net_total

			_so_undelivered += so_undelivered
			_so_to_deliver += so_to_deliver
			_so_to_bill += so_to_bill
			_cancelled_closed += cancelled_closed
			_so_delivered += so_delivered

			_so_undelivered_qty += so_undelivered_qty
			_so_to_deliver_qty += so_to_deliver_qty
			_so_to_bill_qty += so_to_bill_qty
			_cancelled_closed_qty += cancelled_closed_qty
			_so_delivered_qty += so_delivered_qty

			_so_undelivered_val += so_undelivered_val
			_so_to_deliver_val += so_to_deliver_val
			_so_to_bill_val += so_to_bill_val
			_cancelled_closed_val += cancelled_closed_val
			_so_delivered_val += so_delivered_val

			_so_delvr_24_hrs += so_delvr_24_hrs
			_so_delvr_48_hrs += so_delvr_48_hrs
			_so_delvr_post_48_hrs += so_delvr_post_48_hrs

			row["so_total"] = _so_total
			row["total_qty"] = _total_qty
			row["base_net_total"] = _base_net_total

			row["so_undelivered"] = _so_undelivered
			row["so_to_deliver"] = _so_to_deliver
			row["so_to_bill"] = _so_to_bill
			row["cancelled_closed"] = _cancelled_closed
			row["so_delivered"] = _so_delivered

			row["so_undelivered_qty"] = _so_undelivered_qty
			row["so_to_deliver_qty"] = _so_to_deliver_qty
			row["so_to_bill_qty"] = _so_to_bill_qty
			row["cancelled_closed_qty"] = _cancelled_closed_qty
			row["so_delivered_qty"] = _so_delivered_qty

			row["so_undelivered_val"] = _so_undelivered_val
			row["so_to_deliver_val"] = _so_to_deliver_val
			row["so_to_bill_val"] = _so_to_bill_val
			row["cancelled_closed_val"] = _cancelled_closed_val
			row["so_delivered_val"] = _so_delivered_val

			row["so_delvr_24_hrs"] = _so_delvr_24_hrs
			row["so_delvr_48_hrs"] = _so_delvr_48_hrs
			row["so_delvr_post_48_hrs"] = _so_delvr_post_48_hrs
			row["so_delvr_24_hrs_perc"] = flt((_so_delvr_24_hrs/_so_delivered) * 100, 2) if _so_delivered > 0 else None
			row["so_delvr_48_hrs_perc"] = flt((_so_delvr_48_hrs/_so_delivered) * 100, 2) if _so_delivered > 0 else None
			row["so_delvr_post_48_hrs_perc"] = flt((_so_delvr_post_48_hrs/_so_delivered) * 100, 2) if _so_delivered > 0 else None
			if row.get('so_total') > 0:
				out = [row] + out

		self.data = out

	def get_entity_data(self):
		self.entity_data = frappe._dict()

		for d in self.entries:
			period_value = {
				'so_so_status_dict': [], 'so_total': 0, 'total_qty': 0.0, 'base_net_total': 0.0,
				'so_undelivered': 0, 'so_delivered': 0, 'so_to_bill': 0, 'cancelled_closed': 0, 'so_to_deliver': 0,
				'so_undelivered_qty': 0, 'so_delivered_qty': 0, 'so_to_bill_qty': 0, 'cancelled_closed_qty': 0, 'so_to_deliver_qty': 0,
				'so_undelivered_val': 0, 'so_delivered_val': 0, 'so_to_bill_val': 0, 'cancelled_closed_val': 0, 'so_to_deliver_val': 0,
				'so_delvr_24_hrs': 0, 'so_delvr_48_hrs': 0, 'so_delvr_post_48_hrs': 0
			}
			self.entity_data.setdefault(d.entity, period_value)

			self.entity_data[d.entity]['so_so_status_dict'].append({d.get('name'): d.get('status')})
			self.entity_data[d.entity]['so_total'] += 1
			self.entity_data[d.entity]['total_qty'] += flt(d.total_qty)
			self.entity_data[d.entity]['base_net_total'] += flt(d.base_net_total)

			self.entity_data[d.entity]['so_undelivered'] += 1 if d.get('status') == 'To Deliver and Bill' else 0
			self.entity_data[d.entity]['so_to_deliver'] += 1 if d.get('status') == 'To Deliver' else 0
			self.entity_data[d.entity]['so_to_bill'] += 1 if d.get('status') == 'To Bill' else 0
			self.entity_data[d.entity]['cancelled_closed'] += 1 if d.get('status') in ['Cancelled', 'Closed'] else 0
			self.entity_data[d.entity]['so_delivered'] += 1 if d.get('status') == 'Completed' else 0

			self.entity_data[d.entity]['so_undelivered_qty'] += flt(d.total_qty) if d.get('status') == 'To Deliver and Bill' else 0
			self.entity_data[d.entity]['so_delivered_qty'] += flt(d.total_qty) if d.get('status') == 'To Deliver' else 0
			self.entity_data[d.entity]['so_to_bill_qty'] += flt(d.total_qty) if d.get('status') == 'To Bill' else 0
			self.entity_data[d.entity]['cancelled_closed_qty'] += flt(d.total_qty) if d.get('status') in ['Cancelled', 'Closed'] else 0
			self.entity_data[d.entity]['so_to_deliver_qty'] += flt(d.total_qty) if d.get('status') == 'Completed' else 0

			self.entity_data[d.entity]['so_undelivered_val'] += flt(d.base_net_total) if d.get('status') == 'To Deliver and Bill' else 0
			self.entity_data[d.entity]['so_delivered_val'] += flt(d.base_net_total) if d.get('status') == 'To Deliver' else 0
			self.entity_data[d.entity]['so_to_bill_val'] += flt(d.base_net_total) if d.get('status') == 'To Bill' else 0
			self.entity_data[d.entity]['cancelled_closed_val'] += flt(d.base_net_total) if d.get('status') in ['Cancelled', 'Closed'] else 0
			self.entity_data[d.entity]['so_to_deliver_val'] += flt(d.base_net_total) if d.get('status') == 'Completed' else 0

			self.entity_data[d.entity]['so_delvr_24_hrs'] += order_delivery_duration_checker(d, 'so_delvr_24_hrs')
			self.entity_data[d.entity]['so_delvr_48_hrs'] += order_delivery_duration_checker(d, 'so_delvr_48_hrs')
			self.entity_data[d.entity]['so_delvr_post_48_hrs'] += order_delivery_duration_checker(d, 'so_delvr_post_48_hrs')
			# frappe.msgprint(str(self.entity_data[d.entity]['so_delvr_24_hrs']) + ' : ' + str(self.entity_data[d.entity]['so_delvr_48_hrs']) + ' : ' + str(self.entity_data[d.entity]['so_delvr_post_48_hrs']))

	def get_groups(self):
		root = cond = ''
		if self.filters.tree_type == "Territory":
			parent = 'parent_territory'
			root = 'KSA'
		if self.filters.tree_type == "Warehouse":
			parent = 'parent_warehouse'
			root = '5- Finished Goods  - ABNA'
		if self.filters.tree_type == "Customer Group":
			parent = 'parent_customer_group'

		if root and self.filters.tree_type in ['Territory', 'Warehouse']:
			lft, rgt = frappe.get_value(self.filters.tree_type, root, ['lft', 'rgt'])
			cond += 'and lft >= {0} and rgt <= {1}'.format(lft, rgt)

		self.group_entries = frappe.db.sql("""select name, lft, rgt, {parent} as parent from `tab{tree}` where 1=1 {cond} order by lft""".format(tree=self.filters.tree_type, parent=parent, cond=cond), as_dict=1, debug=True)  # where lft >= 18 and rgt <= 169

		# frappe.msgprint(cstr(self.group_entries))
		self.depth_map = frappe._dict()
		for d in self.group_entries:
			pass
			if d.parent and (d.parent not in ['All Territories', '1 - Logistics  - ABNA']):
				self.depth_map.setdefault(d.name, self.depth_map.get(d.parent) + 1)
			else:
				self.depth_map.setdefault(d.name, 0)
		# frappe.msgprint(cstr(self.depth_map))

	def get_chart_data(self):
		if self.filters.charts_based_on == 'Count':
			# frappe.msgprint('service')
			title = 'Orders count by status'
			data = []
			datasets = []
			labels = [{d.get("fieldname"): d.get("label")} for d in self.columns if d.get('service_level_count')]
			# frappe.msgprint(cstr(labels))
			for d in labels:
				if self.data[0]:
					# frappe.msgprint(cstr(self.data[0].get(list(d.keys())[0])) + ' : ' + list(d.keys())[0])
					data.append(self.data[0].get(list(d.keys())[0]))

			labels = [list(d.values())[0] for d in labels]
			datasets.append({'name': 'Service Level Chart', 'values': data})

		if self.filters.charts_based_on == 'Volume':
			title = 'Orders Volume by status'
			data = []
			datasets = []
			labels = [{d.get("fieldname"): d.get("label")} for d in self.columns if d.get('service_level_qty')]
			# frappe.msgprint(cstr(labels))
			for d in labels:
				if self.data[0]:
					# frappe.msgprint(cstr(self.data[0].get(list(d.keys())[0])) + ' : ' + list(d.keys())[0])
					data.append(self.data[0].get(list(d.keys())[0]))

			labels = [list(d.values())[0] for d in labels]
			datasets.append({'name': 'Service Level Chart', 'values': data})

		if self.filters.charts_based_on == 'Value':
			title = 'Orders Value by status'
			data = []
			datasets = []
			labels = [{d.get("fieldname"): d.get("label")} for d in self.columns if d.get('service_level_val')]
			# frappe.msgprint(cstr(labels))
			for d in labels:
				if self.data[0]:
					# frappe.msgprint(cstr(self.data[0].get(list(d.keys())[0])) + ' : ' + list(d.keys())[0])
					data.append(self.data[0].get(list(d.keys())[0]))

			labels = [list(d.values())[0] for d in labels]

			datasets.append({'name': 'Service Level Chart', 'values': data})

		self.chart = {
			"title": "Service Level chart: {0}".format(title),
			"data": {
				'labels': labels,
				'datasets': datasets
			},
			"type": "pie",

		}
		# frappe.msgprint(cstr(self.chart))


def order_status_count_checker(status, column):
	counter = 0
	if column == 'so_undelivered':
		if status == 'To Deliver and Bill':
			counter = 1

	if column == 'so_delivered':
		if status == 'Completed':
			counter = 1

	if column == 'so_to_bill':
		if status == 'To Bill':
			counter = 1

	if column == 'cancelled_closed':
		if status in ['Cancelled', 'Closed']:
			counter = 1

	if column == 'so_to_deliver':
		if status == 'To Deliver':
			counter = 1

	return counter


def order_delivery_duration_checker(order_row, column):
	counter = 0
	if order_row.get('status') == 'Completed':
		time_to_deliver = flt(time_diff_in_hours(order_row.get('modified'), order_row.get('transaction_date')))

		if column == 'so_delvr_24_hrs':
			if time_to_deliver <= 24:
				counter = 1
				# frappe.msgprint(cstr(time_to_deliver) + '<< so_delvr_24_hrs >>' + cstr(order_row.get('name')))

		if column == 'so_delvr_48_hrs':
			if 24 < time_to_deliver <= 48:
				counter = 1
				# frappe.msgprint(cstr(time_to_deliver) + '<< so_delvr_48_hrs >>' + cstr(order_row.get('name')))

		if column == 'so_delvr_post_48_hrs':
			if time_to_deliver > 48:
				counter = 1
				# frappe.msgprint(cstr(time_to_deliver) + '<< so_delvr_post_48_hrs >>' + cstr(order_row.get('name')))

	return counter
