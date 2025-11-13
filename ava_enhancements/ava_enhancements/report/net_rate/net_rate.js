// Copyright (c) 2025, Furqan Asghar and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Net Rate"] = {
	"filters": [

	]
};
frappe.query_reports["Net Rate"] = {
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
            fieldname: "company",
            label: "Company",
            fieldtype: "Link",
            options: "Company"
        }
    ],

    formatter: function(value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);
        if (data && data.item_code === "Total") {
            value = `<strong>${value}</strong>`;
        }
        return value;
    },

    onload: function(report) {
        report.page.set_title("Net Rate");
    },

    on_refresh: function(report) {
        // Clear existing chart if any
        if (report.chart) {
            report.chart.clear();
        }

        if(report.data && report.chart_data){
            report.chart = new frappe.Chart("#chart-container", {
                data: report.chart_data.data,
                type: report.chart_data.type,
                height: 300,
                colors: report.chart_data.colors,
                axisOptions: {
                    xIsSeries: true
                },
                tooltipOptions: {
                    formatTooltipX: d => d,
                    formatTooltipY: d => d.toLocaleString()
                }
            });
        }
    }
};
