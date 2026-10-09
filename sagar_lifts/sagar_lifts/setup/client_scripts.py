"""Client Scripts — form-level JS. Everything else in this app is no-code
config (Custom Fields, Property Setters, Workflows); a custom button is the
one thing that genuinely needs client-side script.
"""

import frappe

SALES_ORDER_VIEW_PROJECT_SCRIPT = """
frappe.ui.form.on("Sales Order", {
	refresh: function(frm) {
		if (frm.doc.project) {
			frm.add_custom_button(__("View Project"), function() {
				frappe.set_route("Form", "Project", frm.doc.project);
			});
		}
	},
});
"""

# CLs / the Accounts Caller can't edit a submitted invoice natively (needs
# Submit permission) — this dialog posts only their allowed fields to
# sagar_lifts.sagar_lifts.collection.log_collection_update.
SALES_INVOICE_LOG_COLLECTION_SCRIPT = """
frappe.ui.form.on("Sales Invoice", {
	refresh: async function(frm) {
		if (frm.doc.docstatus !== 1) return;
		const { message: fieldnames } = await frappe.call("sagar_lifts.sagar_lifts.collection.get_collection_fields");
		if (!fieldnames || !fieldnames.length) return;
		frm.add_custom_button(__("Log Collection Update"), () => {
			const fields = fieldnames.map((fieldname) => {
				const df = frappe.meta.get_docfield("Sales Invoice", fieldname, frm.doc.name);
				return { ...df, read_only: 0, reqd: 0, default: frm.doc[fieldname] };
			});
			const d = new frappe.ui.Dialog({
				title: __("Log Collection Update"),
				fields,
				primary_action_label: __("Save"),
				primary_action: async (values) => {
					await frappe.call({
						method: "sagar_lifts.sagar_lifts.collection.log_collection_update",
						args: { invoice: frm.doc.name, values },
						freeze: true,
					});
					d.hide();
					frm.reload_doc();
				},
			});
			d.show();
		});
	},
});
"""

CLIENT_SCRIPTS = [
	{
		"name": "Sales Order View Project Button",
		"dt": "Sales Order",
		"view": "Form",
		"script": SALES_ORDER_VIEW_PROJECT_SCRIPT,
	},
	{
		"name": "Sales Invoice Log Collection Update",
		"dt": "Sales Invoice",
		"view": "Form",
		"script": SALES_INVOICE_LOG_COLLECTION_SCRIPT,
	},
]


def setup_client_scripts():
	for cs in CLIENT_SCRIPTS:
		name = cs["name"]
		if frappe.db.exists("Client Script", name):
			doc = frappe.get_doc("Client Script", name)
		else:
			doc = frappe.new_doc("Client Script")
			doc.name = name
		doc.dt = cs["dt"]
		doc.view = cs["view"]
		doc.script = cs["script"]
		doc.enabled = 1
		doc.save(ignore_permissions=True)
