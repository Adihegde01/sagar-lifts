// Billing raises each payment milestone (Advance, On Delivery, Handover...)
// as a Proforma Invoice cut to that milestone's share of the order, instead
// of ERPNext's "bill the whole order" Create -> Sales Invoice.
const SL_CONFIRM_ROLES = ["SL Sales Admin", "SL Billing", "SL Manufacturing", "SL Admin", "System Manager"];

frappe.ui.form.on("Sales Order", {
	refresh(frm) {
		// A saved draft order has no Submit on screen (workflow quirk), so give
		// the teams that confirm orders one. Once the Draft state is in place
		// the workflow's own "Confirm Order" button takes over and this hides.
		if (
			frm.doc.docstatus === 0 &&
			!frm.is_new() &&
			frm.doc.deployment_status !== "Draft" &&
			SL_CONFIRM_ROLES.some((r) => frappe.user.has_role(r))
		) {
			frm.add_custom_button(__("Confirm Order"), () => {
				if (frm.is_dirty()) return frappe.msgprint(__("Save the order first, then confirm it."));
				frappe.confirm(__("Submit {0} and start the job?", [frm.doc.name]), () =>
					frappe
						.call("sagar_lifts.sagar_lifts.milestone_billing.confirm_order", { sales_order: frm.doc.name })
						.then(() => frm.reload_doc())
				);
			}).addClass("btn-primary");
		}

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
