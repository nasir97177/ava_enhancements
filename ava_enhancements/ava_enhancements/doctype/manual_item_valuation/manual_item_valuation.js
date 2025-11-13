frappe.ui.form.on('Manual Item Valuation', {
    refresh: function(frm) {
        frm.add_custom_button('Run Valuation', function() {
            if (!frm.doc.items || frm.doc.items.length === 0) {
                frappe.msgprint('Please add items to update.');
                return;
            }

            let items = frm.doc.items.map(d => ({
                item_code: d.item_code,
                valuation_rate: d.valuation_rate
            }));

            frappe.call({
                method: 'ava_enhancements.ava_enhancements.doctype.manual_item_valuation.manual_item_valuation.manual_item_valuation',
                args: {
                    items: JSON.stringify(items),
                    from_date: frm.doc.from_date,
                    to_date: frm.doc.to_date
                },
                callback: function(r) {
                    if (r.message) {
                        frappe.msgprint('Item Valuation, Stock, and GL Entries Updated Successfully!');
                        frm.reload_doc();
                    }
                }
            });
        });
    }
});

