// The person raising an invoice sees every payment milestone of the job, with
// what is already invoiced against each; this invoice's own milestone is highlighted.
frappe.ui.form.on("Sales Invoice", {
	refresh(frm) {
		if (!frm.doc.job_id) return;
		frappe
			.call("sagar_lifts.sagar_lifts.milestone_billing.milestone_summary", {
				sales_order: frm.doc.job_id,
				current: frm.doc.milestone_number,
			})
			.then(({ message }) => {
				if (message) frm.dashboard.add_section(message, __("Payment Milestones — {0}", [frm.doc.job_id]));
			});
	},
	job_id(frm) {
		frm.refresh();
	},
});
