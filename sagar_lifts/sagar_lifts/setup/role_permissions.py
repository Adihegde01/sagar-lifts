"""Role Permissions Manager grids — transcribed from the No-Code Guide,
Section 4/5, for the four core doctypes: Sales Order, Delivery Note, Sales
Invoice, Maintenance Visit.

Cells left out of a role's dict are "No" (absent Custom DocPerm = no access,
same as an all-zero row, so a zeroed row is never added just to say "No").

"Own accounts only" (SL Collection Lead) is a per-user User Permission on
Customer, not built here — assigning each Collection Lead's own developer
accounts needs real user/customer data (Phase 1).

"Own only" (SL Technician, Maintenance Visit) IS built here, as if_owner=1 —
a technician's assigned visits are the ones they create from the mobile app,
so doc ownership is the right native restriction.

Sales Order also gets a permlevel=1 row for SL Admin/SL Management — the
override-field permission level (Dispatch Override Approved etc.) needs at
least one role granted that level or the field is uneditable/hidden to
everyone, Admin included.
"""

import frappe
from frappe.permissions import setup_custom_perms

CORE_DOCTYPE_GRID = {
	"Sales Order": {
		"SL Admin": dict(read=1, write=1, create=1, delete=1, submit=1, cancel=1),
		"SL Management": dict(read=1, write=1),
		"SL Collection Lead": dict(read=1),
		"SL Billing": dict(read=1, write=1, create=1, submit=1),
		"SL Manufacturing": dict(read=1, write=1, create=1, submit=1),
		"SL Stores": dict(read=1),
		# write=1 and submit=1 are required here even though the guide's own
		# grid prints Edit=No/Submit=No: SL Dispatch is the sole allowed role
		# on 2 workflow transitions (Mark Dispatched, Signed Challan
		# Received). Completing a transition on an already-submitted order
		# calls doc.save(), which Frappe treats as "update_after_submit" and
		# checks the Submit permission (not just Write) regardless of the
		# workflow's own "allow_edit"/transition "allowed" roles. Without
		# this, SL Dispatch can never move the order out of Active at all —
		# confirmed by live-testing the workflow end to end.
		"SL Dispatch": dict(read=1, write=1, submit=1),
		"SL Service Manager": dict(read=1),
	},
	"Delivery Note": {
		"SL Admin": dict(read=1, write=1, create=1, delete=1, submit=1, cancel=1),
		# Not in the guide's own grid (Section 5 flags this) — added Read-only
		# to match Management's read-only pattern everywhere else.
		"SL Management": dict(read=1),
		"SL Billing": dict(read=1),
		"SL Manufacturing": dict(read=1),
		"SL Stores": dict(read=1, write=1, create=1),
		"SL Dispatch": dict(read=1, write=1, create=1, submit=1),
		"SL Service Manager": dict(read=1),
	},
	"Sales Invoice": {
		"SL Admin": dict(read=1, write=1, create=1, delete=1, submit=1, cancel=1),
		"SL Management": dict(read=1),
		"SL Billing": dict(read=1, write=1, create=1, submit=1),
		"SL Collection Lead": dict(read=1),
		"SL Manufacturing": dict(read=1),
	},
	"Maintenance Visit": {
		"SL Admin": dict(read=1, write=1, create=1, delete=1, submit=1, cancel=1),
		"SL Management": dict(read=1),
		"SL Service Manager": dict(read=1, write=1, create=1, submit=1),
		"SL Technician": dict(read=1, write=1, create=1, submit=1, if_owner=1),
		"SL Billing": dict(read=1),
		"SL Manufacturing": dict(read=1),
		"SL Collection Lead": dict(read=1),
	},
}

PERMLEVEL_1_GRID = {
	"Sales Order": {
		"SL Admin": dict(read=1, write=1),
		"SL Management": dict(read=1, write=1),
	},
}

_PERM_FIELDS = ("read", "write", "create", "delete", "submit", "cancel", "if_owner")


def _upsert(doctype, role, permlevel, values):
	setup_custom_perms(doctype)
	name = frappe.db.get_value(
		"Custom DocPerm", {"parent": doctype, "role": role, "permlevel": permlevel}
	)
	doc = frappe.get_doc("Custom DocPerm", name) if name else frappe.new_doc("Custom DocPerm")
	doc.parent = doctype
	doc.parenttype = "DocType"
	doc.parentfield = "permissions"
	doc.role = role
	doc.permlevel = permlevel
	for field in _PERM_FIELDS:
		doc.set(field, values.get(field, 0))
	doc.save(ignore_permissions=True)


def setup_role_permissions():
	for doctype, roles in CORE_DOCTYPE_GRID.items():
		for role, values in roles.items():
			_upsert(doctype, role, 0, values)

	for doctype, roles in PERMLEVEL_1_GRID.items():
		for role, values in roles.items():
			_upsert(doctype, role, 1, values)
