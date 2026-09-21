"""Scheduled tasks for Sagar Lifts (wired in hooks.py scheduler_events)."""

import frappe
from frappe.utils import getdate

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
