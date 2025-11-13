frappe.ui.form.on('Asset', {
	onload: function(frm) {
		frm.add_fetch('company_name', 'accumulated_depreciation_account', 'accumulated_depreciation_account');
		frm.add_fetch('company_name', 'depreciation_expense_account', 'depreciation_expense_account');

		frm.set_query('fixed_asset_account', function(doc, cdt, cdn) {
			var d  = locals[cdt][cdn];
			return {
				"filters": {
					"account_type": "Fixed Asset",
					"root_type": "Asset",
					"is_group": 0,
					"company": d.company_name
				}
			};
		});

		frm.set_query('accumulated_depreciation_account', function(doc, cdt, cdn) {
			var d  = locals[cdt][cdn];
			return {
				"filters": {
					"account_type": "Accumulated Depreciation",
					"is_group": 0,
					"company": d.company_name
				}
			};
		});

		frm.set_query('depreciation_expense_account', function(doc, cdt, cdn) {
			var d  = locals[cdt][cdn];
			return {
				"filters": {
					"root_type": ["in", ["Expense", "Income"]],
					"is_group": 0,
					"company": d.company_name
				}
			};
		});

		frm.set_query('capital_work_in_progress_account', function(doc, cdt, cdn) {
			var d  = locals[cdt][cdn];
			return {
				"filters": {
					"account_type": "Capital Work in Progress",
					"is_group": 0,
					"company": d.company_name
				}
			};
		});

	}
});

frappe.ui.form.on('Depreciation Schedule', {
     before_schedules_remove: function(frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        if (row.journal_entry) {
            frappe.throw('Cannot delete row with Journal Entry');
        }
    }
})


frappe.ui.form.off("Depreciation Schedule", "make_depreciation_entry");
frappe.ui.form.on('Depreciation Schedule', {
	make_depreciation_entry: function(frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		if (!row.journal_entry) {
		    frappe.show_progress(__("Creating Journal Entries"), 50, 100, 'Please wait');
			frappe.call({
				method: "erpnext.assets.doctype.asset.depreciation.make_depreciation_entry",
				args: {
					"asset_name": frm.doc.name,
					"date": row.schedule_date
				},
				callback: function(r) {
					frappe.model.sync(r.message);
					frm.refresh();
					frappe.hide_progress();
				}
			})
		}
	},
	depreciation_amount: function(frm, cdt, cdn) {
		erpnext.asset.set_accumulated_depreciation(frm);
	}
})
