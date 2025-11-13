// Copyright (c) 2022, Furqan Asghar and contributors
// For license information, please see license.txt

frappe.ui.form.on('Ava Ecommerce Settings', {
	refresh (frm) {
		frm.trigger("check_enabled");
		frm.set_query("tax_account", ()=>{
			return {
				"filters": {
					"company": frappe.defaults.get_default("company"),
					"is_group": 0
				}
			};
		});
	},
//	Ava Ecommerce Settings

	enable_woocommerce_sync (frm) {
		frm.trigger("check_enabled");
	},

	check_enabled (frm) {
		frm.set_df_property("woocommerce_server_url", "reqd", frm.doc.enable_woocommerce_sync);
//		frm.set_df_property("woocommerce_user", "reqd", frm.doc.enable_woocommerce_sync);
//		frm.set_df_property("woocommerce_password", "reqd", frm.doc.enable_woocommerce_sync);
		frm.set_df_property("api_consumer_key", "reqd", frm.doc.enable_woocommerce_sync);
		frm.set_df_property("api_consumer_secret", "reqd", frm.doc.enable_woocommerce_sync);
		frm.set_df_property("api_access_token_salla", "reqd", frm.doc.enable_woocommerce_sync);
	}
});
