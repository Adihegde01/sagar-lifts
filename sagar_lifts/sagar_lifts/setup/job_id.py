"""Job ID — the deployment's lifelong identifier.

The originating Sales Order's name (JOB-.####.) is stamped on every downstream
document so the whole lifecycle — delivery, billing, service, AMC — can be
traced back to one job.
"""

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def _job_id_field(insert_after, reqd=0):
	return {
		"fieldname": "job_id",
		"label": "Job ID",
		"fieldtype": "Link",
		"options": "Sales Order",
		"reqd": reqd,
		"insert_after": insert_after,
		"in_standard_filter": 1,
		"description": "The deployment's lifelong identifier — its originating Sales Order (Job Number)",
	}


def _job_number_field(insert_after="job_id"):
	return {
		"fieldname": "job_number",
		"label": "Job Number",
		"fieldtype": "Data",
		"fetch_from": "job_id.job_number",
		"read_only": 1,
		"insert_after": insert_after,
	}


def _job_name_field(insert_after="job_id"):
	return {
		"fieldname": "job_name",
		"label": "Job Name",
		"fieldtype": "Data",
		"fetch_from": "job_id.job_name",
		"read_only": 1,
		"insert_after": insert_after,
		"description": "Fetched from the Job — keeps the deployment identifiable end to end",
	}


CUSTOM_FIELDS = {
	"Delivery Note": [
		_job_id_field("customer_name", reqd=1),
		# No job_number here — Sales Order's own job_number defaults to the
		# order's own name (doc_events.sales_order_set_job_number), so it
		# duplicated Job ID's value verbatim. Dropped 2026-09-30.
		_job_name_field(insert_after="job_id"),
	],
	# Maintenance Visit, Purchase Invoice and Sales Invoice own their own
	# job_id/job_number/job_name — see setup/maintenance_visit.py,
	# setup/purchase_invoice.py and setup/sales_invoice.py
	"Contract": [_job_id_field("party_full_name")],
}


def setup_job_id_links():
	# Drop the now-redundant Job Number field this used to add to Delivery
	# Note — see the CUSTOM_FIELDS comment above.
	frappe.db.delete("Custom Field", {"dt": "Delivery Note", "fieldname": "job_number"})
	create_custom_fields(CUSTOM_FIELDS, ignore_validate=True)
	frappe.clear_cache(doctype="Delivery Note")
