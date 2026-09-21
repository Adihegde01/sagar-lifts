"""Runtime doc_events for Sagar Lifts (wired in hooks.py)."""

import frappe
from frappe.utils import today


def sales_order_set_job_number(doc, method=None):
	# Default Job Number to the Sales Order's own name (JOB-.####.) but leave it
	# editable — only fill when blank. autoname has already run by validate.
	if not doc.job_number and doc.name:
		doc.job_number = doc.name


def purchase_invoice_set_manufacturing_approval(doc, method=None):
	# Stamp who/when approved a contractor bill the first time it's ticked.
	if doc.is_contractor_bill and doc.approved_by_manufacturing and not doc.manufacturing_approval_by:
		doc.manufacturing_approval_by = frappe.session.user
		doc.manufacturing_approval_date = today()
