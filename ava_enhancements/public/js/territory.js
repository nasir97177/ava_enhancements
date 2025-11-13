frappe.ui.form.on('Territory', {
	fence: function(frm) {
	    console.log('fence updated')
	    if (frm.doc.fence) {
	        frappe.call({
	            method: 'ava_enhancements.main.territory_fence_validation',
	            args: {
	                'fence': frm.doc.fence
	            },
	            callback: function(r) {
//	                if (r.message == 'one_fence_allowed') {
//	                    frappe.msgprint('Only one Polygon or Rectangle is allowed');
//	                    frm.set_value('fence', '{"type":"FeatureCollection","features":[]}')
//	                }
	                if (r.message == 'only_poly_allowed') {
	                    frappe.msgprint('Only Polygon or Rectangle are allowed');
	                    frm.set_value('fence', '{"type":"FeatureCollection","features":[]}')
	                }
	            }
	        })
            frappe.call({
                method: 'ava_enhancements.geofencing.territories_intersecting',
                    args: {
                        'territory': frm.doc.name,
                        'geo_shape': frm.doc.fence,
                        'customer_groups': frm.doc.customer_groups
                    },
                    callback: function(r) {
                        if (r.message) {
                            frm.set_value('fence', '{"type":"FeatureCollection","features":[]}');
                            frappe.throw('Following Territories were intersecting this territory: ' + r.message);
                        }
                    }
                })
	    }
	}
})
