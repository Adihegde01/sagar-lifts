"""Sagar Lifts Sales Module — Lead Source setup (Section 4.2 of the guide).

The guide was written against an older ERPNext "Lead Source" doctype. This
v16 install replaced it with "UTM Source" (linked from Lead.utm_source),
and three of the guide's six sources already exist there under different
names:

    Guide name          -> Existing UTM Source
    -----------------------------------------
    Referral             -> Reference
    Cold Call             -> Cold Calling
    Walk-in                -> Walk In

Per team decision, those three are reused as-is rather than duplicated.
Only the three genuinely new sources are added here.
"""

NEW_SOURCES = [
	"Scouting",
	"Repeat Developer",
	"Online",
]


def setup_lead_sources():
	import frappe

	for source in NEW_SOURCES:
		if not frappe.db.exists("UTM Source", source):
			frappe.get_doc({"doctype": "UTM Source", "name": source}).insert(ignore_permissions=True)
