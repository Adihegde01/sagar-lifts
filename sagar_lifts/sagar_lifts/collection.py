"""Collection follow-up on Sales Invoices.

Collection Leads and the Accounts Caller only have Read on Sales Invoice, and
Frappe requires Submit permission to edit any submitted document — so they
log structured follow-up through log_collection_update instead, which lets
each role change only its own Collection-tab fields. The narrative of each
call/visit goes in the invoice's Comment timeline (Read is enough for that).
"""

import frappe
from frappe import _
from frappe.desk.doctype.notification_log.notification_log import enqueue_create_notification
from frappe.utils.user import get_users_with_role

COMMITMENT_FIELDS = [
	"payment_commitment_received",
	"payment_committed_amount",
	"payment_committed_date",
	"commitment_given_by",
	"commitment_fulfilled",
]
EDITABLE_BY_ROLE = {
	"SL Accounts Caller": [
		"last_accounts_call_date",
		"last_accounts_contact_type",
		*COMMITMENT_FIELDS,
		"next_follow_up_date",
	],
	"SL Collection Lead": [
		"last_cl_contact_date",
		"last_cl_contact_type",
		*COMMITMENT_FIELDS,
		"collection_status",
		"next_follow_up_date",
		"next_follow_up_by",
		"collection_notes",
	],
}


@frappe.whitelist()
def get_collection_fields():
	"""Collection-tab fields the current user may log, in form order."""
	roles = set(frappe.get_roles())
	allowed = {f for role, fields in EDITABLE_BY_ROLE.items() if role in roles for f in fields}
	return [df.fieldname for df in frappe.get_meta("Sales Invoice").fields if df.fieldname in allowed]


@frappe.whitelist(methods=["POST"])
def log_collection_update(invoice, values):
	values = frappe.parse_json(values) or {}
	doc = frappe.get_doc("Sales Invoice", invoice)
	doc.check_permission("read")  # also honours the CL's own-developer User Permission
	if doc.docstatus != 1:
		frappe.throw(_("Collection updates are logged on submitted invoices only"))
	not_allowed = set(values) - set(get_collection_fields())
	if not values or not_allowed:
		frappe.throw(_("You can't update: {0}").format(", ".join(sorted(not_allowed)) or "-"), frappe.PermissionError)
	doc.update(values)
	doc.flags.ignore_permissions = True  # the role/field check above is the gate
	doc.save()
	return doc.name


WEEKLY_REVIEWS = [
	(
		"Weekly CL Activity Review Due",
		"Please review Collection Lead activity logs for last week. Go to Sales Invoice list "
		"filtered by each CL to see their interaction comments.",
	),
	(
		"Weekly Accounts Caller Review Due",
		"Please review Accounts Caller activity logs for last week. Go to Sales Invoice list "
		"filtered by Accounts Caller to see all call and email logs.",
	),
]


def send_weekly_review_reminders():
	"""Monday reminders to SL Admin (wired as a cron in hooks.scheduler_events)."""
	admins = get_users_with_role("SL Admin")
	if not admins:
		return
	# Bell notification always; email only once an outgoing Email Account is set
	# up — without one sendmail raises and would sink the bell alert with it.
	can_email = frappe.db.exists("Email Account", {"default_outgoing": 1, "enable_outgoing": 1})
	for subject, message in WEEKLY_REVIEWS:
		enqueue_create_notification(
			admins, {"type": "Alert", "subject": subject, "email_content": message, "document_type": "Sales Invoice"}
		)
		if can_email:
			frappe.sendmail(recipients=admins, subject=subject, message=message)
