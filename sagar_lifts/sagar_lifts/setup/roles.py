import frappe

SL_ROLES = [
	"SL Admin",
	"SL Management",
	"SL Sales",
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

	# Mobile-only role (setup/maintenance_visit.py) — land straight on their own
	# chrome-free portal after login instead of an empty/irrelevant desk home
	# or the full desk list view. Role.home_page is a native field Frappe's
	# login redirect already checks (auth.py), so no custom JS/route needed.
	# See page/technician_portal for the page itself.
	frappe.db.set_value("Role", "SL Technician", "home_page", "app/technician-portal")
