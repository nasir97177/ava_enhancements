frappe.query_reports["Current Stock Balance"] = {
    "filters": [
        {
            "fieldname": "company",
            "label": __("Company"),
            "fieldtype": "Link",
            "width": "80",
            "options": "Company",
            "default": frappe.defaults.get_default("company")
        },
        {
            "fieldname":"from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "width": "80",
            "reqd": 1,
            "default": frappe.datetime.get_today()
        },
        {
            "fieldname":"to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "width": "80",
            "reqd": 1,
            "default": frappe.datetime.get_today()
        },
        {
            "fieldname": "include_uom",
            "label": __("Include UOM"),
            "fieldtype": "Link",
            "options": "UOM"
        },
        {
            "fieldname": "show_variant_attributes",
            "label": __("Show Variant Attributes"),
            "fieldtype": "Check"
        },
        {
            "fieldname": 'show_stock_ageing_data',
            "label": __('Show Stock Ageing Data'),
            "fieldtype": 'Check'
        }
    ],

    "formatter": function (value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);

        if (column.fieldname == "out_qty" && data && data.out_qty > 0) {
            value = "<span style='color:red'>" + value + "</span>";
        }
        else if (column.fieldname == "in_qty" && data && data.in_qty > 0) {
            value = "<span style='color:green'>" + value + "</span>";
        }

        return value;
    },

    // Initialize the chart property
    "chart": {
        "data": {
            "labels": [],
            "datasets": [
                {
                    "name": "Balance Qty",
                    "values": []
                }
            ]
        },
        "type": "bar",
        "height": 300
    },

    // Populate the chart after report data is loaded
    "onload_post_render": function(report) {
        const data = report.data;
        if (!data || !data.length) return;

        let branch_qty = {};

        data.forEach(d => {
            let branch = d.branch || 'Other';
            branch_qty[branch] = (branch_qty[branch] || 0) + (d.bal_qty || 0);
        });

        report.chart.data.labels = Object.keys(branch_qty);
        report.chart.data.datasets[0].values = Object.values(branch_qty);

        report.show_chart();
    }
};
