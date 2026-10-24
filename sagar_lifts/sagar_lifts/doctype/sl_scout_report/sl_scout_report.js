// Copyright (c) 2026, Sagar Lifts and contributors
// For license information, please see license.txt

// Same roles the controller's validate() lets pick another scouter.
const CAN_PICK_SCOUTER = ["SL Admin", "SL Sales Admin", "System Manager"];

frappe.ui.form.on("SL Scout Report", {
	setup(frm) {
		// only users who actually scout, never the whole user list
		const by_role = (role) => () => ({
			query: "sagar_lifts.sagar_lifts.sales_permissions.users_with_role",
			filters: { role },
		});
		frm.set_query("scouter_name", by_role("SL Scouter"));
		frm.set_query("assigned_to_caller", by_role("SL Caller"));
	},
	onload(frm) {
		const can_pick = CAN_PICK_SCOUTER.some((r) => frappe.user.has_role(r));
		if (frm.is_new() && (!frm.doc.scouter_name || !can_pick)) {
			frm.set_value("scouter_name", frappe.session.user);
		}
		if (!frm.doc.submission_date && frm.is_new()) {
			frm.set_value("submission_date", frappe.datetime.get_today());
		}
		// a scouter files reports as themselves only
		frm.set_df_property("scouter_name", "read_only", can_pick ? 0 : 1);
	},
});
