import frappe
from frappe.utils import cstr

import json
import requests
import geopy.distance
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

def ava_reverse_geocoding(geo_coords):
    '''
        Description: This function get geo address by reverse geocoding customer geolocation using google Maps Geocode API

        param/Input:  Geo Coordinates > geo_coords (dict)

        return/Output : Address of Geo Coordinates > address_dict (dict)
    '''

    lat, lng = cstr(geo_coords.get('lat')), cstr(geo_coords.get('lng')) #geo_coords.get('lan'), geo_coords.get('lat')

    address_dict = {}
    wc_config = frappe.get_doc("Ava Ecommerce Settings")
    key = wc_config.get_password(fieldname="api_key_google_maps")
    url = 'https://maps.googleapis.com/maps/api/geocode/json?latlng={0},{1}&key={2}'.format(lat, lng, key)
    allow_street_types = ['street_address', 'premise', 'subpremise', 'route']
    #
    response = requests.get(url)
    if response.status_code == 200:

        response = response.json()

        if response.get('results'):
            results = response.get('results')
            city_alt = ''
            for d in results:
                if d.get('types') == [ "locality", "political" ]:
                    for addr_comp in d.get('address_components'):
                        if addr_comp.get('types') == [ "locality", "political" ]:
                            address_dict['city'] = d.get('address_components')[0].get('long_name')

                if d.get('types') == [ "political", "sublocality", "sublocality_level_1" ]:
                    for addr_comp in d.get('address_components'):
                        if addr_comp['types'] == [ "political", "sublocality", "sublocality_level_1" ]:
                            address_dict['district'] = d.get('address_components')[0].get('long_name')

                if d.get('types') == [ "postal_code" ]:
                    for addr_comp in d.get('address_components'):
                        if addr_comp['types'] == [ "postal_code" ]:
                            address_dict['postal_code'] = addr_comp['long_name']

                if d.get('types') == ['administrative_area_level_2', 'political']:
                    for addr_comp in d.get('address_components'):
                        if addr_comp['types'] == ['administrative_area_level_2', 'political']:
                            city_alt = addr_comp['long_name']

            if not address_dict.get('city') and city_alt:
                address_dict['city'] = city_alt

        elif response.get('error_message'):
            error_message = response.get('error_message')
            frappe.log_error(error_message, "Error: Google API error")
            return

    return address_dict


def get_geolocation_for_leaflet(geo_coords):
	'''
        Description: Take geolocation points (lat, lng) and convert to geolocation format for leaflet

        param/Input:  Geo Coordinates > geo_coords (dict)

        return/Output : Leaflet Formatted geolocation (dict)
	'''
	geolocation = ''
	if geo_coords:
		lat, lng = cstr(geo_coords.get('lat')), cstr(geo_coords.get('lng'))
		geolocation = '{"type":"FeatureCollection","features":[{"type":"Feature","properties":{},"geometry":{"type":"Point","coordinates":[' + lng +','+ lat + ']}}]}'
	return geolocation


def is_location_inside_fence(geo_point, geo_shape):
    '''
	Description: This function check in a geolocation point lies inside a given Polygon, if exist return True else False

	param/Input: Geopoint > geo_point (Point), Polygon shape > geo_shape (Polygon)

	return/Output : inside_fence (bool)
	'''
    inside_fence = False
    if geo_point.within(geo_shape) and geo_shape.contains(geo_point):
        inside_fence = True
    return inside_fence


@frappe.whitelist()
def get_coverage_area(geolocation, customer_group):
    '''
        Description: Loop all the territories with Fence and check if given location exist inside any fence

        param/Input: geolocation

        return/Output : (coverage_area_exist, msg) => (tuple => (bool, str)
	'''

    coverage_area_exist = False
    customer_location = json.loads(geolocation)['features'][0]['geometry']
    customer_location_type = customer_location.get('type')
    customer_location_coords = Point(customer_location.get('coordinates'))

    if customer_location_type != 'Point':
        msg = 'Geofencing Expection, Customer location Should be a Point location for geofencing'
        return coverage_area_exist, msg

    territories = frappe.db.get_list('Territory', fields=['name', 'fence'], filters={'fence': ['!=', '']})
    for territory in territories:
        territory_name = territory.name
        territory_geometry = json.loads(territory.fence)
        fence_features = territory_geometry.get('features')

        for d in fence_features:
            fence_geometry = d.get('geometry')
            geometry_type = fence_geometry.get('type')
            geometry_coords = fence_geometry.get('coordinates')

            if geometry_type == 'Polygon':
                geo_shape = Polygon(geometry_coords[0])
                check_is_location_inside_fence = is_location_inside_fence(customer_location_coords, geo_shape)
                customer_groups = [d.customer_group for d in frappe.get_doc('Territory', territory_name).customer_groups]
                if check_is_location_inside_fence and customer_group in customer_groups:
                    coverage_area_name = territory_name
                    coverage_area_exist = True
                    break

        if coverage_area_exist:
            break

    if coverage_area_exist:
        return coverage_area_exist, coverage_area_name
    else:
        cust_coords = customer_location_coords
        msg = 'Geofencing Expection, No Fence set for this location {0}'.format((cust_coords.y, cust_coords.x))
        return coverage_area_exist, msg


@frappe.whitelist()
def get_possible_territories(geolocation):
    '''
        Description: Loop all the territories with Fence and check if given location exist inside any fence

        param/Input: geolocation

        return/Output : (coverage_area_exist, msg) => (tuple => (bool, str)
	'''

    possible_territories = []
    customer_location = json.loads(geolocation)['features'][0]['geometry']
    customer_location_type = customer_location.get('type')
    customer_location_coords = Point(customer_location.get('coordinates'))

    territories = frappe.db.get_list('Territory', fields=['name', 'fence'], filters={'fence': ['!=', '']})
    for territory in territories:
        territory_name = territory.name
        territory_geometry = json.loads(territory.fence)
        fence_features = territory_geometry.get('features')

        for d in fence_features:
            fence_geometry = d.get('geometry')
            geometry_type = fence_geometry.get('type')
            geometry_coords = fence_geometry.get('coordinates')

            if geometry_type == 'Polygon':
                geo_shape = Polygon(geometry_coords[0])
                check_is_location_inside_fence = is_location_inside_fence(customer_location_coords, geo_shape)
                if check_is_location_inside_fence:
                    possible_territories.append(territory_name)

    return possible_territories

@frappe.whitelist()
def territories_intersecting(territory, geo_shape, customer_groups):
    '''
        Description: A validation for Territory; this function checks whether a given fence in a Territory intersect with some previously created Territory Fence

        param/Input: Territory > territory (str), Leaflet Polygon > geo_shape (dict)

        return/Output : Comma seperated string of intersecting_territories list (str)
	'''

    features = json.loads(geo_shape)
    customer_groups = [d.get('customer_group') for d in json.loads(customer_groups)]

    if features.get('features'):
        feature  = features['features']
        if len(feature) == 1:
            feature_type = feature[0]['geometry']['type']
            if feature_type == 'Polygon':
                main_feature_coords = Polygon(feature[0]['geometry']['coordinates'][0])

                existing_territories = frappe.db.get_list('Territory', fields=['name', 'fence'], filters={'fence': ['!=', ''], 'name': ['!=', territory] })
                intersecting_territories = []

                for ex_territory in existing_territories:
                    geometry = json.loads(ex_territory.fence)
                    fence = geometry.get('features')
                    if len(fence) == 1:
                        geometry = fence[0]['geometry']
                        territory_name = ex_territory.name
                        ex_terr_cust_grp = [d.customer_group for d in frappe.get_doc('Territory', territory_name).customer_groups]

                        geometry_type = geometry['type']
                        geometry_coords = Polygon(geometry['coordinates'][0])

                        if main_feature_coords.intersects(geometry_coords) and len(set(ex_terr_cust_grp) & set(customer_groups)) > 0:
                            intersecting_territories.append(territory_name)

                return ", ".join(intersecting_territories)
