"""Runtime doc_events for Sagar Lifts (wired in hooks.py)."""

import frappe
from frappe import _
from frappe.utils import today

from sagar_lifts.sagar_lifts.amc_calendar import get_pm_month, get_quarter


def sales_order_set_job_number(doc, method=None):
	# Default Job Number to the Sales Order's own name (JOB-.####.) but leave it
	# editable — only fill when blank. autoname has already run by validate.
	if not doc.job_number and doc.name:
		doc.job_number = doc.name


def sales_order_validate_contract_value(doc, method=None):
	# "Contract Value" (No-Code Guide 9.1) is the order's own grand total —
	# no separate field, so it can never drift from the actual line items.
	# Required + non-zero, same as any other mandatory field.
	if not doc.grand_total:
		frappe.throw(_("Contract Value (the order total) cannot be zero"))


def maintenance_visit_set_quarter(doc, method=None):
	# Quarter/PM Month default from the visit date (Indian FY: Apr-Mar) but stay editable.
	if not doc.mntc_date:
		return
	if not doc.quarter:
		doc.quarter = get_quarter(doc.mntc_date)
	if not doc.pm_month:
		doc.pm_month = get_pm_month(doc.mntc_date)


def purchase_invoice_set_manufacturing_approval(doc, method=None):
	# Stamp who/when approved a contractor bill the first time it's ticked.
	is_contractor_bill = doc.bill_type == "Contractor"
	if is_contractor_bill and doc.approved_by_manufacturing and not doc.manufacturing_approval_by:
		doc.manufacturing_approval_by = frappe.session.user
		doc.manufacturing_approval_date = today()
