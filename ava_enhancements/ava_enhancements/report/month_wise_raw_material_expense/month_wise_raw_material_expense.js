// Copyright (c) 2025, Furqan Asghar and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Month Wise Raw Material Expense"] = {
    "filters": []
};

// Make sure the financial statements JS is loaded first
frappe.require("assets/erpnext/js/financial_statements.js", function() {
    
    // Extend your custom report with financial statements functionality (optional)
    frappe.query_reports["Month Wise Raw Material Expense"] = $.extend(
        {}, 
        erpnext.financial_statements
    );

    // Add dimensions if needed (optional, adjust first parameter to your report name)
    erpnext.utils.add_dimensions('Month Wise Raw Material Expense', 10);

    // Add custom filters
    frappe.query_reports["Month Wise Raw Material Expense"]["filters"].push(
        {
            "fieldname": "project",
            "label": __("Project"),
            "fieldtype": "MultiSelectList",
            get_data: function(txt) {
                return frappe.db.get_link_options('Project', txt);
            }
        },
        {
            "fieldname": "include_default_book_entries",
            "label": __("Include Default Book Entries"),
            "fieldtype": "Check",
            "default": 1
        }
    );
});
