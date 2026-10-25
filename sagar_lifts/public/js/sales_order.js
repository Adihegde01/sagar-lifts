// Billing raises each payment milestone (Advance, On Delivery, Handover...)
// as a Proforma Invoice cut to that milestone's share of the order, instead
// of ERPNext's "bill the whole order" Create -> Sales Invoice.
frappe.ui.form.on("Sales Order", {
	refresh(frm) {
		if (frm.doc.docstatus !== 1 || !frappe.model.can_create("Sales Invoice")) return;

		for (const i of [1, 2, 3, 4, 5]) {
			const name = frm.doc[`milestone_${i}_name`];
			const pct = frm.doc[`milestone_${i}_percent`];
			if (!name || !pct) continue;
			frm.add_custom_button(
				`${name} — ${pct}%`,
				() =>
					frappe
						.call("sagar_lifts.sagar_lifts.milestone_billing.make_milestone_invoice", {
							sales_order: frm.doc.name,
							milestone: i,
						})
						.then(({ message }) => {
							if (!message) return;
							frappe.model.sync(message);
							frappe.set_route("Form", "Sales Invoice", message.name);
						}),
				__("Proforma Invoice")
			);
		}
	},
});
