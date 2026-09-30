"""Maintenance Schedule — AMC schedule, one per deployment.

Same as Maintenance Visit (setup/maintenance_visit.py): every AMC schedule
is for one specific lift, so the Sales Order link is mandatory here too,
not optional like on Payment Entry.
"""

from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

CUSTOM_FIELDS = {
	"Maintenance Schedule": [
		{
			"fieldname": "job_id",
			"label": "Sales Order",
			"fieldtype": "Link",
			"options": "Sales Order",
			"reqd": 1,
			"in_standard_filter": 1,
			"description": "Links this AMC schedule to the specific deployment",
			"insert_after": "customer",
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


def setup_maintenance_schedule_customization():
	create_custom_fields(CUSTOM_FIELDS, ignore_validate=True)
