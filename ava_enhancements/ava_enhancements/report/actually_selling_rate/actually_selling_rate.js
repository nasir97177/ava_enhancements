// Copyright (c) 2025, Furqan Asghar and contributors
// For license information, please see license.txt
/* eslint-disable */

// frappe.query_reports["Actually Selling Rate"] = {
// 	"filters": [

// 	]
// };
frappe.query_reports["Actually Selling Rate"] = {
    filters: [
        {
            fieldname: "from_date",
            label: "From Date",
            fieldtype: "Date",
            reqd: 1,
            default: "2025-01-01"
        },
        {
            fieldname: "to_date",
            label: "To Date",
            fieldtype: "Date",
            reqd: 1,
            default: "2025-12-31"
        },
        {
            fieldname: "year",
            label: "Year",
            fieldtype: "Select",
            options: (() => {
                const currentYear = new Date().getFullYear();
                return ["", currentYear - 1, currentYear, currentYear + 1, currentYear + 2].join("\n");
            })(),
            default: new Date().getFullYear().toString(),
            reqd: 1
        },
        {
            fieldname: "company",
            label: "Company",
            fieldtype: "Link",
            options: "Company",
            default: frappe.defaults.get_user_default("Company")
        }
    ],

    formatter: function(value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);
        if (data && (data.item_code === "Total" || data.name === "Total")) {
            value = `<strong>${value}</strong>`;
        }
        return value;
    }
};
