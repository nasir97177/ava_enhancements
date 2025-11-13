frappe.ui.form.on('Customer', {
    onload: function(frm) {
        if (!frm.is_new() && frm.doc.name) {
            frm.refresh_fields('customer_branch_detail_cf');
            frappe.call({
                method: "ava_rebate.api.get_customer_branch_list",
                args: {
                        customer_code: frm.doc.name,
                },
                callback: function (r) {
                    if (!r.exc) {
                        let customer_branch_list = r.message
                        if (customer_branch_list) {
                            frm.set_query("branch_name", () => {
                                return {
                                    "filters": {
                                        name: ['in', customer_branch_list]
                                    }
                                }
                            })
                            frm.refresh_field('branch_name')
                        } else {
                            frappe.msgprint(__('No branch found for {0}', [frm.doc.customer]))
                        }
                    }
                }
            });
       }
    },

	new_address_for_branch: function(frm) {
	    frappe.new_doc("Address", {'customer_branch': cur_frm.doc.branch_name, 'address_title': cur_frm.doc.name + '-' + cur_frm.doc.branch_name});
	},

	pick_this_location: function(frm) {
	    function locationRecieved(position){
            var longitude= position.coords.longitude;
            var latitude= position.coords.latitude;
            frm.set_value('longitude',longitude);
            frm.set_value('latitude',latitude);

            frm.set_df_property('my_location','options','<div class="mapouter"><div class="gmap_canvas"><iframe width=100% height="200" id="gmap_canvas" src="https://maps.google.com/maps?q='+latitude+','+longitude+'&t=&z=17&ie=UTF8&iwloc=&output=embed" frameborder="0" scrolling="no" marginheight="0" marginwidth="0"></iframe><style>.mapouter{position:relative;text-align:right;height:210px;width:100%;}</style><style>.gmap_canvas {overflow:hidden;background:none!important;height:200px;width:100%;}</style></div></div>');
            frm.refresh_field('my_location');
        }

        function locationNotRecieved(positionError){
	        frm.set_value('longitude','');
	        frm.set_value('latitude','');
            frappe.msgprint(positionError.message + ': Please check Location', 'Location Service Error');
        }
	    if(navigator.geolocation){
	        navigator.geolocation.getCurrentPosition(locationRecieved,locationNotRecieved,{ enableHighAccuracy: true});
	    }
    },

    create_address_for_this_location: function(frm) {
        if (frm.doc.longitude && frm.doc.latitude) {
            frappe.call({
                'method': 'ava_enhancements.main.create_address_from_customer',
                args: {
                    'customer_name': frm.doc.name,
                    'longitude': frm.doc.longitude,
                    'latitude': frm.doc.latitude,
                },
                callback: function(r) {
                    if (!r.exc) {
                        var status = r.message.status;
                        var data = r.message.data;
                        if (status == 'failed') {
                            frappe.msgprint(cstr(data), 'Fence not found in Territories');
                        }
                        else if (status == 'success') {
                            frappe.msgprint(data, 'Address created');
                            frm.set_value('longitude','');
                            frm.set_value('latitude','');
                            frm.reload_doc();
                        }
                    }
                }
            })
        }
    }
})
