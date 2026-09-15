"""Job ID — the deployment's lifelong identifier.

The originating Sales Order's name (JOB-.####.) is stamped on every downstream
document so the whole lifecycle — delivery, billing, service, AMC — can be
traced back to one job.
"""

from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def _job_id_field(insert_after):
	return {
		"fieldname": "job_id",
		"label": "Job ID",
		"fieldtype": "Link",
		"options": "Sales Order",
		"insert_after": insert_after,
		"in_standard_filter": 1,
		"description": "The deployment's lifelong identifier — its originating Sales Order (Job Number)",
	}


def _job_name_field():
	return {
		"fieldname": "job_name",
		"label": "Job Name",
		"fieldtype": "Data",
		"fetch_from": "job_id.job_name",
		"read_only": 1,
		"insert_after": "job_id",
		"description": "Fetched from the Job — keeps the deployment identifiable end to end",
	}


CUSTOM_FIELDS = {
	"Delivery Note": [_job_id_field("customer_name"), _job_name_field()],
	"Sales Invoice": [_job_id_field("customer_name"), _job_name_field()],
	# Maintenance Visit owns its own job_id/job_number/job_name — see setup/maintenance_visit.py
	"Contract": [_job_id_field("party_full_name")],
	# Purchase Invoice: Job ID only on a contractor bill, never a routine supplier bill.
	"Purchase Invoice": [
		{
			"fieldname": "is_contractor_bill",
			"label": "Contractor Bill",
			"fieldtype": "Check",
			"insert_after": "supplier_name",
			"description": "Tick for a contractor bill against a job — not for routine supplier bills",
		},
		{
			**_job_id_field("is_contractor_bill"),
			"depends_on": "eval:doc.is_contractor_bill",
			"mandatory_depends_on": "eval:doc.is_contractor_bill",
		},
		{
			**_job_name_field(),
			"depends_on": "eval:doc.is_contractor_bill",
		},
	],
}


def setup_job_id_links():
	create_custom_fields(CUSTOM_FIELDS, ignore_validate=True)
