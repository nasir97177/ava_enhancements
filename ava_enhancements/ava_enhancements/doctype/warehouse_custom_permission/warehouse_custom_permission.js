// Copyright (c) 2022, Furqan Asghar and contributors
// For license information, please see license.txt

frappe.ui.form.on('Warehouse Custom Permission', {
//	 refresh: function(frm) {
//
//	 },
});


frappe.ui.form.on('Allowed Warehouse', {
     create_perm: function(frm, cdt, cdn) {
        create_custom_perm(frm, cdt, cdn);
    },
//    create_delivery_note_perm: function(frm, cdt, cdn) {
//        create_custom_perm(frm, cdt, cdn, 'delivery_note_perm');
//    },
    remove_perm: function(frm, cdt, cdn) {
        remove_custom_perm(frm, cdt, cdn);
    },
//    remove_delivery_note_perm: function(frm, cdt, cdn) {
//        remove_custom_perm(frm, cdt, cdn, 'delivery_note_perm');
//    },
})


var create_custom_perm = function(frm, cdt, cdn, field) {
    var row = locals[cdt][cdn];
    frappe.call({
        'method': 'ava_enhancements.ava_enhancements.doctype.warehouse_custom_permission.warehouse_custom_permission.create_custom_perm',
        args:{
            user: frm.doc.user,
            row: row
        },
        callback: function(r){
            if (!r.exc) {
                var perm = r.message.perm;
                if (perm) {
                    frm.reload_doc();
                }
            }
        }
    })
}


var remove_custom_perm = function(frm, cdt, cdn, field) {
    var row = locals[cdt][cdn];
    frappe.call({
        'method': 'ava_enhancements.ava_enhancements.doctype.warehouse_custom_permission.warehouse_custom_permission.remove_custom_perm',
        args:{
            row: row
        },
        callback: function(r){
            if (!r.exc) {
                var success = r.message.success;
                if (success) {
                    frm.reload_doc();
                }
            }
        }
    })
}

