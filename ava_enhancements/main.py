import json
import frappe
import requests
from frappe.utils import cstr, today, get_url, flt
from frappe.utils.background_jobs import enqueue
from ava_enhancements.geofencing import (
	get_coverage_area, get_geolocation_for_leaflet,
	ava_reverse_geocoding, get_possible_territories
)
from frappe.model.mapper import get_mapped_doc


def get_customer_address(customer_name, geolocation=None):
	'''
	Description: This function check if a customer with geolocation have some similar address that match geolocation of customer, or without geolocation it return latest address linked with customer

	param/Input: Customer Name > customer_name (str), Leaflet geolocation > geolocation (str)

	return/Output : Address status keys => ('addr_exist', 'addr_name') > address_status (dict)
	'''

	address_list = frappe.db.get_list('Dynamic Link', filters={'link_doctype': 'Customer', 'parenttype': 'Address', 'link_name': customer_name}, order_by='modified desc', fields=['parent'])

	address_status = {'addr_exist':False}
	for d in address_list:
		customer_geolocation = frappe.db.get_value('Address', d.get('parent'), 'geolocation')
		if geolocation == customer_geolocation:
			address_status['addr_exist'] = True
			address_status['addr_name'] = d.get('parent')
			return address_status

	if not geolocation and address_list:
		address_status['addr_exist'] = True
		address_status['addr_name']	 = address_list[0].get('parent')

	return address_status


def make_out_of_fence_order(order_source, order_id, customer_name, customer_mobile, order_time, items, geolocation):
	'''
		Description: This function makes records for Salla/IVR orders that are not within any of coverage area

		param/Input: Sall/IVR > order_source (str), Order ID for Salla > order_id (str),
			Customer Name > customer_name (str), Customer mobile no. > customer_mobile (str),
			Time now > order_time (str), Order items > items (str), Leaflet Geolocation > geolocation (str)

		return/Output : Out of Fence Order name (str)
	'''

	if order_source == 'Salla':
		items = [{'item': d.get('product').get('id'), 'quantity': d.get('quantity')} for d in items]
	elif order_source == 'IVR':
		items = [{'item': d.get('item_code'), 'quantity': d.get('qty')} for d in items]
	elif order_source == 'Woocommerce':
		items = [{'item': d.get('product_id'), 'quantity': d.get('quantity')} for d in items]

	possible_territory = [{'territory': d} for d in get_possible_territories(geolocation)]
	doc = frappe.get_doc(dict(
		doctype="Out of Fence Order",
		order_source=order_source,
		order_id=order_id,
		customer_name=customer_name,
		customer_mobile=customer_mobile,
		order_time=order_time,
		items=items,
		location=geolocation,
		possible_territory=possible_territory
	))
	doc.save()
	frappe.db.commit()

	wc_config = frappe.get_doc("Ava Ecommerce Settings")
	if wc_config.send_error_log_email:
		call_centre_agents = get_users_by_role(wc_config.out_of_fence_order_reviewer_role)
		if call_centre_agents:
			link = '<a class="btn  btn-primary" style="margin-right: 10px" href="' + '/app/out-of-fence-order/{0}'.format(doc.name) + '">{0}</a>'.format(doc.name)
			message = 'Please check this Order from {0}, this seems out of Fence. Click here to check Out of fence order  {1}'.format('Salla', link)
			if doc.possible_territory:
				possible_territories = ', '.join([d.territory for d in doc.possible_territory])
				possible_territories_msg = '<br>Check following possible territories, {0} for this Order.'.format(possible_territories)
				message = message + possible_territories_msg

			frappe.sendmail(recipients=call_centre_agents, content=message, subject='Out of Fence Order review')

	return doc.name


def make_customer(customer_name, customer_mobile, customer_email=None, is_ivr_customer=False, salla_customer_id=None, woocomm_customer_id=None):
	'''
		Description: This function create customer record in ERP for Salla and IVR

		param/Input: customer (str), customer_mobile (str), is_salla_customer (bool)

		return/Output : Customer name (str)
	'''

	wc_config = frappe.get_doc("Ava Ecommerce Settings")

	doc = frappe.get_doc(dict(
		doctype="Customer",
		is_salla_customer='1' if salla_customer_id else '0',
		is_ivr_customer='1' if is_ivr_customer else '0',
		industry_type=wc_config.industry_type,
		customer_type='Individual',
		payment_cash=1,
		dn_required=1,
		mobile_no=customer_mobile,
		customer_mobile_number=customer_mobile,
		customer_group=wc_config.default_customer_group,
		email_id=customer_email,
		woocommerce_id=woocomm_customer_id,
		salla_customer_id=salla_customer_id,
		customer_name=customer_name,
		customer_name_in_arabic=customer_name
	)).insert(ignore_permissions=True)

	return doc.name


def create_customer_address(customer_name, customer_location, geolocation, territory, is_salla_address=False, is_ivr_address=False):
	'''
		Description: This function check Address record in ERP for specific customer and location, and return address name if exist, else create new address

		param/Input: customer_name (str), customer_location (str), geolocation (dict), territory (str), is_salla_address (bool), is_ivr_address (bool)

		return/Output : customer_address (str)
	'''

	address_status = get_customer_address(customer_name, geolocation)
	if not address_status.get('addr_exist'):
		#### Create address
		customer_address = make_address(customer_name, customer_location, geolocation, territory, is_salla_address=is_salla_address, is_ivr_address=is_ivr_address)
	else:
		customer_address = address_status.get('addr_name')

	return customer_address


def make_address(customer_name, customer_location, geolocation, territory, is_salla_address=False, is_ivr_address=False):
	'''
		Description: This function create Address record in ERP for customer and location

		param/Input: customer_name (str), customer_location (str), geolocation (dict), territory (str), is_salla_address (bool), is_ivr_address (bool)

		return/Output : customer_address (str)
	'''
	address_from_location = ava_reverse_geocoding(customer_location)

	if not address_from_location:
		frappe.throw('Error: Address not created, Something wrong with reverse Geocode API')

	address_line1 = ", ".join(map(str,address_from_location.values()))
	address_line2 = '' ##### TBC GF

	wc_config = frappe.get_doc("Ava Ecommerce Settings")

	links = [{'link_doctype': 'Customer', 'link_name': customer_name, 'link_title': customer_name}]

	doc = frappe.get_doc(dict(
		doctype = 'Address',
		is_salla_address = '1' if is_salla_address else '0',
		is_ivr_address = '1' if is_ivr_address else '0',
		coverage_area = territory,
		territory =  territory,
		country = wc_config.country, #change
		address_type = 'Shipping',
		geolocation =  geolocation,
		address_title = customer_name,
		city = address_from_location.get('city'),
		pincode = address_from_location.get('postal_code'),
		address_line1 = address_line1,
		links = links
	)).insert(ignore_permissions = True)

	return doc.name


def make_sales_order(customer, so_items, customer_address, coupon_code=None, json_resp=None, salla_order_id=None,
	salla_payment_method=None, wooorder_id=None, wooorder_payment_method=None, delivery_date=None, delivery_slot=None,
	woorder_link=None, keep_in_draft=False):
	'''
		Description: This function create Sales Order record in ERP for Salla and IVR customer

		param/Input: customer (str), so_items (list), customer_address (str), salla_order_id (str), salla_payment_method (bool)

		return/Output : sales order details (dict)
	'''

	from erpnext.controllers.accounts_controller import get_taxes_and_charges

	taxes_and_charges_temp = frappe.get_value('Sales Taxes and Charges Template', {'is_default':1}, ['name'])

	taxes = get_taxes_and_charges('Sales Taxes and Charges Template', taxes_and_charges_temp)

	transaction_date_time = today()  # Salla Order Time

	territory = frappe.db.get_value('Address', customer_address, 'coverage_area')  # fix to coverage_area to territory

	warehouse, territory_manager = frappe.db.get_value('Territory', territory, ['default_warehouse', 'territory_manager'])

	sales_team = [{'doctype': 'Sales Team', 'sales_person': territory_manager, 'allocated_percentage': 100}]

	doc = frappe.get_doc(dict(
		doctype="Sales Order",
		is_salla_order='1' if salla_order_id else '0',
		is_ivr_order='0' if salla_order_id else '1',
		salla_order_id=salla_order_id if salla_order_id else '',
		po_no=salla_order_id or wooorder_id or '',
		salla_payment_method=salla_payment_method if salla_payment_method else '',
		customer=customer,
		disable_rounded_total=1,
		taxes_and_charges=taxes_and_charges_temp,
		customer_address=customer_address,
		company=frappe.db.get_value("Global Default","Global Default","default_company"),
		transaction_date=transaction_date_time,
		delivery_date=delivery_date if delivery_date else transaction_date_time,
		delivery_slot=delivery_slot,
		set_warehouse=warehouse,
		coupon_code=coupon_code,
		woocommerce_id=wooorder_id,
		woocommerce_link=woorder_link,
		woocommerce_payment_method=wooorder_payment_method,
		territory=territory,
		items=so_items,
		taxes=taxes,
		sales_team=sales_team,
		salla_response=frappe.utils.cstr(json_resp) if salla_order_id else ''
	))

	so = doc.insert(ignore_permissions = True)
	# so.save()
	if salla_order_id:
		if flt(so.grand_total) == flt(json_resp.get('amounts').get('total').get('amount')):
			so.submit()
		else:
			so.save()
	elif keep_in_draft:
		so.save()
	else:
		so.submit()
	frappe.db.commit()
	so_items_order = [{'item_code': d.get('item_code'), 'item_name': d.get('item_name'), 'qty': d.get('qty'), 'is_free_item': d.get('is_free_item')} for d in so.items]
	return {
			'order_id': so.name, 'creation': so.creation, 'customer': so.customer, 'customer_name': so.customer_name,
			'delivery_date': so.delivery_date, 'items': so_items_order, 'mobile_no': so.customer_mobile_number
		}


# def make_advance_payment(dt, dn, salla_order_id=None, salla_payment_method=None):
# 	'''
# 		Description: This function create Payment Entry record in ERP for Salla customer
#
# 		param/Input: 'Sales Order' > dt (str), Sales Order name > dn (str), salla_order_id (str), salla_payment_method (str)
#
# 		return/Output : Payment Entry  Name (str)
# 	'''
#
# 	from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry
# 	pe = get_payment_entry(dt, dn)
#
# 	pe.is_salla_order = 1
# 	pe.salla_order_id = salla_order_id
# 	pe.salla_payment_method = salla_payment_method
#
# 	pe = pe.insert(ignore_permissions = True)
# 	pe.submit()
# 	return pe
#
#
# @frappe.whitelist()
# def make_sales_invoice(sales_order, salla_order_id=None):
# 	'''
# 		Description: This function create Sales Invoice record in ERP for Salla customer linked with given sales_order
#
# 		param/Input: Sales Order name > sales_order (str), salla_order_id (str)
#
# 		return/Output : Sales Invoice Name (str)
# 	'''
#
# 	from erpnext.selling.doctype.sales_order.sales_order import make_sales_invoice
#
# 	salla_pos_profile = frappe.db.get_value('Ava Enhancements Settings', 'Ava Enhancements Settings', 'salla_pos_profile')
#
# 	si = make_sales_invoice(sales_order)
#
# 	si.is_pos = 1
# 	si.is_salla_order = 1
# 	si.salla_order_id = salla_order_id
# 	si.invoice_reference = salla_order_id
# 	si.pos_profile = salla_pos_profile
#
# 	si.run_method("set_missing_values")
# 	for d in si.payments:
# 		if d.default:
# 			d.base_amount = flt(si.outstanding_amount, d.precision("base_amount"))
# 			d.amount = flt(si.outstanding_amount/si.conversion_rate, d.precision("amount"))
#
# 	si = si.insert(ignore_permissions = True)
# 	# si.submit()
#
# 	return si
#
#
# @frappe.whitelist()
# def make_delivery_note(sales_invoice):
# 	'''
# 		Description: This function create Delivery Note record in ERP for Salla customer linked with given sales invoice
#
# 		param/Input: Sales Invoice name > sales_invoice (str)
#
# 		return/Output : Delivery Note Name (str)
# 	'''
#
# 	from erpnext.accounts.doctype.sales_invoice.sales_invoice import make_delivery_note
# 	dn = make_delivery_note(sales_invoice)
# 	dn = dn.insert(ignore_permissions = True)
# 	# dn.submit()
#
# 	return dn


def salla_orders_background_job():
	'''
		Description: This function run as background cron job to fetch Salla Orders and process accordingly

		param/Input:

		return/Output : Create Erpnext Sales Orders, Sales Inoice, Customer, Address and Error Logs
	'''

	enqueue("ava_enhancements.main.get_salla_orders", queue='short', timeout=1500)


@frappe.whitelist()
def get_address_territory_from_geolocation(geolocation, customer_name):
	'''
		Description: For a given geolocation point this function will get street address using Google maps API on changing geolocaton in Address
					also return territory in exist

		param/Input: Leaflet Geolocation > geolocation (dict)

		return/Output : street address > resp (dict), 'invalid_location' (str) if geolocation type is not Point
	'''

	customer_group = frappe.get_value('Customer', customer_name, 'customer_group')
	if not customer_group:
		frappe.throw(cstr('no customer group in customer'))

	features = json.loads(geolocation)['features']

	if len(features) == 1 and features[0]['geometry']['type'] == 'Point':
		coordinates = features[0]['geometry']['coordinates']
		address = ava_reverse_geocoding({'lat':coordinates[1], 'lng':coordinates[0]})
		territory = get_coverage_area(geolocation, customer_group)

		resp = { 'success': True, 'city': address['city'], 'postal_code': address['postal_code'],
				'address_line1':", ".join(map(str,address.values()))}

		if territory[0] == True:
			resp['territory'] = territory[1]
		else:
			resp['territory'] = territory[0]
		return resp

	else:
		return 'invalid_location'


@frappe.whitelist()
def territory_fence_validation(fence):
	'''
		Description: This is a validation function for Territory , whenever a new fence in Territory is created this function
			take care and make sure valid fence of type Polygon is created and also restrict to just one fence each Territory

		param/Input: Leaflet Geolocation > fence (str)

		return/Output : 'one_fence_allowed' (dict), 'only_poly_allowed' (str)
	'''

	features = json.loads(fence)
	if features.get('features'):
		feature  = features['features']
		# if len(feature) > 1:
		# 	return 'one_fence_allowed'

		if feature[0]['geometry']['type'] != 'Polygon':
			return 'only_poly_allowed'


@frappe.whitelist()
def pick_location_from_pluscode(google_plus_code):
	if google_plus_code:
		import urllib.parse
		google_plus_code = urllib.parse.quote(google_plus_code)
		wc_config = frappe.get_doc("Ava Ecommerce Settings")
		key = wc_config.get_password(fieldname="api_key_google_maps")
		url = 'https://maps.googleapis.com/maps/api/geocode/json?address={}&key={}'.format(google_plus_code, key)
		response = requests.get(url)
		if response.status_code == 200:
			response = response.json()
			results = response.get('results')
			if results:
				lat_lng = results[0].get('geometry').get('location')
				return get_geolocation_for_leaflet(lat_lng)
			else:
				frappe.throw('Inaccurate Plus Code, resp {}'.format(cstr(response.get('status'))))
	else:
		frappe.throw('Please input Plus Code')


def update_territory_in_customer(self, method):
	territory = self.territory or self.coverage_area
	if self.links and territory:
		customer = [d.link_name for d in self.links if d.link_doctype == 'Customer' and d.parenttype == 'Address']
		if customer:
			customer = frappe.get_doc('Customer', customer[0])

			if not customer.customer_primary_contact:
				contact = frappe.get_all('Dynamic Link', {'link_doctype': 'Customer', 'link_name': customer.name, 'parenttype': 'Contact'}, ['parent'])
				if contact:
					contact = contact[0].get('parent')
					customer.customer_primary_contact = contact

			customer.territory = territory
			if not customer.customer_name_in_arabic:
				customer.customer_name_in_arabic = customer.customer_name
			customer.save()


def get_users_by_role(role):
	return frappe.db.sql_list("""select parent FROM `tabHas Role`
		WHERE role='{0}'
		AND parent!='Administrator'
		AND parent IN (SELECT email FROM tabUser WHERE enabled=1)""".format(role))


def custom_wh_allowed(warehouses, fwh=None, twh=None):
	allowed_warehouses = []
	if frappe.db.exists('Warehouse Custom Permission', frappe.session.user):
		doc = frappe.get_doc('Warehouse Custom Permission', frappe.session.user)
		perm_field = 'allowed_source_warehouses' if fwh else 'allowed_target_warehouses'
		if doc.get(perm_field):
			for wh in doc.get(perm_field):
				allowed_warehouses.append([wh.warehouse])
		elif not allowed_warehouses:
			allowed_warehouses = warehouses
	return allowed_warehouses


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_custom_allowed_s_warehouse(doctype, txt, searchfield, start, page_len, filters):
	warehouses = frappe.db.sql("""select name from tabWarehouse
		where is_group = 0 and disabled = 0 and company = %s and name != %s 
		and %s like %s order by name limit %s, %s""" %
		("%s", "%s", searchfield, "%s", "%s", "%s"),
		(filters[0][-1], filters[-1][-1], "%%%s%%" % txt, start, page_len), as_list=1)

	allowed_warehouses = custom_wh_allowed(warehouses, fwh=True)
	return allowed_warehouses


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_custom_allowed_t_warehouse(doctype, txt, searchfield, start, page_len, filters):
	warehouses = frappe.db.sql("""select name from tabWarehouse
		where is_group = 0 and disabled = 0 and company = %s and %s like %s order by name
		limit %s, %s""" % ("%s", searchfield, "%s", "%s", "%s"),
		(filters[0][-1], "%%%s%%" % txt, start, page_len), as_list=1)

	allowed_warehouses = custom_wh_allowed(warehouses, twh=True)
	return allowed_warehouses


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_custom_allowed_t_warehouse_transits(doctype, txt, searchfield, start, page_len, filters):
	warehouses = frappe.db.sql("""select name from tabWarehouse
		where is_group = 0 and disabled = 0 and company = %s and warehouse_type = %s and %s like %s order by name 
		limit %s, %s""" % ("%s", "%s", searchfield, "%s", "%s", "%s"),
		(filters['company'], filters['warehouse_type'], "%%%s%%" % txt, start, page_len), as_list=1)

	allowed_warehouses = custom_wh_allowed(warehouses, twh=True)
	return allowed_warehouses


def validate_custom_warehouse_permission(self, method):
	if frappe.db.exists('Warehouse Custom Permission', frappe.session.user):
		doc = frappe.get_doc('Warehouse Custom Permission', frappe.session.user)
		if (doc.allowed_source_warehouses and self.from_warehouse) or (doc.allowed_target_warehouses and self.to_warehouse):
			flag_fwh = flag_twh = False
			msg = []
			allowed_source_warehouses = [d.warehouse for d in doc.allowed_source_warehouses]
			allowed_target_warehouses = [d.warehouse for d in doc.allowed_target_warehouses]
			if self.from_warehouse and self.from_warehouse not in allowed_source_warehouses:
				msg.append('{0} warehouse in Source Warehouse is restricted'.format(self.from_warehouse))
				flag_fwh = True

			if self.to_warehouse and self.to_warehouse not in allowed_target_warehouses:
				msg.append('{0} warehouse in Source Warehouse is restricted'.format(self.to_warehouse))
				flag_twh = True

			for d in self.items:
				if d.s_warehouse and d.s_warehouse not in allowed_source_warehouses:
					flag_fwh = True
					msg.append('{0} warehouse in Source Warehouse of Item # {1} is restricted'.format(d.s_warehouse, d.idx))
				if d.t_warehouse and d.t_warehouse not in allowed_target_warehouses:
					flag_twh = True
					msg.append('{0} warehouse in Target Warehouse of Item # {1} is restricted'.format(d.t_warehouse, d.idx))

			if (flag_fwh or flag_twh) and msg:
				frappe.throw(cstr('<br>'.join(msg)))


def is_payment_cash_customer(self, method):
	payment_cash = frappe.db.get_value('Customer', self.customer, 'payment_cash')
	if payment_cash:
		if not (frappe.get_all('POS Profile User', {'user':  frappe.session.user}) or frappe.session.user == "Administrator" or "System Manager" in frappe.get_roles(frappe.session.user)):
			frappe.throw('User <b>{0}</b> not authorized to create cash invoice'.format(frappe.session.user))
		self.is_pos = '1'


def sales_order_cancel_validation(self, method):
	if not (frappe.session.user == self.owner or frappe.session.user == "Administrator" or bool(set(['System Manager', '01 Call Center']) & set(frappe.get_roles(frappe.session.user)))):
		frappe.throw('User <b>{0}</b> can only cancel own Sales Order, please contact Call Centre for more info'.format(frappe.session.user))


@frappe.whitelist()
def set_branch_and_territory(customer_branch, branch_address, territory):
	'''
		Description: This function run in after_save event of Address to updates branch address and  Territory in Branch

		param/Input: customer_branch (str), branch_address (str), territory (str)

		return/Output : save/update values in child table row
	'''
	customer_branch_name = frappe.db.get_value('Customer Branch Detail CT', {'customer_branch': customer_branch}, 'name')
	frappe.db.set_value('Customer Branch Detail CT', customer_branch_name, 'branch_address', branch_address)
	frappe.db.set_value('Customer Branch Detail CT', customer_branch_name, 'territory', territory)


@frappe.whitelist()
def create_address_from_customer(customer_name, longitude, latitude):
	'''
		Description: This is a validation function for Territory , whenever a new fence in Territory is created this function
			take care and make sure valid fence of type Polygon is created and also restrict to just one fence each Territory

		param/Input: Leaflet Geolocation > fence (str)

		return/Output : 'one_fence_allowed' (dict), 'only_poly_allowed' (str)
	'''

	customer_coords =  {"lat": latitude, "lng": longitude}
	geolocation = get_geolocation_for_leaflet(customer_coords)

	customer_group = frappe.get_value('Customer', customer_name, 'customer_group')

	territory_exist, territory_name_or_msg = get_coverage_area(geolocation, customer_group)

	if territory_exist:
		territory = territory_name_or_msg
		if customer_name and customer_coords and geolocation and territory:
			address = make_address(customer_name, customer_coords, geolocation, territory)
			return {'status': 'success', 'data': address}
	else:
		return {'status': 'failed', 'data': territory_name_or_msg}


@frappe.whitelist()
def get_customer_location(customer_address):
	if not customer_address:
		return

	customer_location = frappe.get_value('Address', customer_address, 'geolocation')
	if customer_location:
		resp = json.loads(customer_location)
		lng, lat = resp.get('features')[0].get('geometry').get('coordinates')
		coordinates = {'lng': lng, 'lat': lat}
		return coordinates


@frappe.whitelist()
def fetch_territory_manager_and_warehouse_for_address(address):
	territory = frappe.db.get_value('Address', address, 'coverage_area')  # fix to coverage_area to territory
	if territory:
		resp = frappe.db.get_value('Territory', territory, ['territory_manager', 'default_warehouse', 'name'], as_dict=1)

		customer_coords = frappe.get_value('Address', address, 'geolocation')
		if customer_coords:
			customer_coords = json.loads(customer_coords)
			lng, lat = customer_coords.get('features')[0].get('geometry').get('coordinates')
			coordinates = {'lng': lng, 'lat': lat}
			resp['customer_coords'] = coordinates
		else:
			resp['customer_coords'] = ''

		return resp


#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
# def mobile_number_validation(customer_mobile_number):
# 	customer_mobile_number = customer_mobile_number.strip('+')
#
# 	if len(customer_mobile_number) != 12:
# 		frappe.throw('Mobile no. Length not accurate')
#
# 	if cstr(customer_mobile_number[:3]) != '966':
# 		frappe.throw('Country code missing')
#
# 	return customer_mobile_number
#
#
# @frappe.whitelist()
# def send_address_request_link(doc):
# 	import string
# 	import random
# 	from frappe.core.doctype.sms_settings.sms_settings import send_sms
# 	doc = json.loads(doc)
# 	if not doc.get('customer_mobile_number'):
# 		frappe.throw('Please Enter Customer Mobile number')
#
# 	mobile_number = mobile_number_validation(doc.get('customer_mobile_number'))
# 	code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=9))
# 	customer = frappe.get_doc(doc.get('doctype'), doc.get('name'))
# 	customer.append('customer_text_code', {'code': code})
# 	customer.save()
#
# 	msg = 'a'
# 	# msg = 'abc '
# 	site = 'https://abna-alarabiya.com'
# 	# site = '192.168.100.217:8000' #frappe.local.site  # 'https://abna-alarabiya.com'
# 	secode = '6287txtava725@'
# 	msg = msg + '<br>{0}/customer_address?add_rqst_id={1}{2}{3}'.format(site, code, secode, doc.get('name'))
# 	frappe.msgprint(cstr(len(msg)))
# 	send_sms([mobile_number], msg)
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
# def create_contact(self):
# 	if not self.lead_name:
# 		self.set_lead_name()
#
# 	names = self.lead_name.strip().split(" ")
# 	if len(names) > 1:
# 		first_name, last_name = names[0], " ".join(names[1:])
# 	else:
# 		first_name, last_name = self.lead_name, None
#
# 	contact = frappe.new_doc("Contact")
# 	contact.update({
# 		"first_name": first_name,
# 		"last_name": last_name,
# 		"salutation": self.salutation,
# 		"gender": self.gender,
# 		"designation": self.designation,
# 		"company_name": self.company_name,
# 	})
#
# 	if self.email_id:
# 		contact.append("email_ids", {
# 			"email_id": self.email_id,
# 			"is_primary": 1
# 		})
#
# 	if self.customer_mobile_number:
# 		contact.append("phone_nos", {
# 			"phone": self.customer_mobile_number,
# 			"is_primary_mobile_no":1
# 		})
#
# 	contact.insert(ignore_permissions=True)
#
# 	return contact
#
#
# @frappe.whitelist()
# def make_customer_from_lead(source_name, target_doc=None):
# 	def set_missing_values(source, target):
# 		if source.payment_type == 'Cash':
# 			target.payment_cash = 1
# 		elif source.payment_type == 'Credit':
# 			target.payment_credit = 1
#
# 		if source.customer_type == 'Company' and source.payment_type == 'Cash':
# 			target.is_parent_customer_cf = 1
#
# 	doclist = get_mapped_doc("Lead", source_name,
# 		{"Lead": {
# 			"doctype": "Customer",
# 			"field_map": {
# 				"name": "lead_name",
# 				"lead_name": "customer_name"
# 			}
# 		}}, target_doc, set_missing_values)
#
# 	return doclist
#
# @frappe.whitelist()
# def make_opportunity_from_lead(source_name, target_doc=None):
#
# 	# def set_missing_values(source, target):
# 	# 	_set_missing_values(source, target)
#
# 	target_doc = get_mapped_doc("Lead", source_name,
# 		{"Lead": {
# 			"doctype": "Opportunity",
# 			"field_map": {
# 				"doctype": "opportunity_from",
# 				"name": "party_name",
# 				"lead_name": "contact_display",
# 				"company_name": "customer_name",
# 				"email_id": "contact_email",
# 				"mobile_no": "contact_mobile"
# 			}
# 		}}, target_doc)
# 		# }}, target_doc, set_missing_values)
#
# 	return target_doc
