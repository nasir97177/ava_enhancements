// Copyright (c) 2023, Furqan Asghar and contributors
// For license information, please see license.txt

// frappe.ui.form.on('AVA Geidea Closing', {
// 	// refresh: function(frm) {

// 	// }
// });
frappe.ui.form.on('AVA Geidea Closing', {
    // setup: function(frm) {
    //     frm.set_df_property('sales_invoice_reference', 'read_only', 1);
    //     frm.set_df_property('payment_entry_reference', 'read_only', 1);
    //     frm.set_df_property('mode_of_payment', 'read_only', 1);
    // },

    validate: function(frm) {
        if (!(frm.doc.sales_invoice_reference || frm.doc.payment_entry_reference)) {
            frappe.throw('No Invoices/Payments meeting criteria');
        }
    },

	fetch_geidea_payment: function(frm) {
	    if (frm.doc.date && frm.doc.pos_profile) {
            frappe.call({
                'method': 'ava_enhancements.ava_enhancements.doctype.ava_geidea_closing.ava_geidea_closing.fetch_geidea_payments',
                // 'method': 'ava_enhancements.ava_enhancements.doctype.ava_cash_collection.ava_cash_collection.fetch_invoices_payments',
                args:{
                    date: frm.doc.date,
                    pos_profile: frm.doc.pos_profile
                },
                callback: function(r){
                    if (!r.exc) {
                        var invoices = r.message.invoices;
                        var payments = r.message.payments;
                        var mode_of_payments = r.message.mode_of_payments;
                        var total_sales_invoice_amount = r.message.total_sales_invoice_amount;
                        var total_payment_entry_amount = r.message.total_payment_entry_amount;
                        var total_received_amount = r.message.total_received_amount;

                        if ((invoices || payments) && mode_of_payments && (total_sales_invoice_amount)) {
                            frm.doc.total_sales_invoice_amount = total_sales_invoice_amount;
                            frm.doc.total_payment_entry_amount = total_payment_entry_amount;
                            frm.doc.total_received_amount = total_received_amount;

                            frm.set_value("sales_invoice_reference", []);
                            frm.set_value("payment_entry_reference", []);
                            frm.set_value("mode_of_payment", []);

                            // $.each(invoices, function(i, d) {
                                $.each(invoices, function(i, d) {
                                    var row =  frm.add_child("sales_invoice_reference");
                                    row.sales_invoice = d.name;
                                    row.paid_amount = d.bank_receive_amount;
                                    row.mode_of_payments = d.inv_mops
                                    // row.mode_of_payment = d.mode_of_payment
                                });
                            
                            // $.each(invoices, function(i, d) {
                            $.each(invoices, function(i, d) {
                                var row =  frm.add_child("mode_of_payment");
                                // var mop_row =  frm.add_child("mode_of_payment");
                                row.sales_invoice = d.name;
                                row.paid = d.bank_receive_amount;
                                // row.mode_of_payments = d.inv_mops;
                                // mop_row.mode_of_payment = mop
                            });

                            // $.each(payments, function(i, d) {
                            //     var row =  frm.add_child("payment_entry_reference");
                            //     row.payment_entry = d.name;
                            //     row.paid_amount = d.paid_amount;
                            //     row.mode_of_payment = d.mode_of_payment
                            // });

                            // $.each(mode_of_payments, function(mop, amt) {
                            //     var mop_row =  frm.add_child("mode_of_payment");
                            //     mop_row.mode_of_payment = mop;
                            //     mop_row.amount = amt;
                            // });


                            refresh_field("total_sales_invoice_amount");
                            refresh_field("total_payment_entry_amount");
                            refresh_field("total_received_amount");

                            refresh_field("sales_invoice_reference");
                            refresh_field("payment_entry_reference");
                            refresh_field("mode_of_payment");
                        }
                        else {
                            frappe.throw('No Invoices/Payments meeting criteria');
                        }
                    }
                }
            })
	    }
	    else {
	        frappe.throw('Invoice Date or POS Profile missing');
	    }
    }
});
