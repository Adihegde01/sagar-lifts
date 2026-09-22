"""Scheduled tasks for Sagar Lifts (wired in hooks.py scheduler_events)."""

import frappe
from frappe.utils import get_first_day, getdate

from sagar_lifts.sagar_lifts.amc_calendar import get_last_completed_quarter, get_quarter_start


def flag_overdue_amc_billing():
	"""Tick Outstanding Flag on any AMC Sales Order whose last completed
	quarter's PM PI (a Proforma Invoice) wasn't raised by the deadline.

	Only sets the flag — never clears it, so a manually-ticked flag for some
	other reason is never silently undone by this job.
	"""
	today = getdate()
	quarter, quarter_end, deadline = get_last_completed_quarter(today)
	if today <= deadline:
		return

	quarter_start = get_quarter_start(quarter_end)

	amc_orders = frappe.get_all(
		"Sales Order",
		filters={"deployment_status": "AMC", "outstanding_flag": 0},
		pluck="name",
	)
	for job_id in amc_orders:
		billed = frappe.db.exists(
			"Sales Invoice",
			{
				"job_id": job_id,
				"pi_type": "Proforma Invoice",
				"docstatus": ["!=", 2],
				"posting_date": ["between", [quarter_start, quarter_end]],
			},
		)
		if not billed:
			frappe.db.set_value("Sales Order", job_id, "outstanding_flag", 1)


def flag_overdue_pm_visits():
	"""Tick PM Visit Overdue on any Handed Over/AMC order with no Preventive
	Maintenance visit logged this month, once the 25th has passed.

	Unlike flag_overdue_amc_billing, this one also clears the flag once a
	visit is logged — "no PM this month" is the field's whole meaning, so
	nothing else could have set it for an unrelated reason.

	# ponytail: checks "a visit this calendar month", not "a visit for the
	# specific month that went overdue" — once flagged it stays flagged
	# until any new visit is logged, matching the guide's "doesn't auto-close"
	# intent closely enough without tracking which month was missed.
	"""
	if getdate().day < 25:
		return

	month_start = get_first_day(getdate())
	under_maintenance = frappe.get_all(
		"Sales Order",
		filters={"deployment_status": ["in", ("Handed Over", "AMC")]},
		fields=["name", "pm_visit_overdue"],
	)
	for so in under_maintenance:
		visited = frappe.db.exists(
			"Maintenance Visit",
			{
				"job_id": so.name,
				"visit_type": "Preventive Maintenance",
				"docstatus": 1,
				"mntc_date": [">=", month_start],
			},
		)
		if visited and so.pm_visit_overdue:
			frappe.db.set_value("Sales Order", so.name, "pm_visit_overdue", 0)
		elif not visited and not so.pm_visit_overdue:
			frappe.db.set_value("Sales Order", so.name, "pm_visit_overdue", 1)
