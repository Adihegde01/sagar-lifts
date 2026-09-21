"""Sales Invoice — Proforma & Tax Invoice.

PI Type and the Sales Order link aren't in the guide's Section 5 table but
Steps 28-29 depend on them (Section 5, Open Items) — every PI/TI must link
back to a Sales Order.
"""

from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

CUSTOM_FIELDS = {
	"Sales Invoice": [
		{
			"fieldname": "pi_type",
			"label": "PI Type",
			"fieldtype": "Select",
			"options": "Proforma Invoice\nTax Invoice",
			"reqd": 1,
			"description": "Decides which Naming Series applies",
			"insert_after": "customer_name",
		},
		{
			"fieldname": "job_id",
			"label": "Sales Order",
			"fieldtype": "Link",
			"options": "Sales Order",
			"reqd": 1,
			"in_standard_filter": 1,
			"description": "Every PI/TI must be linked to a Sales Order",
			"insert_after": "pi_type",
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
		{
			"fieldname": "collection_lead",
			"label": "Collection Lead",
			"fieldtype": "Link",
			"options": "User",
			"fetch_from": "job_id.collection_lead",
			"read_only": 1,
			"insert_after": "job_name",
			"description": "Fetched from the Job — the escalation ladder routes reminders to this user",
		},
	]
}


def setup_sales_invoice_customization():
	create_custom_fields(CUSTOM_FIELDS, ignore_validate=True)
