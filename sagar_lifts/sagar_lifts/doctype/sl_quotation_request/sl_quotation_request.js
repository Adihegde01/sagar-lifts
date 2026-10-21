// Copyright (c) 2026, Sagar Lifts and contributors
// For license information, please see license.txt

frappe.ui.form.on("SL Quotation Request", {
	onload(frm) {
		if (frm.is_new()) {
			if (!frm.doc.requested_by) frm.set_value("requested_by", frappe.session.user);
			if (!frm.doc.request_date) frm.set_value("request_date", frappe.datetime.get_today());
		}
	},
	refresh(frm) {
		// Sales guide 7.3: Sales Admin answers a submitted request with the actual Quotation.
		if (frm.doc.docstatus === 1 && !frm.doc.quotation_generated && frappe.model.can_create("Quotation")) {
			frm.add_custom_button(__("Quotation"), () => {
				frappe.new_doc("Quotation", {
					quotation_to: frm.doc.lead_reference ? "Lead" : "Customer",
					party_name: frm.doc.lead_reference,
					quotation_request: frm.doc.name,
				});
			}, __("Create"));
		}
	},
	lead_reference(frm) {
		if (!frm.doc.lead_reference) return;
		frappe
			.call(
				"sagar_lifts.sagar_lifts.doctype.sl_quotation_request.sl_quotation_request.get_lead_values",
				{ lead: frm.doc.lead_reference }
			)
			.then(({ message }) => {
				// only fill what the user hasn't typed yet
				for (const [field, value] of Object.entries(message || {})) {
					if (!frm.doc[field]) frm.set_value(field, value);
				}
			});
	},
});
