import json
import frappe
import requests
from frappe.utils import cstr, today, get_url, flt
from frappe.utils.background_jobs import enqueue
from ava_enhancements.geofencing import (
	get_coverage_area, get_geolocation_for_leaflet
)
from ava_enhancements.main import (
	make_customer, create_customer_address, make_sales_order, make_out_of_fence_order, get_users_by_role
)

def get_request(content_type, method, access_token):
	'''
		Description: Get request for Salla

		param/Input: Content Type > content_type (str), Order ID > method (str), access token > access_token (str)

		return/Output : Salla response > response
	'''

	headers = {'Content-Type': content_type, 'Authorization': 'Bearer '+cstr(access_token)}
	url = 'https://api.salla.dev/admin/v2/'+method
	response = requests.get(url, headers=headers)

	return response


def get_salla_orders_details(order_id, access_token):
	'''
		Description: This function Salla order id and return all the order details

		param/Input: Salla Order ID > order_id (str), Salla access token > access_token (str)

		return/Output : Comma seperated string of intersecting_territories list (str)
	'''

	response = get_request('application/json', 'orders/{0}'.format(order_id), access_token)

	if response.status_code == 200:
		response = response.json()
		return response.get('data')


@frappe.whitelist()
def get_salla_orders():
	'''
		Description: This function Records from Salla between current and previous day based on pagination on Salla API,
			 then fetch order details for each order id and then process each response to create records in ERP

		param/Input:

		return/Output : Create ERPnext records or log errors
	'''

	wc_config = frappe.get_doc("Ava Ecommerce Settings")
	access_token = wc_config.get_password(fieldname="api_access_token_salla")

	if wc_config.enable_salla_sync and access_token:

		to_date = frappe.utils.add_days(frappe.utils.nowdate(), +1)
		from_date = frappe.utils.add_days(to_date, -2)

		response = get_request('application/json', 'orders?from_date={0}&to_date={1}'.format(from_date, to_date), access_token)

		if response.status_code == 200:
			response = response.json()
			pagination = response.get('pagination')

			curr_page = pagination.get('currentPage')
			total_pages = pagination.get('totalPages')
			count = 0
			for page in range(curr_page, total_pages+1):
				page = 'orders?from_date={0}&to_date={1}&page={2}'.format(from_date, to_date, page)
				paginated_resp = get_request('application/json', page, access_token)

				if paginated_resp.status_code == 200:
					paginated_resp = paginated_resp.json()
					for d in paginated_resp.get('data'):
						if not frappe.db.exists({'doctype':'Sales Order', 'salla_order_id': d.get('reference_id')}):
							count = count + 1
							'''
								status:
									{'id': 1939592358, 'name': 'قيد التنفيذ'} >> In Progress Order
									{'id': 99911771, 'name': 'محذوف'} >> Deleted Order
									{'id': 566146469, 'name': 'بإنتظار المراجعة'} >> Under Review
							'''
							if d.get('status').get('id') not in [99911771, 525144736]: # if not deleted Order
								orders_details = get_salla_orders_details(d.get('id'), access_token)
								if orders_details.get('id'):
									salla_order_processor(orders_details)
						else:
							pass
				else:
					error_message = cstr(paginated_resp.text)
					frappe.log_error(error_message, "Error: Salla Sales Order Details API Error")
			# print(count)

		else:
			error_message = cstr(response.text)
			frappe.log_error(error_message, "Error: Salla Sales Order Details API Error")


def salla_order_processor(orders_details):
	'''
		Description: Salla Sales Order Proccessing

			Check customer by phone no. if exist > create/modify customer, create address, create sales Order
				take cust mob no. from salla and check
					if not any customer with mobile no. then create customer and get customer name
					else get customer name in ERP and if not  set salla_customer_id then set in customer
				check if no address exist with customer and goelocation(catering multiple address for customer)
					if True Create address
				Check and make Sales Order Items list from current Salla Order items ids
					if item_sku exist for order take item
					elif check for promtional item
					else make error log
				if Sales Order Items list exist
					make Sales Order

		param/Input: Salla Order > orders_details (dict)

		return/Output : Customer, Address, Sales Orders (submit) and return so name, Sales Invoivce , Error log
	'''

	try:
		salla_order_id = orders_details.get('reference_id')
		salla_items=orders_details.get('items')
		order_time = frappe.utils.now_datetime()
		customer = orders_details.get('customer')
		source_details = orders_details.get('source_details')
		salla_payment_method = orders_details.get('payment_method')
		salla_address = orders_details.get('shipping').get('address')
		customer_mobile = cstr(customer.get('mobile_code')) + cstr(customer.get('mobile'))  # cstr(customer.get('mobile_code').replace('+', "")) + cstr(customer.get('mobile'))
		customer_email = customer.get('email')
		customer_id = customer.get('id')
		_customer_name = cstr(customer.get('first_name')) + ' ' + cstr(customer.get('last_name'))

		customer_location = salla_address.get('geo_coordinates')

		geolocation = get_geolocation_for_leaflet(customer_location)
		territory_exist, territory_name_or_msg = get_coverage_area(geolocation, 'HOME DELIVERY HD')

		coupon_code = ''
		if source_details.get('type') == 'coupon':
			coupon_codes = [cc[0] for cc in frappe.get_all('Coupon Code', as_list=1)]
			if source_details.get('value') not in coupon_codes:
				frappe.throw('Invalid Coupon Code')
			else:
				coupon_code = source_details.get('value')

		if territory_exist:
			territory = territory_name_or_msg
			if customer_mobile:
				if not frappe.db.exists({'doctype': 'Customer', 'customer_mobile_number': customer_mobile}):
					### Create customer
					customer_name = make_customer(_customer_name, customer_mobile, customer_email, salla_customer_id=customer_id)

				else:
					existing_cust_data = frappe.db.get_value('Customer', {'customer_mobile_number': customer_mobile}, ['name', 'salla_customer_id'])
					customer_name = existing_cust_data[0]
					if not existing_cust_data[1]:
						frappe.db.set_value('Customer', existing_cust_data[0], {'is_salla_customer': '1', 'salla_customer_id': cstr(customer.get('id'))})

				customer_address = create_customer_address(customer_name, customer_location, geolocation, territory, is_salla_address=True)

				#### Check and make Sales Order Items from Salla Order
				items = []
				non_existing_items = ''
				for d in salla_items:
					salla_sku = cstr(d.get('product').get('id'))
					if salla_sku and frappe.db.exists({'doctype':'Item', 'salla_sku': salla_sku}):
						item = frappe.get_doc('Item', {'salla_sku': salla_sku})
						items.append({'item_code': item.item_code, 'qty': d.get('quantity'), 'salla_sku': salla_sku})

					else:
						# Need to remove salla free qty col
						promo_item = frappe.db.get_value('Salla Promotions', {'parenttype': 'Item', 'salla_promotion_code': salla_sku}, ['parent', 'salla_order_qty', 'salla_free_qty'])
						if promo_item:
							item_code, salla_order_qty, salla_free_qty = promo_item
							items.append({'item_code': item_code, 'qty': salla_order_qty, 'salla_sku': salla_sku})
							# items.append({'item_code': item_code, 'qty': salla_free_qty, 'pricing_rules': '', 'salla_sku': salla_sku,
							# 			  'rate': 0, 'price_list_rate':0 , 'is_free_item': 1})
						else:
							non_existing_items += '\t' + cstr(salla_sku) + '\n'
				if items:
					#### Create Sales Order
					_orders_details = orders_details  # frappe.utils.cstr(orders_details)
					so = make_sales_order(customer_name, items, customer_address, coupon_code=coupon_code, json_resp=_orders_details, salla_order_id=salla_order_id, salla_payment_method=salla_payment_method)
					sales_order = so.get('order_id')
					return sales_order

				else:
					message = 'During Salla Orders synchronize an exception occured for Salla Order ID: {0}\nSynchronization time: {1}\nItem(s) with following Salla ID not existed in ERP:\n{2}'
					frappe.throw(message.format(salla_order_id, order_time, non_existing_items))
					return non_existing_items

			else:
				message = 'During Salla Orders synchronization an exception occured for Salla Order ID: {0}\nSynchronization time: {1}\nCustomer mobile was not in Order'
				message = message.format(salla_order_id, order_time)
				frappe.throw(message)

		else:
			if not frappe.db.exists({'doctype':'Out of Fence Order', 'order_source': 'Salla', 'customer_mobile': customer_mobile, 'order_id': salla_order_id}):
				make_out_of_fence_order('Salla', salla_order_id, _customer_name, customer_mobile, order_time, salla_items, geolocation)

	except Exception as e:
		print("Salla Orders synchronization failed : {}".format(e))
		error_message = frappe.get_traceback()+"\n{}".format(str(e)) + '\nOrder sync failed for Payload: {}'.format(orders_details)
		title = "Error: Salla Sales Order synchronization failed"
		error_log = frappe.log_error(error_message, title)
		wc_config = frappe.get_doc("Ava Ecommerce Settings")
		if wc_config.send_error_log_email:
			dev_users = get_users_by_role(wc_config.ecommerce_error_log_reviewer_role)
			salla_order_url = orders_details.get('urls').get('admin')
			error_log_url = get_url("/app/error-log/{0}".format(error_log.name))
			email_body = 'Please check Error Log: {0} for this Salla Order: {1}'.format(error_log_url, salla_order_url)
			frappe.sendmail(recipients=dev_users, content=email_body, subject=title)


def salla_orders_background_job():
	'''
		Description: This function run as background cron job to fetch Salla Orders and process accordingly

		param/Input:

		return/Output : Create Erpnext Sales Orders, Sales Inoice, Customer, Address and Error Logs
	'''

	enqueue("ava_enhancements.ava_salla_connection.get_salla_orders", queue='short', timeout=1500)

