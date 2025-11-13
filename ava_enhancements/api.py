
import json
import frappe
from frappe.utils import cstr
from frappe.auth import LoginManager
from ava_enhancements.geofencing import get_coverage_area, get_geolocation_for_leaflet
from ava_enhancements.main import (
	make_customer, create_customer_address, make_out_of_fence_order, make_sales_order
)


def gen_response(status, message, data=[]):
	"""
		Description: This function Generate API response for subsequent API's for IVR

		param/Input: http status code > status (str), response message > message (str), data (list)

		return/Output : set response keys for above paraments in frappe.response dictionary
	"""

	frappe.response['http_status_code'] = status
	frappe.response['message'] = message
	frappe.response['data'] = data


def generate_key(user):
	"""
		Description: This function Generate API secret key credentials for API login

		param/Input Username > user (str)

		return/Output : Dictionary with keys ('api_secret', 'api_key')> (dict)
	"""

	user_details = frappe.get_doc("User", user)
	api_secret = api_key = ''
	if not user_details.api_key and not user_details.api_secret:
		api_secret = frappe.generate_hash(length=15)
		# if api key is not set generate api key
		api_key = frappe.generate_hash(length=15)
		user_details.api_key = api_key
		user_details.api_secret = api_secret
		
		user_details.save(ignore_permissions=True)
	else:
		api_secret = user_details.get_password('api_secret')
		api_key = user_details.get('api_key')
	return {"api_secret": api_secret, "api_key": api_key}


@frappe.whitelist(allow_guest = True)
def login(usr=None, pwd=None):
	"""
		Description: This function is API for user login

		param/Input Username > usr (str), Password > pwd (str)

		return/Output : Generate Json Login details response or Error message for each call
	"""

	if usr and pwd:
		try:
			login_manager = LoginManager()
			login_manager.authenticate(usr, pwd)
			login_manager.post_login()
			if frappe.response['message'] == 'Logged In':
				frappe.response['user'] = login_manager.user
				frappe.response['key_details'] = generate_key(login_manager.user)
				frappe.response['expiry'] = '3 days, check cookies for expiry datetime'
				gen_response(200, frappe.response['message'])

		except Exception as e:
			error_message = frappe.get_traceback()+"\n{0}\nPayload:\n\tUser: {1}\tpassword: {2}".format(str(e), usr, pwd)
			frappe.log_error(error_message, "Error: IVR login failed")
			gen_response(401, "Invalid login credentials")

	else:
		gen_response(400, 'Insufficient Params')


def validate_customer(mobile_no):
	"""
		Description: This function check and return customer name if some is_ivr_customer customer exist with given mobile_no

		param/Input Mobile No > mobile_no (str)

		return/Output : customer name or False
	"""

	customer = frappe.db.get_value("Customer", {"customer_mobile_number": mobile_no}, "name")
	if customer:
		return customer
	else:
		return False


@frappe.whitelist()
def create_sales_order_ivr(data):
	try:
		data = json.loads(data)

		resp_items = data.get('items')
		customer = data.get('customer_name')
		customer_mobile = data.get('mobile_no').strip('+').lstrip('0')
		if len(customer_mobile) == 9:
			customer_mobile = '966' + str(customer_mobile)

		customer_location = data.get('geo_coordinates')

		if customer_location:
			customer_location = customer_location[0]
			geolocation = get_geolocation_for_leaflet(customer_location)
			territory_exist, territory_name_or_msg = get_coverage_area(geolocation, 'HOME DELIVERY HD')
		else:
			customer_location = None

		if customer and customer_mobile and customer_location and resp_items:
			if territory_exist:
				territory = territory_name_or_msg
				if not frappe.db.exists({'doctype': 'Customer', 'customer_mobile_number': customer_mobile}):
					# Create customer
					customer_name = make_customer(customer, customer_mobile, is_ivr_customer=True)

				else:
					customer_name = frappe.db.get_value('Customer', {'customer_mobile_number': customer_mobile}, ['name'])

				customer_address = create_customer_address(customer_name, customer_location, geolocation, territory, is_ivr_address=True)
				items = []
				for d in resp_items:
					items.append({'item_code': d.get('item_code'), 'qty': d.get('qty')})

				if items:
					so = make_sales_order(customer_name, items, customer_address, salla_order_id=False)
					sales_order = so.get('order_id')
					gen_response(201, "Sales Order Created", data=so)

			else:
				make_out_of_fence_order('IVR', '-', customer, customer_mobile, frappe.utils.now_datetime(), resp_items, geolocation)
				gen_response(200, "Out of Coverage Area Order")

		else:
			gen_response(400, "Insufficient Params")

	except Exception as e:
		gen_response(500, "Something wrong, please check error log in server")
		error_message = frappe.get_traceback()+"\n{0}\n\nPayload:\n\t{1}".format(str(e), data)
		frappe.log_error(error_message, "Error: IVR create sales order API Failed")


# @frappe.whitelist()
# def check_customer(data):
# 	"""
# 		Description: This function is API for checking customer if there is some customer exist with given mobile number
#
# 		param/Input: mobile_no in json > data (json)
#
# 		return/Output : Generate Json Customer details response or Error message for each call
# 	"""
#
# 	try:
# 		data = json.loads(data)
# 		mobile_no = data.get('mobile_no')
#
# 		if mobile_no:
# 			mobile_no = mobile_no.strip()
# 			customer = validate_customer(mobile_no)
# 			if customer:
# 				data = frappe.get_all("Customer", filters={"name": customer}, fields=["name", "customer_mobile_number"])
# 				gen_response(200, "Customer Exists", data=data)
# 			else:
# 				gen_response(404, "Customer Not Exists")
# 		else:
# 			gen_response(400, "Insufficient Params")
#
# 	except Exception as e:
# 		gen_response(500, "Something wrong, please check error log in server")
# 		error_message = frappe.get_traceback()+"\n{0}\n\nPayload:\n\t{1}".format(str(e), data)
# 		frappe.log_error(error_message, "Error: IVR check customer API Failed")
#
#
# @frappe.whitelist()
# def create_customer(data):
# 	"""
# 		Description: This function is API for creating customer with given json data
#
# 		param/Input: JSON keys (customer_name, mobile_no, geo_coordinates) > data > (json)
#
# 		return/Output : Generate Json Customer details response if customer created or Error message for each call
# 	"""
#
# 	try:
# 		data = json.loads(data)
# 		mobile_no = data.get('mobile_no')
# 		customer_name = data.get('customer_name')
# 		customer = make_customer(customer_name, mobile_no, is_salla_customer=False)
# 		gen_response(201, "Customer Created Successfully", customer)
#
# 	except Exception as e:
# 		error_message = frappe.get_traceback()+"\n{0}\n\nPayload:\n\t{1}".format(str(e), data)
# 		frappe.log_error(error_message, "Error: IVR create customer API Failed")
# 		gen_response(500, "Something wrong, please check error log in server")
#
#
# @frappe.whitelist()
# def create_sales_order(data):
# 	"""
# 		Description: This function is API for creating sales order or customer sales order or address with sales order with given json data
#
# 		param/Input: JSON keys (customer_name, mobile_no, geo_coordinates, items) > data > (json)
#
# 		return/Output : Generate JSON Sales Order details response if Sales Order created or Error message for each call
# 	"""
#
# 	try:
# 		# create_ivr_customer_and_sales_order(data, with_sales_order=True)
# 		data = json.loads(data)
#
# 		items = data.get('items')
# 		mobile_no = data.get('mobile_no')
# 		customer_name = data.get('customer_name')
# 		customer_coords = data.get('geo_coordinates')
#
# 		if mobile_no and customer_name and items and customer_coords:
# 			mobile_no = mobile_no.strip()
# 			geolocation = get_geolocation_for_leaflet(customer_coords)
# 			territory_exist, territory_name_or_msg = get_coverage_area(geolocation, 'HOME DELIVERY HD')
#
# 			if territory_exist:
# 				territory = territory_name_or_msg
#
# 				customer = validate_customer(mobile_no)
# 				customer_address = create_customer_address(customer, customer_coords, geolocation, territory, is_ivr_address=True)
#
# 				so = make_sales_order(customer, data.get('items'), customer_address)
# 				gen_response(201, "Sales Order Created Successfully", so)
#
# 			else:
# 				make_out_of_fence_order('IVR', '-', customer_name, mobile_no, frappe.utils.now_datetime(), [], geolocation)
# 				gen_response(200, "Out of Coverage Area Order")
#
# 		else:
# 			gen_response(400, "Insufficient Params")
#
# 	except Exception as e:
# 		error_message = frappe.get_traceback()+"\n{0}\n\nPayload:\n\t{1}".format(str(e), data)
# 		frappe.log_error(error_message, "Error: IVR create Sales Order API Failed for Order")
# 		gen_response(500, "Something wrong, please check error log in server")
#
#
# def create_ivr_customer_and_sales_order(data, with_sales_order=False):
# 	"""
# 		Description: This function is API for creating sales order or customer sales order or address with sales order with given json data
#
# 		param/Input: JSON keys (customer_name, mobile_no, geo_coordinates, items) > data > (json)
#
# 		return/Output : Generate JSON Sales Order details response if Sales Order created or Error message for each call
# 	"""
#
# 	data = json.loads(data)
#
# 	mobile_no = data.get('mobile_no')
# 	customer_name = data.get('customer_name')
# 	customer_coords = data.get('geo_coordinates')
#
# 	if customer_coords:
# 		geolocation = get_geolocation_for_leaflet(customer_coords)
# 		territory_exist, territory_name_or_msg = get_coverage_area(geolocation, 'HOME DELIVERY HD')
#
# 	customer = validate_customer(mobile_no)
# 	if customer:
# 		gen_response(409, "Customer Exists", data=customer)
# 		if with_sales_order:
# 			if customer_coords:
# 				if territory_exist:
# 					territory = territory_name_or_msg
# 					address = ava_reverse_geocoding(customer_coords)
# 					customer_address = create_customer_address(customer, customer_coords, geolocation, territory, is_ivr_address=True)
# 				else:
# 					make_out_of_fence_order('IVR', '-', customer_name, mobile_no, frappe.utils.now_datetime(), [], geolocation)
# 					gen_response(200, "Out of Coverage Area Order")
# 					return
#
# 			else:
# 				customer_address = get_customer_address(customer).get('addr_name')
#
# 			so = make_sales_order(customer, data.get('items'), customer_address)
# 			gen_response(201,"Sales Order Created Successfully", so)
#
# 	elif customer == False:
# 		if customer_name and mobile_no and customer_coords:
# 			if territory_exist:
# 				territory = territory_name_or_msg
#
# 				customer = make_customer(customer_name, mobile_no, is_salla_customer=False)
# 				address = ava_reverse_geocoding(customer_coords)
# 				customer_address = create_customer_address(customer, customer_coords, geolocation, territory, is_ivr_address=True)
#
# 				gen_response(201, "Customer Created Successfully", customer)
#
# 				if with_sales_order:
# 					so = make_sales_order(customer, data.get('items'), customer_address)
# 					gen_response(201, "Sales Order Created Successfully", so)
#
# 			elif not territory_exist:
# 				make_out_of_fence_order('IVR', '-', customer_name, mobile_no, frappe.utils.now_datetime(), [], geolocation)
# 				gen_response(200, "Out of Coverage Area Order")
# 				return
#
# 		else:
# 			gen_response(400, "Insufficient Params")




import frappe
from frappe import _

@frappe.whitelist()
def prevent_file_delete():
    # Only Administrator or System Manager can delete
    if frappe.session.user != 'Administrator' and not frappe.has_role("System Manager"):
        frappe.throw(_("You are not allowed to delete attachments."))

    # Call the original delete method
    from frappe.core.doctype.file.file import delete
    return delete()

