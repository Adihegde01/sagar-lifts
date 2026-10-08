"""Role Profiles — bundle a role set so new field users get assigned
consistently (User.role_profile_name applies every role in the bundle).
"""

import frappe

ROLE_PROFILES = {
	"SL Technician": ["SL Technician"],
}


def setup_role_profiles():
	for profile_name, roles in ROLE_PROFILES.items():
		if frappe.db.exists("Role Profile", profile_name):
			continue
		frappe.get_doc(
			{
				"doctype": "Role Profile",
				"role_profile": profile_name,
				"roles": [{"role": role} for role in roles],
			}
		).insert(ignore_permissions=True)
