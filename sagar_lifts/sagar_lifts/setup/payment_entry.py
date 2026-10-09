"""Payment Entry — optional Job traceability.

Not every payment is job-linked (routine supplier payments, expenses, salary,
etc.), so unlike Purchase Order/Purchase Invoice this is a plain optional
field — Payment Entry has no Bill Type of its own to gate it behind.
"""

from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

CUSTOM_FIELDS = {
	"Payment Entry": [
		{
			"fieldname": "job_id",
			"label": "Job ID",
			"fieldtype": "Link",
			"options": "Sales Order",
			"in_standard_filter": 1,
			"description": "The deployment this payment is for — leave blank for payments not tied to a specific job",
			"insert_after": "party_name",
		},
		{
			"fieldname": "job_number",
			"label": "Job Number",
			"fieldtype": "Data",
			"fetch_from": "job_id.job_number",
			"read_only": 1,
			"insert_after": "job_id",
		},
		{
			"fieldname": "job_name",
			"label": "Job Name",
			"fieldtype": "Data",
			"fetch_from": "job_id.job_name",
			"read_only": 1,
			"insert_after": "job_number",
		},
	]
}


def setup_payment_entry_customization():
	create_custom_fields(CUSTOM_FIELDS, ignore_validate=True)
