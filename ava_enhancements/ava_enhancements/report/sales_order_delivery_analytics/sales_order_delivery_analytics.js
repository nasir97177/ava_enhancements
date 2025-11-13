// Copyright (c) 2022, Furqan Asghar and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Sales Order Delivery Analytics"] = {
	"filters": [
		{
			fieldname: "tree_type",
			label: __("Tree Type"),
			fieldtype: "Select",
			options: ["Territory", "Warehouse", "Customer Group"],
			default: "Territory",
			reqd: 1
		},
		{
			fieldname: "territory",
			label: __("Territory"),
			fieldtype: "Link",
			options: "Territory",
//			reqd: 1
		},
		{
			fieldname: "warehouse",
			label: __("Warehouse"),
			fieldtype: "Link",
			options: "Warehouse",
//			reqd: 1
		},
		{
			fieldname: "customer_group",
			label: __("Customer Group"),
			fieldtype: "Link",
			options: "Customer Group",
//			default: 'HOME DELIVERY HD',
//			reqd: 1
		},
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: frappe.defaults.get_user_default("year_start_date"),
			reqd: 1
		},
		{
			fieldname:"to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: frappe.defaults.get_user_default("year_end_date"),
			reqd: 1
		},
		{
			label: __("Charts Based On"),
			fieldname:"charts_based_on",
			fieldtype: "Select",
			options: ["Count", "Volume", "Value"],
			default: "Count"
		},
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("Company"),
			reqd: 1
		},
	],
};
