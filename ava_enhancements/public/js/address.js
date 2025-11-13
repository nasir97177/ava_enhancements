frappe.ui.form.on('Address', {
	geolocation: function(frm) {
        var customer_name;
        $.each(cur_frm.doc.links, function(i, d) { if (d.link_doctype == 'Customer'){ customer_name = d.link_name} });

	    if (frm.doc.geolocation && customer_name) {
	        frappe.call({
	            method: 'ava_enhancements.main.get_address_territory_from_geolocation',
	            args: {
	                'geolocation': frm.doc.geolocation,
	                'customer_name': customer_name
	            },
	            callback: function(r) {
	                if (r.message == 'invalid_location') {
	                    frappe.msgprint('invalid_location');
	                    frm.set_value('geolocation', '{"type":"FeatureCollection","features":[]}')
	                }
	                else if (!r.exc && r.message.success) {
	                    var city = r.message.city;
	                    var postal_code = r.message.postal_code;
	                    var address_line1 = r.message.address_line1;
	                    var territory = r.message.territory;

    	                frm.set_value('city', city);
    	                frm.set_value('pincode', postal_code);
    	                frm.set_value('address_line1', address_line1);
    	                if (territory) {
    	                    frm.set_value('territory', territory);
    	                    frm.set_value('coverage_area', territory);
    	                }
    	                else {
    	                    frm.set_value('territory', '');
    	                    frm.set_value('coverage_area', '');
    	                    frappe.msgprint('Location is out of Fences coverage, please set a fence for this location', 'Automatic Territory setting failed');
    	                }
	                }
	            }
	        })
	    }
	    else {
	        frappe.msgprint('no location or customer');
	    }
	},

	after_save: function(frm){
	    if (frm.doc.customer_branch) {
	        frappe.call({
	            'method': 'ava_enhancements.main.set_branch_and_territory',
	            args:{
                    'customer_branch': frm.doc.customer_branch,
                    'branch_address': frm.doc.name,
                    'territory': frm.doc.territory
                },
                callback: function(r){
                    if (!r.exc) {
                        console.log('saved')
                    }
                }
            })
	    }
	},

	add_location_to_map: function(frm){
	    if (frm.doc.google_plus_code) {
	        frappe.call({
	            'method': 'ava_enhancements.main.pick_location_from_pluscode',
	            args:{
                    'google_plus_code': frm.doc.google_plus_code
                },
                callback: function(r){
                    if (!r.exc) {
                        var leaflet_geolocation = r.message;
                        frm.set_value('geolocation', leaflet_geolocation);
                        frm.refresh_field('geolocation');
//                        console.log(leaflet_geolocation)
                    }
                }
            })
        }
	},
})
