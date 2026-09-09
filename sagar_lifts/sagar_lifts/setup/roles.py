import frappe

SL_ROLES = [
	"SL Admin",
	"SL Management",
	"SL Collection Lead",
	"SL Billing",
	"SL Manufacturing",
	"SL Stores",
	"SL Dispatch",
	"SL Service Manager",
	"SL Technician",
]


def after_install():
	create_sl_roles()


def create_sl_roles():
	for role_name in SL_ROLES:
		if not frappe.db.exists("Role", role_name):
			frappe.get_doc({"doctype": "Role", "role_name": role_name}).insert(ignore_permissions=True)
