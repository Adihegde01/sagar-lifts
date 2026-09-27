"""User accounts + SL role assignment — from Sagar_Lifts_User_Import sheet.

Welcome emails are deliberately suppressed (send_welcome_email=0) — the client
sends password-reset links to real @sagarlifts.com staff separately, not as
a side effect of running setup. Idempotent: skips a user that already exists,
just makes sure they hold their assigned role.

sales@ and marketing@ are SL Sales per the sheet's correction note (the
sheet's own "Assign Role" reference column still shows their old SL
Technician / SL Service Manager placeholder — superseded here).
"""

import frappe

USERS = [
	("accounts@sagarlifts.com", "Pinky", "SL Billing"),
	("administration@sagarlifts.com", "Admin", "SL Management"),
	("collection@sagarlifts.com", "Collection", "SL Collection Lead"),
	("finance@sagarlifts.com", "Aarti", "SL Billing"),
	("info@sagarlifts.com", "Info", "SL Management"),
	("maintenance@sagarlifts.com", "Snehal", "SL Service Manager"),
	("marketing@sagarlifts.com", "Marketing", "SL Sales"),
	("nidhi@sagarlifts.com", "nidhi", "SL Admin"),
	("praharsh@sagarlifts.com", "Praharsh", "SL Admin"),
	("pune@sagarlifts.com", "pune HO", "SL Manufacturing"),
	("purchase@sagarlifts.com", "Arti", "SL Stores"),
	("rakesh@sagarlifts.com", "Rakesh", "SL Manufacturing"),
	("sales@sagarlifts.com", "Sales", "SL Sales"),
	("service@sagarlifts.com", "ranjana", "SL Service Manager"),
	("stock@sagarlifts.com", "Sanoj", "SL Dispatch"),
	("vaishali@sagarlifts.com", "Vaishali", "SL Billing"),
	("vtrajani@sagarlifts.com", "VT Rajani", "SL Admin"),
	("himanshu@sagarlifts.com", "himanshu", "SL Management"),
]


def setup_users():
	for email, first_name, role in USERS:
		if frappe.db.exists("User", email):
			user = frappe.get_doc("User", email)
		else:
			user = frappe.get_doc(
				{
					"doctype": "User",
					"email": email,
					"first_name": first_name,
					"send_welcome_email": 0,
				}
			)
			user.insert(ignore_permissions=True)
		if not any(r.role == role for r in user.roles):
			user.append("roles", {"role": role})
			user.save(ignore_permissions=True)
