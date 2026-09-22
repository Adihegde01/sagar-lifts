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

CLIENT_SCRIPTS = [
	{
		"name": "Sales Order View Project Button",
		"dt": "Sales Order",
		"view": "Form",
		"script": SALES_ORDER_VIEW_PROJECT_SCRIPT,
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
