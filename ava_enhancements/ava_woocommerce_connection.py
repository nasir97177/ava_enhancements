# Copyright (c) 2022, Furqan Asghar and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import cstr, today, get_url, flt, cint
from frappe.utils.background_jobs import enqueue
from woocommerce import API
import datetime
from datetime import timedelta
from ava_enhancements.geofencing import (
	get_coverage_area, get_geolocation_for_leaflet
)
from ava_enhancements.main import (
	make_customer, create_customer_address, make_sales_order, make_out_of_fence_order, get_users_by_role
)


@frappe.whitelist()
def get_woorders():
	wc_config = frappe.get_doc("Ava Ecommerce Settings")

	if wc_config.enable_woocommerce_sync:
		consumer_key = wc_config.api_consumer_key
		consumer_secret = wc_config.get_password(fieldname="api_consumer_secret")
		store_url = wc_config.woocommerce_server_url
		wc_api = API(url=store_url, consumer_key=consumer_key, consumer_secret=consumer_secret, timeout=50)
		params = {}
		from_date = (datetime.datetime.now() + timedelta(days=-1)).isoformat()
		params['after'] = from_date

		wooorders = wc_api.get('orders', params=params)
		if wooorders.status_code == 200:
			total_pages = int(wooorders.headers['X-WP-TotalPages'])
			# count = 0
			for page_no in range(1, total_pages+1):
				params['page'] = str(page_no)
				paginated_wooorders = wc_api.get('orders', params=params)
				if paginated_wooorders.status_code == 200:
					paginated_wooorders = paginated_wooorders.json()
					for woorder in paginated_wooorders:
						if not frappe.db.exists({'doctype': 'Sales Order', 'woocommerce_id': woorder.get('id')}):
							# count = count + 1
							if woorder.get('status') in ['processing', 'pending']: # if not deleted Order
								woorder_processor(woorder, wc_api, wc_config)
							# woorder_processor(woorder, wc_api, wc_config)
						else:
							pass
				else:
					error_message = cstr(paginated_wooorders.text)
					frappe.log_error(error_message, "Error: Woocommerce Sales Order Details API Error")
			# # return wooorders.json()
		else:
			error_message = cstr(wooorders.text)
			frappe.log_error(error_message, "Error: Woocommerce Sales Order Details API Error")


@frappe.whitelist()
def woorder_processor(orders_details, wc_api, wc_config):
	'''
		Description: Woocommrce Order Proccessing

			Check customer by phone no. if exist > create/modify customer, create address, create sales Order
				take cust mob no. from Woocommerce and check
					if not any customer with mobile no. then create customer and get customer name
					else get customer name in ERP and if not  set customer_id then set in customer
				check if no address exist with customer and goelocation(catering multiple address for customer)
					if True Create address
				Check and make Sales Order Items list from current Woocommrce Order items ids
					if item_sku exist for order take item
					elif check for promtional item
					else make error log
				if Sales Order Items list exist
					make Sales Order

		param/Input: Woocommrce Order > orders_details (dict)

		return/Output : Customer, Address, Sales Orders (submit) and return so name, Sales Invoivce , Error log
	'''
	try:
		order_id = cstr(orders_details.get('id'))
		order_status = cstr(orders_details.get('status'))
		payment_method = orders_details.get('payment_method')
		payment_method_title = orders_details.get('payment_method_title')
		order_items = orders_details.get('line_items')
		order_time = orders_details.get('date_created')
		customer_id = orders_details.get('customer_id')

		billing_address = orders_details.get('billing')
		customer_mobile = billing_address.get('phone').strip('+').lstrip('0')
		if len(customer_mobile) == 9:
			customer_mobile = '966' + str(customer_mobile)

		customer_email = billing_address.get('email')
		customer_name = billing_address.get('first_name') + ' ' + billing_address.get('last_name')

		order_link = 'https://ava-water.com/wp-admin/post.php?post={0}&action=edit'.format(order_id)

		delivery_date = [d.get('value') for d in orders_details.get('meta_data') if d.get('key') == 'Delivery Date'][0]
		delivery_slot = [d.get('value') for d in orders_details.get('meta_data') if d.get('key') == 'Delivery Slot'][0]
		lpac_latitude = [d.get('value') for d in orders_details.get('meta_data') if d.get('key') == 'lpac_latitude'][0]
		lpac_longitude = [d.get('value') for d in orders_details.get('meta_data') if d.get('key') == 'lpac_longitude'][0]

		customer_location = {"lat": lpac_latitude, "lng": lpac_longitude}

		geolocation = get_geolocation_for_leaflet(customer_location)

		territory_exist, territory_name_or_msg = get_coverage_area(geolocation, wc_config.default_customer_group)

		coupon_code = None
		keep_in_draft = False
		if orders_details.get('coupon_lines'):
			# considering just first coupon in listt
			_coupon_code = orders_details.get('coupon_lines')[0].get('code').upper()
			if frappe.db.exists({'doctype': 'Coupon Code', 'name': _coupon_code}):
				coupon_code = _coupon_code
			else:
				error_message = 'Order sync failed for Payload: {0}'.format(orders_details)
				title = "Error: Woocommerce Sales Order Coupon not found"
				frappe.log_error(error_message, title)
				keep_in_draft = True

		if order_status == 'pending':
			keep_in_draft = True

		if territory_exist:
			territory = territory_name_or_msg
			if customer_mobile:
				if not frappe.db.exists({'doctype':'Customer', 'customer_mobile_number': customer_mobile}):
					# Create customer
					customer_name = make_customer(customer_name, customer_mobile, customer_email=customer_email, woocomm_customer_id=customer_id)

				else:
					existing_cust_data = frappe.db.get_value('Customer', {'customer_mobile_number': customer_mobile}, ['name', 'woocommerce_id'])
					customer_name = existing_cust_data[0]
					if not existing_cust_data[1]:
						frappe.db.set_value('Customer', existing_cust_data[0], {'woocommerce_id': customer_id})

				customer_address = create_customer_address(customer_name, customer_location, geolocation, territory)

				# Check and make Sales Order Items from Woocommerce Order
				items = []
				non_existing_items = ''
				for item in order_items:
					sku = item.get('sku')
					quantity = cint(item.get('quantity'))
					if frappe.db.exists({'doctype': 'Item', 'name': sku}):
						if flt(item.get('total')) > 0:
							items.append({'item_code': sku, 'qty': quantity})

					else:
						item = 'ID: {0}, Item Name: {1}, SKU: {2} '.format(item.get('name'), item.get('name'), sku)
						non_existing_items += '\t' + cstr(item) + '\n'
				if items:
					# Create Sales Order
					_orders_details = orders_details
					so = make_sales_order(customer_name, items, customer_address, coupon_code=coupon_code, wooorder_id=order_id, wooorder_payment_method=payment_method_title, delivery_date=delivery_date, delivery_slot=delivery_slot, woorder_link=order_link, keep_in_draft=keep_in_draft)
					sales_order = so.get('order_id')
					return sales_order

				else:
					message = 'During Woocommerce Orders synchronize an exception occured for Order ID: {0}\nSynchronization time: {1}\nItem(s) with following ID not existed in ERP:\n{2}'
					frappe.throw(message.format(order_id, order_time, non_existing_items))

			else:
				message = 'During Woocommerce Orders  synchronization an exception occured for Order ID: {0}\nSynchronization time: {1}\nCustomer mobile was not in Order'
				message = message.format(order_id, order_time)
				frappe.throw(message)

		else:

			if not frappe.db.exists({'doctype': 'Out of Fence Order', 'order_source': 'Woocommerce', 'customer_mobile': customer_mobile, 'order_id': order_id}):
				make_out_of_fence_order('Woocommerce', order_id, customer_name, customer_mobile, order_time, order_items, geolocation)
	#
	except Exception as e:
		error_message = frappe.get_traceback()+"\n{}".format(str(e)) + '\nOrder sync failed for Payload: {}'.format(orders_details)
		title = "Error: Woocommerce Sales Order synchronization failed"
		error_log = frappe.log_error(error_message, title)
		wc_config = frappe.get_doc("Ava Ecommerce Settings")
		if wc_config.send_error_log_email:
			dev_users = get_users_by_role(wc_config.ecommerce_error_log_reviewer_role)
			salla_order_url = orders_details.get('urls').get('admin')
			error_log_url = get_url("/app/error-log/{0}".format(error_log.name))
			email_body = 'Please check Error Log: {0} for this Woocommerce Order: {1}'.format(error_log_url, salla_order_url)
			frappe.sendmail(recipients=dev_users, content=email_body, subject=title)


def woorders_background_job():
	'''
		Description: This function run as background cron job to fetch Woocommerce Orders and process accordingly

		param/Input:

		return/Output : Create Erpnext Sales Orders, Sales Inoice, Customer, Address and Error Logs
	'''

	enqueue("ava_enhancements.ava_woocommerce_connection.get_woorders", queue='default', timeout=1500)


def change_woorder_status(order_id, status, wc_config):
	consumer_key = wc_config.api_consumer_key
	consumer_secret = wc_config.get_password(fieldname="api_consumer_secret")
	store_url = wc_config.woocommerce_server_url
	wc_api = API(url=store_url, consumer_key=consumer_key, consumer_secret=consumer_secret, timeout=50)
	resp = wc_api.put('orders/{0}'.format(order_id), {'status': status})

	return resp


def woorder_status_change(self, method):
	wc_config = frappe.get_doc("Ava Ecommerce Settings")
	if self.has_value_changed("status") and self.woocommerce_id and wc_config.enable_woocommerce_sync:
		"""
			#from hold to unhold
			Woocommerce Order status Options: pending, processing, on-hold, completed, cancelled, refunded, failed and trash  (Default is pending)
			ERP Order status Options: Draft, On Hold, To Deliver and Bill, To Bill, To Deliver, Completed, Cancelled, Closed
			
			woocommerce			ERP system 
			completed			Completed
			on-hold				On Hold
			Cancelled			cancelled
			processing			To Deliver and Bill, To Deliver
		"""
		order_status_mapping = {
			'To Deliver and Bill': 'processing', 'To Deliver': 'processing', 'Completed': 'completed',
			'On Hold': 'on-hold', 'Closed': 'cancelled', 'Cancelled': 'cancelled'
		}

		if order_status_mapping.get(self.status):
			resp = change_woorder_status(self.woocommerce_id, order_status_mapping.get(self.status), wc_config)
			if resp.status_code == 200:
				# self.db_set("woocommerce_so_status", order_status_mapping.get(self.status), update_modified=True)
				frappe.msgprint('{0} <br>Above Order status Changed to {1} on Woocommerce'.format(self.woocommerce_link, order_status_mapping.get(self.status)))
			else:
				# Error Log, email, and Trigger to set status
				frappe.throw(msg=resp.text, title='Order status update to {0} failed on Woocommerce'.format(order_status_mapping.get(self.status)))

	elif self.has_value_changed("status") and self.woocommerce_id and not wc_config.enable_woocommerce_sync:
		frappe.throw('Please enable Woocommerce sync from settings')
