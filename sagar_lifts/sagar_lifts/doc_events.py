"""Runtime doc_events for Sagar Lifts (wired in hooks.py)."""

from sagar_lifts.sagar_lifts.amc_calendar import get_pm_month, get_quarter


def sales_order_set_job_number(doc, method=None):
	# Default Job Number to the Sales Order's own name (JOB-.####.) but leave it
	# editable — only fill when blank. autoname has already run by validate.
	if not doc.job_number and doc.name:
		doc.job_number = doc.name


def maintenance_visit_set_quarter(doc, method=None):
	# Quarter/PM Month default from the visit date (Indian FY: Apr-Mar) but stay editable.
	if not doc.mntc_date:
		return
	if not doc.quarter:
		doc.quarter = get_quarter(doc.mntc_date)
	if not doc.pm_month:
		doc.pm_month = get_pm_month(doc.mntc_date)
