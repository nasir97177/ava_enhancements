// Copyright (c) 2022, Furqan Asghar and contributors
// For license information, please see license.txt

frappe.ui.form.on('Ava Bulk Cancel', {
	 doctype_name: function(frm) {
	    if (frm.doc.doctype_name) {
	        $.each(frm.doc.to_cancel_entries, function(i, row) {
				row.link_doctype = frm.doc.doctype_name;
	        })
           refresh_field("to_cancel_entries");
	    }
	 },
//	 cancel_all: function(frm) {
//			frappe.call({
//				method: "ava_enhancements.ava_enhancements.doctype.ava_bulk_cancel.ava_bulk_cancel.cancel_all",
//				freeze: true,
//				freeze_message: __('Cancelling Entries'),
//				args: {
//				    "doctype": frm.doc.doctype,
//					"docname": frm.doc.name
//				},
//				callback: function(r) {
//					frappe.model.sync(r.message);
//					frm.refresh();
//				}
//			})
//	 }
});
