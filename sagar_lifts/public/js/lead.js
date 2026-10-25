// Callers work a lead and ask for a quotation; they never create the
// Customer/Opportunity/Quotation/Prospect that ERPNext's Create menu offers
// (Sales Admin and the Senior team do). Hide those for a caller and give them
// the one action that is theirs: a Quotation Request.
const SL_LEAD_CALLER_HIDE = ["Customer", "Opportunity", "Quotation", "Prospect"];
const SL_LEAD_PRIVILEGED = ["SL Admin", "SL Sales Admin", "SL Sales Senior", "SL Sales Supervisor", "System Manager"];

frappe.ui.form.on("Lead", {
	refresh(frm) {
		if (frm.is_new()) return;

		if (frappe.model.can_create("SL Quotation Request")) {
			frm.add_custom_button(
				__("Quotation Request"),
				() => frappe.new_doc("SL Quotation Request", { lead_reference: frm.doc.name }),
				__("Create")
			);
		}

		const isCallerOnly =
			frappe.user.has_role("SL Caller") && !SL_LEAD_PRIVILEGED.some((r) => frappe.user.has_role(r));
		if (isCallerOnly) {
			// Frappe's own Lead script adds these on refresh too — remove after it has run.
			setTimeout(() => SL_LEAD_CALLER_HIDE.forEach((b) => frm.remove_custom_button(__(b), __("Create"))), 0);
		}
	},
});
