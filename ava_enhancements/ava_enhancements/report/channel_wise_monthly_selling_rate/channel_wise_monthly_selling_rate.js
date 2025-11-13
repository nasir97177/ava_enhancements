// Copyright (c) 2025, Furqan Asghar and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Channel Wise Monthly Selling Rate"] = {
	"filters": [

	]
};
frappe.query_reports["Channel Wise Monthly Selling Rate"] = {
    filters: [
        {
            fieldname: "from_date",
            label: "From Date",
            fieldtype: "Date",
            reqd: 1,
            default: "2025-01-01"  // YYYY-MM-DD format
        },
        {
            fieldname: "to_date",
            label: "To Date",
            fieldtype: "Date",
            reqd: 1,
            default: "2025-12-31"  // YYYY-MM-DD format
        },
		{
    "fieldname": "year",
    "label": "Year",
    "fieldtype": "Select",
    "options": "\n2023\n2024\n2025\n2026",
    "default": "2025",
    "reqd": 1
  },
        {
            fieldname: "company",
            label: "Company",
            fieldtype: "Link",
            options: "Company"
        }
    ],

    // formatter: function(value, row, column, data, default_formatter) {
    //     value = default_formatter(value, row, column, data);
    //     if (data && data.item_code === "Total") {
    //         value = `<strong>${value}</strong>`;
    //     }
    //     return value;
    // }
};
