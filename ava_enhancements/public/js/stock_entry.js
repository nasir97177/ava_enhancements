// Copyright (c) 2017, Frappe Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on('Stock Entry', {
	onload_post_render: function(frm) {
		frappe.db.get_value('Stock Settings', {name: 'Stock Settings'}, 'sample_retention_warehouse', (r) => {
			if (r.sample_retention_warehouse) {
			    var filters = [
			        ["Warehouse", 'company', '=', frm.doc.company],
			        ["Warehouse", "is_group", "=",0],
			        ['Warehouse', 'name', '!=', r.sample_retention_warehouse]
			   ]

			   frm.set_query("from_warehouse", function() {
                    return {
                        query: "ava_enhancements.main.get_custom_allowed_s_warehouse",
                        filters: filters
                    };
                });

               frm.set_query("s_warehouse", "items", function() {
                    console.log('clicked s_warehouse');
                    return {
                        query: "ava_enhancements.main.get_custom_allowed_s_warehouse",
                        filters: filters
                    };
                });
            }
            set_target_warehouses(frm);
		});
	},

});

frappe.ui.form.off("Stock Entry", "add_to_transit");
frappe.ui.form.on('Stock Entry', {
	add_to_transit: function (frm) {
	     if(frm.doc.add_to_transit && frm.doc.purpose=='Material Transfer') {
			frm.set_value('to_warehouse', '');
			frm.fields_dict.to_warehouse.get_query = function() {
				return {
				    query: "ava_enhancements.main.get_custom_allowed_t_warehouse_transits",
					filters:{
						'company': frm.doc.company,
						'is_group': 1,
						'warehouse_type' : 'Transit'
					}
				};
			};
			frm.trigger('set_transit_warehouse');
		}
		else {
		    set_target_warehousess(frm);
		}
    }
});

var set_target_warehousess = function(frm) {
    frm.set_query("to_warehouse", function() {
        return {
            query: "ava_enhancements.main.get_custom_allowed_t_warehouse",
            filters: [
                ["Warehouse", 'company', '=', frm.doc.company],
                ["Warehouse", "is_group", "=",0]
            ]
        };
    });

    frm.set_query("t_warehouse", "items", function() {
        return {
            query: "ava_enhancements.main.get_custom_allowed_t_warehouse",
            filters: [
                ["Warehouse", 'company', '=', frm.doc.company],
                ["Warehouse", "is_group", "=",0]
           ]
        };
    });
}
