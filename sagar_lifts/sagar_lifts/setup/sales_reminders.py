"""Weekly sales-cadence reminders (Sales Module Guide, Section 6.6, #22-24).

"Every Monday"/"Every Friday" triggers have no document to hang a Frappe
Notification off of, so they're sent as scheduler cron jobs instead (wired
in hooks.scheduler_events), following the same bell-plus-email pattern
already used for collection review reminders (collection.py).
"""

import frappe
from frappe.desk.doctype.notification_log.notification_log import enqueue_create_notification
from frappe.utils.user import get_users_with_role

MONDAY_REMINDERS = [
	(
		"Weekly Scout Report Submission Due",
		"Please submit this week's SL Scout Report(s) before end of day.",
		"SL Sales",
	),
	(
		"Weekly Caller Log Review Due",
		"Please review this week's Lead follow-up logs and caller remarks.",
		"SL Admin",
	),
]

FRIDAY_REMINDERS = [
	(
		"Weekly Sales Review Due",
		"Please review this week's sales activity — caller logs, meetings held, and pipeline status.",
		"SL Admin",
	),
]


def _send_reminders(items):
	can_email = frappe.db.exists("Email Account", {"default_outgoing": 1, "enable_outgoing": 1})
	for subject, message, role in items:
		users = get_users_with_role(role)
		if not users:
			continue
		enqueue_create_notification(
			users, {"type": "Alert", "subject": subject, "email_content": message, "document_type": "Lead"}
		)
		if can_email:
			frappe.sendmail(recipients=users, subject=subject, message=message)


def send_monday_sales_reminders():
	_send_reminders(MONDAY_REMINDERS)


def send_friday_sales_reminders():
	_send_reminders(FRIDAY_REMINDERS)
