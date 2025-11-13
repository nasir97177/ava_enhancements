frappe.ui.form.on('Sales Order', {
	onload(frm) {
       if (!frm.is_new() && frm.doc.customer_address) {
            frappe.call({
                method: "ava_enhancements.main.get_customer_location",
                args: {
                        customer_address: frm.doc.customer_address,
                },
                callback: function (r) {
                    if (!r.exc) {
                        var customer_coords = r.message;
                        var hyper_link = ''
                        if (customer_coords)  {
                            var url = 'http://maps.google.com/maps?z=18&q=' + customer_coords['lat'] + ',' + customer_coords['lng']
                            hyper_link = '<button class="btn btn-xs btn-default"><a href=' + '"' +url + '"' + ' target="_blank">Goto Customer Location</a><svg class="icon  icon-md" style=""><use class="" href="#icon-users"></use></svg></button>'
//                            console.log(hyper_link)
                            frm.set_df_property('customer_location', 'options', hyper_link);
                        }
                        else {
                            frm.set_df_property('customer_location', 'options', hyper_link);
                        }
                    }
                }
            });
       }
	},

	before_save: function(frm) {
	    set_territory_warehouse_sales_team_location(frm);
	},

	customer_address: function(frm) {
	    set_territory_warehouse_sales_team_location(frm);
	}
})

var set_territory_warehouse_sales_team_location = function(frm) {
    if (frm.doc.customer_address) {
        frappe.call({
            'method': 'ava_enhancements.main.fetch_territory_manager_and_warehouse_for_address',
            args:{
                'address': frm.doc.customer_address
            },
            callback: function(r){
                if (!r.exc) {
                    var message = r.message;

                    if (message.default_warehouse && message.territory_manager) {
                        frm.set_value('set_warehouse', message.default_warehouse);
                        frm.set_value('territory', message.name);

                        frm.clear_table('sales_team');
                        var new_row = frm.add_child('sales_team');
                        new_row.doctype = 'Sales Team';
                        new_row.allocated_percentage = 100;
                        new_row.sales_person = message.territory_manager;

                        frm.refresh_field('set_warehouse');
                        frm.refresh_field('territory');
                        frm.refresh_field('sales_team');
                    }
                    else {
                        frm.set_value('set_warehouse', '');
                        frm.set_value('territory', '');
                        frm.clear_table('sales_team');

                        frm.refresh_field('set_warehouse');
                        frm.refresh_field('territory');
                        frm.refresh_field('sales_team');

                        frappe.throw('Warehouse or Territory Manager not set for the Territory');
                    }
                }
            }
        })
    }
//    else {
//        frm.set_value('set_warehouse', '');
//        frm.set_value('territory', '');
//        frm.clear_table('sales_team');
//
//        frm.refresh_field('set_warehouse');
//        frm.refresh_field('territory');
//        frm.refresh_field('sales_team');
//
//        frappe.throw('Address not set');
//    }
}
