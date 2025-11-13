// Copyright (c) 2022, Furqan Asghar and contributors
// For license information, please see license.txt

frappe.ui.form.on('Ava Branches and Salesman Fund Accounts Settings', {
	onload: function(frm) {
		if (frm.doc.fund_account && frm.doc.fund_account_parent) {
			frm.set_query('cash_accounts', function(doc, cdt, cdn) {
				return {
					"filters": {
						"name": ['!=', frm.doc.fund_account],
						"parent_account": frm.doc.fund_account_parent,
						"is_group": 0
					}
				};
			});
		}
	},
	fund_account_parent: function(frm) {
		frm.set_query('fund_account', function(doc, cdt, cdn) {
			return {
				"filters": {
					"parent_account": frm.doc.fund_account_parent,
					"is_group": 0
				}
			};
		});
	},
	fund_account: function(frm) {
		frm.set_query('cash_accounts', function(doc, cdt, cdn) {
			return {
				"filters": {
					"name": ['!=', frm.doc.fund_account],
					"parent_account": frm.doc.fund_account_parent,
					"is_group": 0
				}
			};
		});
	}
});
